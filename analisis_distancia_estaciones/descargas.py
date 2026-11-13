"""Descarga Open-Meteo (best match + ERA5-Land), ERA5-Land lluvia (Copernicus CDS) y NASA POWER
para cada estación / pluviómetro de INUMET (y opcionalmente para las ubicaciones de las muestras).

Todas las series quedan en hora local (UTC-3) en cache/grillas/. Uso: python descargas.py [--muestras]
"""
import json
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd

import datos

GRILLAS = datos.CACHE / "grillas"
GRILLAS.mkdir(exist_ok=True)
RANGOS = [("2017-01-01", "2019-12-31"), ("2024-01-01", "2025-12-31")]
ANIOS = [2017, 2018, 2019, 2024, 2025]
OM_URL = "https://archive-api.open-meteo.com/v1/archive"
NASA_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"


def puntos(incluir_muestras=False):
    meta, tx, _, _ = datos.series_convencionales()
    mp, _ = datos.pluviometros()
    conv = meta[meta.nombre.isin(tx.columns)].assign(tipo="conv")
    p = [conv[["lat", "lon", "tipo"]], mp[["lat", "lon"]].assign(tipo="pluvio")]
    if incluir_muestras:
        p.append(datos.muestras()[["lat", "lon"]].assign(tipo="muestra"))
    p = pd.concat(p)
    p["key"] = p.lat.round(3).astype(str) + "_" + p.lon.round(3).astype(str)
    # si un punto es estación convencional en algún caso, se descargan todas las variables
    p["completo"] = p.tipo.isin(["conv", "muestra"])
    return p.groupby("key").agg(lat=("lat", "first"), lon=("lon", "first"), completo=("completo", "max")).reset_index()


def _get_json(url, intentos=6):
    for k in range(intentos):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            espera = 30 * (k + 1) if "429" in str(e) else 5 * (k + 1)
            print("  reintento", k + 1, e, flush=True)
            time.sleep(espera)
    raise RuntimeError(url)


def open_meteo(p):
    destino = GRILLAS / f"om_{p.key}.pkl"
    if destino.exists():
        return
    variables = ["temperature_2m", "relative_humidity_2m", "precipitation"] if p.completo else ["precipitation"]
    modelos = "best_match,era5_land" if p.completo else "best_match"
    partes = []
    for ini, fin in RANGOS:
        q = urllib.parse.urlencode({"latitude": p.lat, "longitude": p.lon, "start_date": ini, "end_date": fin,
                                    "hourly": ",".join(variables), "models": modelos, "timezone": "America/Montevideo"})
        j = _get_json(f"{OM_URL}?{q}")
        h = pd.DataFrame(j["hourly"])
        h.index = pd.to_datetime(h.pop("time"))
        partes.append(h)
        time.sleep(2)
    # coordenadas de la celda ERA5-Land (Open-Meteo elige una celda de tierra)
    q = urllib.parse.urlencode({"latitude": p.lat, "longitude": p.lon, "start_date": "2018-01-01",
                                "end_date": "2018-01-01", "hourly": "temperature_2m", "models": "era5_land"})
    j = _get_json(f"{OM_URL}?{q}")
    h = pd.concat(partes)
    h.columns = [c.replace("_archive_best_match", "_om").replace("_era5_land", "_e5l") for c in h.columns]
    if not p.completo:
        h.columns = [c if c.endswith(("_om", "_e5l")) else c + "_om" for c in h.columns]
    pd.to_pickle({"serie": h, "e5l_lat": j["latitude"], "e5l_lon": j["longitude"]}, destino)
    print("OM ok", p.key, flush=True)


def era5_land_lluvia(lat, lon):
    import cdsapi

    clave = f"{round(lat, 2)}_{round(lon, 2)}"
    destino = GRILLAS / f"e5lpp_{clave}.pkl"
    if destino.exists():
        return
    zp = GRILLAS / f"tmp_{clave}.zip"
    for k in range(5):
        try:
            cdsapi.Client(quiet=True, progress=False).retrieve(
                "reanalysis-era5-land-timeseries",
                {"variable": ["total_precipitation"], "location": {"latitude": lat, "longitude": lon},
                 "date": ["2017-01-01/2025-12-31"], "data_format": "csv"}, str(zp))
            break
        except Exception as e:  # noqa: BLE001
            print("  CDS reintento", clave, k + 1, str(e).splitlines()[-1], flush=True)
            time.sleep(30 * (k + 1))
    with zipfile.ZipFile(zp) as z:
        d = pd.read_csv(z.open(z.namelist()[0]), parse_dates=["valid_time"])
    zp.unlink()
    s = d.set_index("valid_time").tp.clip(lower=0) * 1000
    s.index = s.index - pd.Timedelta(hours=3)
    pd.to_pickle(s.rename("precipitation_e5l"), destino)
    print("CDS ok", clave, int(s.notna().sum()), flush=True)


def nasa(p):
    destino = GRILLAS / f"nasa_{p.key}.pkl"
    if destino.exists():
        return
    partes = []
    for a in ANIOS:
        q = urllib.parse.urlencode({"parameters": "T2M,RH2M,PRECTOTCORR", "community": "AG", "latitude": p.lat,
                                    "longitude": p.lon, "start": f"{a}0101", "end": f"{a}1231",
                                    "format": "CSV", "time-standard": "UTC"})
        for k in range(6):
            try:
                with urllib.request.urlopen(f"{NASA_URL}?{q}", timeout=300) as r:
                    txt = r.read().decode()
                break
            except Exception as e:  # noqa: BLE001
                print("  NASA reintento", k + 1, e, flush=True)
                time.sleep(10 * (k + 1))
        lineas = txt.splitlines()
        i = [n for n, l in enumerate(lineas) if l.startswith("-END HEADER")][0]
        d = pd.read_csv(StringIO("\n".join(lineas[i + 1:]))).replace(-999, np.nan)
        d.index = pd.to_datetime(dict(year=d.YEAR, month=d.MO, day=d.DY, hour=d.HR)) - pd.Timedelta(hours=3)
        partes.append(d[["T2M", "RH2M", "PRECTOTCORR"]])
    h = pd.concat(partes)
    h.columns = ["temperature_2m_nasa", "relative_humidity_2m_nasa", "precipitation_nasa"]
    pd.to_pickle(h, destino)
    print("NASA ok", p.key, flush=True)


def main():
    P = puntos("--muestras" in sys.argv)
    print(len(P), "puntos", flush=True)
    ex_nasa = ThreadPoolExecutor(3)
    tareas_nasa = [ex_nasa.submit(nasa, r) for _, r in P.iterrows()]
    for _, r in P.iterrows():
        open_meteo(r)
    celdas = set()
    for _, r in P.iterrows():
        d = pd.read_pickle(GRILLAS / f"om_{r.key}.pkl")
        celdas.add((round(d["e5l_lat"], 2), round(d["e5l_lon"], 2)))
    print(len(celdas), "celdas ERA5-Land", flush=True)
    for c in sorted(celdas):  # el CDS rechaza pedidos en paralelo para este dataset
        era5_land_lluvia(*c)
    for t in tareas_nasa:
        t.result()
    ex_nasa.shutdown()
    print("FIN", flush=True)


if __name__ == "__main__":
    main()
