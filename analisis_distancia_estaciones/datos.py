"""Carga de estaciones INUMET, pluviómetros y muestras de maíz (mapa KMZ de la tesis)."""
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
CACHE = Path(__file__).resolve().parent / "cache"
CACHE.mkdir(exist_ok=True)
KMZ = BASE / "Mapa Tesis micología.kmz"
INUMET_XLSX = BASE / "1793295547972-CLIM-2026-0000193.xlsx"
PERIODOS = ["2017-2019", "2024-2025"]
ARCHIVOS_PP = ["Precipitación diaria.xlsx", "Precipitación diaria 2.xlsx", "Precipitación diaria 3.xlsx"]
KML_NS = "{http://www.opengis.net/kml/2.2}"


def distancia_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(a))


def _norm(s):
    return " ".join(str(s).replace("_", " ").split()).strip().lower()


# ----------------------------------------------------------------- KMZ
def leer_kmz():
    with zipfile.ZipFile(KMZ) as z:
        root = ET.fromstring(z.read("doc.kml"))
    filas = []
    for carpeta in root.iter(KML_NS + "Folder"):
        nombre_carpeta = carpeta.find(KML_NS + "name").text.strip()
        for pm in carpeta.findall(KML_NS + "Placemark"):
            lon, lat = [float(x) for x in pm.find(f".//{KML_NS}coordinates").text.strip().split(",")[:2]]
            datos = {d.get("name"): getattr(d.find(KML_NS + "value"), "text", None) for d in pm.iter(KML_NS + "Data")}
            filas.append({"carpeta": nombre_carpeta, "nombre": pm.find(KML_NS + "name").text.strip(),
                          "lat": lat, "lon": lon, **datos})
    return pd.DataFrame(filas)


def muestras():
    k = leer_kmz()
    m = k[k.carpeta.str.startswith("Muestras")].copy()
    m["anio"] = m.carpeta.str[-4:].astype(int)
    m["fecha"] = pd.to_datetime(m["Fecha"], dayfirst=True, errors="coerce")
    return m[["nombre", "anio", "fecha", "lat", "lon", "Ubicación", "Departamento / Estado",
              "FB1(ppm)", "%PI Fusarium Total"]].reset_index(drop=True)


# ----------------------------------------------------------------- estaciones convencionales
def estaciones_convencionales():
    k = leer_kmz()
    e = k[k.carpeta.str.startswith("Estaciones Meter") & (k.Tipo == "Convencional")]
    return e[["nombre", "lat", "lon"]].reset_index(drop=True)


def series_convencionales():
    """TX y TN diarias (columnas = estación) y HR horaria (07-19 h)."""
    cache = CACHE / "convencionales.pkl"
    if cache.exists():
        return pd.read_pickle(cache)
    meta = estaciones_convencionales()
    por_nombre = {}
    for n in meta.nombre:  # "Rivera" (serie combinada) tiene prioridad sobre "Rivera - Aeropuerto"
        por_nombre.setdefault(_norm(n.split(" - ")[0]), n)
    wb = openpyxl.load_workbook(INUMET_XLSX, read_only=True, data_only=True)

    rows = list(wb["TxTn"].iter_rows(values_only=True))
    i = [k for k, r in enumerate(rows) if r and r[0] == "Fecha"][0]
    nombres = rows[i - 1]
    cuerpo = [r for r in rows[i + 1:] if r and r[0] is not None]
    fechas = pd.to_datetime([r[0] for r in cuerpo])
    tx, tn = {}, {}
    for c, v in enumerate(nombres):
        if v and _norm(v) in por_nombre:
            n = por_nombre[_norm(v)]
            tx[n] = pd.to_numeric(pd.Series([r[c] if len(r) > c else None for r in cuerpo], fechas), errors="coerce")
            tn[n] = pd.to_numeric(pd.Series([r[c + 1] if len(r) > c + 1 else None for r in cuerpo], fechas), errors="coerce")

    rows = list(wb["HR"].iter_rows(values_only=True))
    i = [k for k, r in enumerate(rows) if r and r[0] == "Fecha/hora"][0]
    cuerpo = [r for r in rows[i + 1:] if r and r[0] is not None]
    horas = pd.to_datetime([r[0] for r in cuerpo])
    hr = {}
    for c, v in enumerate(rows[i]):
        clave = _norm(str(v).split(" - ")[0]) if v else None
        if clave in por_nombre:
            hr[por_nombre[clave]] = pd.to_numeric(pd.Series([r[c] if len(r) > c else None for r in cuerpo], horas),
                                                   errors="coerce")
    hr = pd.DataFrame(hr)
    hr = hr[hr.index.hour.isin(range(7, 20))]
    out = (meta, pd.DataFrame(tx), pd.DataFrame(tn), hr)
    pd.to_pickle(out, cache)
    return out


