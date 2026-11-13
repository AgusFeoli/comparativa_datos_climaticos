"""Series diarias recomendadas para cada ubicación de muestreo de maíz.

Todas las variables usan la misma fórmula (peso_distancia.FORMULA, validada en peso_distancia.py):

    valor = (Σ x_i / d_i^p + G / L^p) / (Σ 1 / d_i^p + 1 / L^p)

- x_i: las 3 estaciones INUMET (o pluviómetros) más cercanas con dato ese día, a d_i km de la chacra.
- G: Open-Meteo en la chacra, que entra como una "estación virtual" a L km.
- TX: p = 1, L = 20 km, Open-Meteo corregido antes por cuantiles mensuales contra la estación más cercana con dato.
- TN y HR diurna (07-19 h): p = 1, L = 30 km. Fracción de horas con HR ≥ 80 %: p = 1, L = 50 km.
- Lluvia (07-07 h, fecha del día de inicio): p = 2, L = 80 km.
Salida: series_diarias_muestras.csv
"""
import time
import urllib.parse

import numpy as np
import pandas as pd

import analisis as A
import datos
from descargas import GRILLAS, OM_URL, RANGOS, _get_json
from peso_distancia import FORMULA, combinar

K = 3
D_MAX = {"conv": 200, "pp": 120}  # rango de distancias validado


def _om(lat, lon, variables, prefijo):
    destino = GRILLAS / f"{prefijo}_{A.clave(lat, lon)}.pkl"
    if destino.exists():
        return pd.read_pickle(destino)
    partes = []
    for ini, fin in RANGOS:
        q = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "start_date": ini, "end_date": fin,
                                    "hourly": variables, "timezone": "America/Montevideo"})
        h = pd.DataFrame(_get_json(f"{OM_URL}?{q}")["hourly"])
        h.index = pd.to_datetime(h.pop("time"))
        partes.append(h)
        time.sleep(2)
    h = pd.concat(partes)
    pd.to_pickle(h, destino)
    return h


def om_diario(lat, lon):
    h = _om(lat, lon, "temperature_2m,relative_humidity_2m", "omT")
    d = pd.DataFrame({"tx": h.temperature_2m.resample("D").max(), "tn": h.temperature_2m.resample("D").min()})
    hr = h.relative_humidity_2m[h.index.hour.isin(range(7, 20))]
    d["hr"] = hr.resample("D").mean()
    d["hr80"] = (hr >= A.UMBRAL_HR).astype(float).resample("D").mean()
    d["hr_24h"] = h.relative_humidity_2m.resample("D").mean()
    p = _om(lat, lon, "precipitation", "omP").precipitation
    d["pp"] = p.shift(-A.DESPLAZ_PP["om"]).resample("D").sum(min_count=24).reindex(d.index).round(1)
    return d[A._en_rangos(d.index)]


def k_cercanas(obs, dist, d_max, k=K):
    """Valores, distancias y columnas de las k estaciones más cercanas con dato cada día (NaN / -1 si faltan)."""
    orden = np.argsort(dist)
    orden = orden[dist[orden] <= d_max]
    V = obs.values[:, orden]
    ok = ~np.isnan(V)
    puesto = np.cumsum(ok, axis=1)
    X, D, col = np.full((k, len(obs)), np.nan), np.full((k, len(obs)), np.nan), np.full((k, len(obs)), -1)
    for j in range(k):
        sel = ok & (puesto == j + 1)
        hay = sel.any(1)
        c = sel.argmax(1)[hay]
        X[j, hay] = V[hay, c]
        D[j, hay] = dist[orden][c]
        col[j, hay] = orden[c]
    return X, D, col


def nombres(col, etiquetas):
    return [" / ".join(str(etiquetas[c]) for c in col[:, t] if c >= 0) for t in range(col.shape[1])]


