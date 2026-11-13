"""¿A partir de qué distancia una estación INUMET deja de servir para una chacra?

Validación cruzada entre estaciones: cada estación INUMET (objetivo B) se estima con
  - otra estación A a distancia d ("estación a d km"),
  - las grillas en B (Open-Meteo, ERA5-Land, NASA POWER y su promedio),
  - estrategias híbridas (mezcla estación+grilla, grilla corregida con la estación A, IDW de varias estaciones),
y se compara el error contra la distancia. Sólo meses de octubre a abril (ciclo del maíz).
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import datos

AQUI = Path(__file__).resolve().parent
FIG = AQUI / "figuras"
FIG.mkdir(exist_ok=True)
GRILLAS = datos.CACHE / "grillas"
MESES = [10, 11, 12, 1, 2, 3, 4]
RANGOS = [("2017-01-01", "2019-12-31"), ("2024-01-01", "2025-12-31")]
FUENTES = ["om", "e5l", "nasa"]
NOMBRE = {"om": "Open-Meteo", "e5l": "ERA5-Land", "nasa": "NASA POWER", "ens": "Promedio 3 grillas"}
DESPLAZ_PP = {"om": 8, "e5l": 8, "nasa": 7}  # hora local que cierra la acumulación 07-07 h
UMBRAL_LLUVIA = 1.0
UMBRAL_HR = 80
D_MAX = {"tx": 200, "tn": 200, "hr": 200, "hr80": 200, "pp": 120}
BINS = {"tx": [0, 30, 60, 90, 120, 150, 200], "pp": [0, 10, 20, 30, 40, 50, 60, 80, 100, 120]}
for v in ("tn", "hr", "hr80"):
    BINS[v] = BINS["tx"]
ESCALAS = {"D": "diaria", "X": "década (10 días)", "M": "mensual"}
VARIABLES = {"tx": "Temperatura máxima (°C)", "tn": "Temperatura mínima (°C)", "hr": "HR media diurna (%)",
             "hr80": "Horas diurnas con HR≥80 % (fracción del día)", "pp": "Lluvia (mm)"}


def _en_rangos(idx):
    m = np.zeros(len(idx), bool)
    for a, b in RANGOS:
        m |= (idx >= a) & (idx <= pd.Timestamp(b) + pd.Timedelta(hours=23))
    return m


def clave(lat, lon):
    return f"{np.round(lat, 3)}_{np.round(lon, 3)}"  # mismo redondeo que pandas en descargas.puntos()


# ----------------------------------------------------------------- grillas -> series diarias
def grillas_diarias(lat, lon):
    k = clave(lat, lon)
    om = pd.read_pickle(GRILLAS / f"om_{k}.pkl")
    h = om["serie"].join(pd.read_pickle(GRILLAS / f"nasa_{k}.pkl"), how="outer")
    f_pp = GRILLAS / f"e5lpp_{round(om['e5l_lat'], 2)}_{round(om['e5l_lon'], 2)}.pkl"
    h["precipitation_e5l"] = pd.read_pickle(f_pp).reindex(h.index) if f_pp.exists() else np.nan
    h = h[_en_rangos(h.index)]
    out = {}
    diurno = h.index.hour.isin(range(7, 20))
    for f in FUENTES:
        d = pd.DataFrame(index=pd.date_range(RANGOS[0][0], RANGOS[-1][1], freq="D"))
        t = f"temperature_2m_{f}"
        if t in h:
            g = h[t].resample("D")
            d["tx"] = g.max()
            d["tn"] = g.min()
            hr = h.loc[diurno, f"relative_humidity_2m_{f}"]
            d["hr"] = hr.resample("D").mean()
            d["hr80"] = (hr >= UMBRAL_HR).astype(float).where(hr.notna()).resample("D").mean()
        pp = h[f"precipitation_{f}"].shift(-DESPLAZ_PP[f]).resample("D").sum(min_count=24)
        d["pp"] = pp.round(1)
        out[f] = d[_en_rangos(d.index)]
    return out


def observadas():
    meta, tx, tn, hr = datos.series_convencionales()
    meta = meta.set_index("nombre").loc[tx.columns]
    dia = hr.index.normalize()
    n = hr.groupby(dia).count()
    hr_d = hr.groupby(dia).mean().where(n >= 11)
    hr80 = (hr >= UMBRAL_HR).astype(float).where(hr.notna()).groupby(dia).mean().where(n >= 11)
    conv = {"tx": tx, "tn": tn, "hr": hr_d, "hr80": hr80}
    mp, pp = datos.pluviometros()
    return meta, conv, mp.set_index("id"), pp


# ----------------------------------------------------------------- métricas
def _grupo(idx, escala):
    if escala == "D":
        return idx
    if escala == "X":
        return idx.year * 1000 + idx.month * 10 + np.minimum((idx.day - 1) // 10, 2)
    return idx.year * 100 + idx.month


_COMPLETO = {}


def _dias_por_grupo(escala):
    if escala not in _COMPLETO:
        idx = pd.date_range(RANGOS[0][0], RANGOS[-1][1], freq="D")
        _COMPLETO[escala] = pd.Series(1, idx).groupby(_grupo(idx, escala)).sum()
    return _COMPLETO[escala]


def agregar(o, e, var, escala):
    m = o.notna() & e.notna() & o.index.month.isin(MESES)
    o, e = o[m], e[m]
    if escala == "D":
        return o, e
    g = _grupo(o.index, escala)
    n = o.groupby(g).count()
    ok = n.index[n >= 0.9 * _dias_por_grupo(escala).reindex(n.index)]
    f = "sum" if var == "pp" else "mean"
    return o.groupby(g).agg(f).loc[ok], e.groupby(g).agg(f).loc[ok]


def puntuar(o, e, var, escala):
    o, e = agregar(o, e, var, escala)
    if len(o) < (60 if escala == "D" else 8):
        return None
    err = e - o
    r = {"n": len(o), "mae": float(err.abs().mean()), "sesgo": float(err.mean())}
    if var == "pp":
        r["mae_rel"] = r["mae"] / float(o.mean()) if o.mean() > 0 else np.nan
        if escala == "D":
            a, b = o >= UMBRAL_LLUVIA, e >= UMBRAL_LLUVIA
            hits = (a & b).sum()
            r["csi"] = float(hits / max((a | b).sum(), 1))
    return r


# ----------------------------------------------------------------- estimadores
def corr_mensual(g_b, g_a, obs_a, var):
    """Grilla en B corregida con el error medio mensual de esa grilla en la estación A."""
    m = g_a.notna() & obs_a.notna()
    mes = g_a.index.month
    if var == "pp":
        f = (obs_a[m].groupby(mes[m]).sum() / g_a[m].groupby(mes[m]).sum()).clip(0.3, 3).fillna(1)
        return g_b * f.reindex(g_b.index.month).values
    s = (obs_a[m] - g_a[m]).groupby(mes[m]).mean()
    out = g_b + s.reindex(g_b.index.month).fillna(0).values
    return out.clip(0, 100) if var == "hr" else out.clip(0, 1) if var == "hr80" else out


def mapeo_cuantiles(g_b, g_a, obs_a, n_q=50):
    """Corrige la distribución mensual de la grilla en B con la relación grilla↔estación observada en A."""
    out = pd.Series(np.nan, g_b.index)
    q = np.linspace(0.01, 0.99, n_q)
    m = g_a.notna() & obs_a.reindex(g_a.index).notna()
    for mes in range(1, 13):
        mk = m & (g_a.index.month == mes)
        if mk.sum() < 30:
            continue
        ga_q, oa_q = np.quantile(g_a[mk], q), np.quantile(obs_a.reindex(g_a.index)[mk], q)
        mb = g_b.index.month == mes
        out[mb] = g_b[mb] + np.interp(g_b[mb], ga_q, oa_q - ga_q)
    return out


def conteos_umbral(meta, conv, grids, var, umbral, signo=1, d_max=120):
    """Error en el número de días por campaña (oct-abr) que superan un umbral, por método y distancia."""
    obs = conv[var]
    est = [s for s in obs.columns if obs[s].notna().sum() >= 200 and s in grids]
    c = meta.loc[est]
    D = pd.DataFrame(datos.distancia_km(c.lat.values[:, None], c.lon.values[:, None],
                                        c.lat.values[None], c.lon.values[None]), est, est)
    filas = []
    for b in est:
        gb = grids[b]["om"][var]
        ob = obs[b].reindex(gb.index)
        for a in est:
            if a == b or D.loc[a, b] > d_max:
                continue
            oa, ga = obs[a].reindex(gb.index), grids[a]["om"][var]
            cand = {"estacion": oa, "om": gb, "mezcla50_om": 0.5 * oa + 0.5 * gb,
                    "mezcla50qm_om": 0.5 * oa + 0.5 * mapeo_cuantiles(gb, ga, oa)}
            m = ob.notna() & oa.notna() & ob.index.month.isin(MESES)
            camp = np.where(ob[m].index.month >= 10, ob[m].index.year + 1, ob[m].index.year)
            n = ob[m].groupby(camp).count()
            ok = n.index[n >= 150]
            o = (signo * ob[m] >= signo * umbral).groupby(camp).sum()[ok]
            for k, s in cand.items():
                e = (signo * s[m] >= signo * umbral).groupby(camp).sum()[ok]
                filas.append({"objetivo": b, "donante": a, "d": D.loc[a, b], "metodo": k, "dias_obs": o.mean(),
                              "sesgo": (e - o).mean(), "mae": (e - o).abs().mean()})
    return pd.DataFrame(filas)


def delta_diario(obs_a, g_b, g_a, var):
    """Estación A + (grilla B − grilla A): traslada el gradiente espacial de la grilla."""
    if var == "pp":
        return (obs_a + g_b - g_a).clip(lower=0)
    out = obs_a + g_b - g_a
    return out.clip(0, 100) if var == "hr" else out.clip(0, 1) if var == "hr80" else out


def series_grilla(g, var):
    s = {f: g[f][var] for f in FUENTES if var in g[f]}
    s["ens"] = pd.concat(s.values(), axis=1).mean(axis=1, skipna=False)
    return s


def evaluar_variable(var, coords, obs, grids):
    """coords: DataFrame(lat, lon) por estación; obs: DataFrame diario; grids: {estación: {fuente: df}}."""
    est = [s for s in obs.columns if obs[s].notna().sum() >= 200 and s in grids]
    c = coords.loc[est]
    D = pd.DataFrame(datos.distancia_km(c.lat.values[:, None], c.lon.values[:, None],
                                        c.lat.values[None], c.lon.values[None]), est, est)
    filas_grilla, filas_par = [], []
    G = {s: series_grilla(grids[s], var) for s in est}
    for b in est:
        ob = obs[b]
        g = G[b]
        for f, s in g.items():
            for esc in ESCALAS:
                r = puntuar(ob, s, var, esc)
                if r:
                    filas_grilla.append({"objetivo": b, "fuente": f, "escala": esc, **r})
        donantes = D.loc[b].drop(b)
        donantes = donantes[(donantes > 2) & (donantes <= D_MAX[var])].sort_values()
        for rank, (a, d) in enumerate(donantes.items()):
            oa = obs[a]
            cand = {"estacion": oa}
            for f in g:
                ga = G[a][f]
                for w in (0.25, 0.5, 0.75):
                    cand[f"mezcla{int(w * 100)}_{f}"] = w * oa + (1 - w) * g[f]
                cand[f"corrmes_{f}"] = corr_mensual(g[f], ga, oa, var)
                cand[f"delta_{f}"] = delta_diario(oa, g[f], ga, var)
                if f == "om" and var != "pp":
                    cand["mezcla50qm_om"] = 0.5 * oa + 0.5 * mapeo_cuantiles(g[f], ga, oa)
            if rank == 0:
                vec = donantes.index[:3]
                w = 1 / donantes.loc[vec] ** 2
                cand["idw3"] = (obs[vec] * w.values).sum(axis=1, min_count=1) / \
                               (obs[vec].notna() * w.values).sum(axis=1).replace(0, np.nan)
                for f in ("om", "nasa", "ens"):
                    if f in g:
                        cand[f"idw3_mezcla50_{f}"] = 0.5 * cand["idw3"] + 0.5 * g[f]
            for nombre, s in cand.items():
                for esc in ESCALAS:
                    r = puntuar(ob, s, var, esc)
                    if r:
                        filas_par.append({"objetivo": b, "donante": a, "d": d, "rank": rank, "metodo": nombre,
                                          "escala": esc, **r})
    return pd.DataFrame(filas_grilla), pd.DataFrame(filas_par), D


def cargar_todo():
    meta, conv, mp, pp = observadas()
    grids_conv = {}
    for s, r in meta.iterrows():
        try:
            grids_conv[s] = grillas_diarias(r.lat, r.lon)
        except FileNotFoundError:
            pass
    grids_pp = {}
    for i, r in mp.iterrows():
        try:
            grids_pp[i] = grillas_diarias(r.lat, r.lon)
        except FileNotFoundError:
            pass
    return meta, conv, mp, pp, grids_conv, grids_pp


def curva(par, var, esc, metodo="estacion", metrica="mae", d_max=150):
    """Recta robusta (Theil-Sen) error = a + b·d con los pares a menos de d_max km."""
    p = par[(par.metodo == metodo) & (par.escala == esc) & (par.d <= d_max)].dropna(subset=[metrica])
    b, a, *_ = stats.theilslopes(p[metrica], p.d)
    return a, b


def cruce(par, grilla, var, esc, metodo="estacion", fuente="om", metrica="mae", d_max=150):
    """Distancia a la que la recta de error de la estación vecina alcanza el error típico de la grilla."""
    a, b = curva(par, var, esc, metodo, metrica, d_max)
    ref = grilla[(grilla.fuente == fuente) & (grilla.escala == esc)][metrica].median()
    if metrica == "csi":
        a, b, ref = -a, -b, -ref
    if a >= ref:
        return 0.0
    return float((ref - a) / b) if b > 0 else np.inf


if __name__ == "__main__":
    meta, conv, mp, pp, grids_conv, grids_pp = cargar_todo()
    print(len(grids_conv), "convencionales con grilla;", len(grids_pp), "pluviómetros con grilla")
    res = {}
    for var in ["tx", "tn", "hr", "hr80"]:
        res[var] = evaluar_variable(var, meta[["lat", "lon"]], conv[var], grids_conv)
    res["pp"] = evaluar_variable("pp", mp[["lat", "lon"]], pp, grids_pp)
    pd.to_pickle(res, datos.CACHE / "resultados.pkl")
    print("guardado")