# ----------------------------------------------------------------- pluviómetros
def pluviometros():
    """Metadatos (id, nombre, lat, lon) y lluvia diaria (columnas = id). TRAZA = 0."""
    cache = CACHE / "pluviometros.pkl"
    if cache.exists():
        return pd.read_pickle(cache)
    k = leer_kmz()
    kp = k[k.carpeta.str.startswith("Estaciones Pluv")].copy()
    kp["codigo"] = kp["Cod. Pluvio"].astype(str).str.replace(r"\.0$", "", regex=True)
    kp["clave"] = kp["Estación"].map(_norm)
    por_codigo = {c: i for i, c in zip(kp.index, kp.codigo) if c not in ("None", "nan")}
    por_nombre = dict(zip(kp.clave, kp.index))
    alias = {"punta del este (tp)": "punta del este (tp)", "punta del este": "punta del este (tp)",
             "rivera aeropuerto": _norm("Rivera - Aeropuerto Internacional Óscar D. Gestido")}

    series = {}
    for periodo in PERIODOS:
        for archivo in ARCHIVOS_PP:
            wb = openpyxl.load_workbook(BASE / periodo / archivo, read_only=True, data_only=True)
            for ws in wb.worksheets:
                rows = [r for r in ws.iter_rows(values_only=True) if r and any(v is not None for v in r)]
                hdr = [str(h).strip() if h else "" for h in rows[0]]
                cf, cm = hdr.index("Fecha"), hdr.index("[mm]")
                cc = hdr.index("Cod. Pluvio") if "Cod. Pluvio" in hdr else None
                cuerpo = [r for r in rows[1:] if r[cf] is not None]
                codigo = str(cuerpo[0][cc]) if cc is not None else None
                if codigo in por_codigo:
                    idx = por_codigo[codigo]
                else:
                    clave = alias.get(_norm(ws.title), _norm(ws.title))
                    idx = por_nombre.get(clave)
                if idx is None:
                    print("pluviómetro sin ubicación:", periodo, archivo, ws.title)
                    continue
                valores = pd.Series([r[cm] for r in cuerpo], pd.to_datetime([r[cf] for r in cuerpo]))
                valores = valores.astype(str).str.strip().str.upper().replace({"TRAZA": "0"})
                s = pd.to_numeric(valores, errors="coerce")
                s = s[~s.index.duplicated()]
                series[idx] = pd.concat([series[idx], s]) if idx in series else s
    pp = pd.DataFrame(series).sort_index()
    meta = kp.loc[pp.columns, ["Estación", "codigo", "lat", "lon"]].rename(columns={"Estación": "nombre"})
    meta.index.name = "id"
    pp.columns = meta.index
    out = (meta.reset_index(), pp)
    pd.to_pickle(out, cache)
    return out


if __name__ == "__main__":
    meta, tx, tn, hr = series_convencionales()
    print(meta.to_string())
    print("TX datos por estación:", tx.notna().sum().to_dict())
    print("HR datos por estación:", hr.notna().sum().to_dict())
    mp, pp = pluviometros()
    print(mp.to_string())
    print("PP datos por pluviómetro:", pp.notna().sum().describe())
    print(pp.notna().sum().sort_values().head(10))
    m = muestras()
    print(m.groupby("anio").size(), m[["lat", "lon"]].drop_duplicates().shape)