def main():
    meta, conv, mp, pp = A.observadas()
    mp = mp.loc[pp.columns]
    m = datos.muestras()
    u = m.groupby([m.lat.round(4), m.lon.round(4)]).agg(
        muestras=("nombre", lambda s: ", ".join(s)), ubicacion=("Ubicación", "first"),
        departamento=("Departamento / Estado", "first")).reset_index()
    salida = []
    om_est = {}
    for n, r in u.iterrows():
        g = om_diario(r.lat, r.lon)
        d = pd.DataFrame(index=g.index)
        dc = datos.distancia_km(r.lat, r.lon, meta.lat.values, meta.lon.values)
        for v in ["tx", "tn", "hr", "hr80"]:
            f = FORMULA[v]
            X, D, col = k_cercanas(conv[v].reindex(index=g.index, columns=meta.index), dc, D_MAX["conv"])
            grilla = g[v].values
            if f["grilla"] == "om_qm":
                # Open-Meteo corregido por cuantiles con la estación más cercana con dato ese día
                grilla = grilla.copy()
                for j in np.unique(col[0][col[0] >= 0]):
                    s = meta.index[j]
                    if s not in om_est:
                        om_est[s] = A.grillas_diarias(meta.loc[s, "lat"], meta.loc[s, "lon"])["om"]
                    corr = A.mapeo_cuantiles(g[v], om_est[s][v], conv[v][s]).values
                    dia = (col[0] == j) & ~np.isnan(corr)
                    grilla[dia] = corr[dia]
                d[f"{v}_openmeteo_corregido"] = grilla.round(2)
            valor, w_est = combinar(X, D, grilla, f["p"], f["L"])
            d[v] = np.round(valor, 3 if v == "hr80" else 2)
            d[f"{v}_estacion"] = X[0]
            d[f"{v}_openmeteo"] = g[v].values.round(3)
            d[f"peso_openmeteo_{v}"] = np.round(1 - w_est, 2)
            if v in ("tx", "hr"):
                sufijo = "t" if v == "tx" else "hr"
                d[f"estacion_{sufijo}"] = np.where(col[0] >= 0, meta.index.values[np.maximum(col[0], 0)], "")
                d[f"d_estacion_{sufijo}_km"] = np.round(D[0], 1)
                d[f"estaciones_{sufijo}_usadas"] = nombres(col, meta.index.values)
                d[f"d_estaciones_{sufijo}_km"] = [" / ".join(f"{x:.0f}" for x in D[:, t] if not np.isnan(x))
                                                  for t in range(D.shape[1])]
        d["hr_24h_openmeteo_no_validada"] = g.hr_24h.round(1)
        f = FORMULA["pp"]
        dp = datos.distancia_km(r.lat, r.lon, mp.lat.values, mp.lon.values)
        X, D, col = k_cercanas(pp.reindex(index=g.index, columns=mp.index), dp, D_MAX["pp"])
        valor, w_est = combinar(X, D, g.pp.values, f["p"], f["L"])
        d["pp"] = np.round(valor, 1)
        d["pp_pluviometros"] = np.round(combinar(X, D, g.pp.values, 2, np.inf)[0], 1)
        d["pp_openmeteo"] = g.pp.values
        d["peso_openmeteo_pp"] = np.round(1 - w_est, 2)
        d["pluviometros_usados"] = nombres(col, mp.nombre.values)
        d["d_pluviometros_km"] = [" / ".join(f"{x:.0f}" for x in D[:, t] if not np.isnan(x)) for t in range(D.shape[1])]
        d.insert(0, "lat", r.lat)
        d.insert(1, "lon", r.lon)
        d.insert(2, "ubicacion", r.ubicacion)
        d.insert(3, "departamento", r.departamento)
        d.insert(4, "muestras", r.muestras)
        salida.append(d.rename_axis("fecha").reset_index())
        print(n + 1, "/", len(u), r.ubicacion, flush=True)
    out = pd.concat(salida)
    out.to_csv(A.AQUI / "series_diarias_muestras.csv", index=False, encoding="utf-8-sig")
    print(out.shape)


if __name__ == "__main__":
    main()
