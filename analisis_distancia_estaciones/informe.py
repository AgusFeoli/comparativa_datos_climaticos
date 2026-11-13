"""Figuras, tablas y recomendación por muestra a partir de analisis.py."""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import analisis as A
import datos
from peso_distancia import FORMULA

RES = datos.CACHE / "resultados.pkl"
METODOS = {"estacion": "Estación INUMET más cercana", "idw3": "Promedio 3 estaciones (IDW)",
           "mezcla50_om": "50 % estación + 50 % Open-Meteo", "mezcla50_ens": "50 % estación + 50 % promedio grillas",
           "mezcla75_om": "75 % estación + 25 % Open-Meteo", "delta_om": "Estación + gradiente Open-Meteo",
           "idw3_mezcla50_ens": "50 % IDW 3 estaciones + 50 % promedio grillas",
           "mezcla50qm_om": "50 % estación + 50 % Open-Meteo corregido por cuantiles", "om": "Open-Meteo solo",
           "corrmes_om": "Open-Meteo corregido con la estación (mensual)"}
COLOR = {"estacion": "k", "idw3": "tab:purple", "mezcla50_om": "tab:red", "mezcla50_ens": "tab:orange",
         "mezcla75_om": "tab:pink", "delta_om": "tab:brown", "corrmes_om": "tab:olive"}
COLOR_G = {"om": "tab:blue", "e5l": "tab:green", "nasa": "tab:gray", "ens": "tab:cyan"}
BINS_TABLA = {"conv": [0, 30, 60, 90, 120, 200], "pp": [0, 10, 20, 30, 45, 60, 80, 120]}
PANELES = [("tx", "D", "mae"), ("tn", "D", "mae"), ("hr", "D", "mae"), ("hr80", "D", "mae"),
           ("tx", "M", "mae"), ("hr", "M", "mae"), ("pp", "D", "csi"), ("pp", "D", "mae"),
           ("pp", "X", "mae_rel"), ("pp", "M", "mae_rel")]
ETQ_MET = {"mae": "Error absoluto medio", "csi": "CSI (acierto de días con lluvia ≥1 mm)",
           "mae_rel": "Error absoluto medio relativo"}


def resultados():
    if RES.exists():
        return pd.read_pickle(RES)
    meta, conv, mp, pp, gc, gp = A.cargar_todo()
    res = {v: A.evaluar_variable(v, meta[["lat", "lon"]], conv[v], gc) for v in ["tx", "tn", "hr", "hr80"]}
    res["pp"] = A.evaluar_variable("pp", mp[["lat", "lon"]], pp, gp)
    pd.to_pickle(res, RES)
    return res


def tabla(res, var, esc, met, metodos=("estacion", "idw3", "mezcla50_om", "mezcla50qm_om", "mezcla50_ens",
                                       "idw3_mezcla50_ens", "delta_om")):
    gr, par, _ = res[var]
    bins = BINS_TABLA["pp" if var == "pp" else "conv"]
    q = par[(par.escala == esc) & par.metodo.isin(metodos)]
    t = q.groupby(["metodo", pd.cut(q.d, bins)], observed=False)[met].median().unstack()
    n = q[q.metodo == "estacion"].groupby(pd.cut(q.d, bins), observed=False).size()
    t = t.loc[[m for m in metodos if m in t.index]]
    t.index = [METODOS[m] for m in t.index]
    g = gr[gr.escala == esc].groupby("fuente")[met].median()
    for f in ["om", "e5l", "nasa", "ens"]:
        if f in g:
            t.loc[f"Grilla sola: {A.NOMBRE[f]}"] = g[f]
    t.loc["n pares"] = n.values
    t.columns = [f"{int(i.left)}–{int(i.right)} km" for i in t.columns]
    return t


def a_md(t, dec=2):
    cab = "| | " + " | ".join(t.columns) + " |\n|---|" + "---:|" * len(t.columns) + "\n"
    filas = ["| " + i + " | " + " | ".join("—" if pd.isna(v) else (f"{int(v)}" if i == "n pares" else f"{v:.{dec}f}")
                                         for v in r) + " |" for i, r in t.iterrows()]
    return cab + "\n".join(filas)


def figura_curvas(res):
    fig, ax = plt.subplots(5, 2, figsize=(13, 22))
    for a, (var, esc, met) in zip(ax.flat, PANELES):
        gr, par, _ = res[var]
        bins = np.array(BINS_TABLA["pp" if var == "pp" else "conv"])
        centro = (bins[1:] + bins[:-1]) / 2
        q = par[par.escala == esc]
        e = q[q.metodo == "estacion"]
        a.scatter(e.d, e[met], s=8, color="k", alpha=0.25, label="par de estaciones")
        for m in ("estacion", "idw3", "mezcla50_om", "delta_om"):
            s = q[q.metodo == m].groupby(pd.cut(q[q.metodo == m].d, bins), observed=False)[met].median()
            a.plot(centro, s.values, "-o", color=COLOR[m], label=METODOS[m], lw=2, ms=4)
        g = gr[gr.escala == esc].groupby("fuente")[met].median()
        for f in ["om", "e5l", "nasa"]:
            if f in g:
                a.axhline(g[f], color=COLOR_G[f], ls="--", label=f"{A.NOMBRE[f]} (en el punto)")
        a.set_title(f"{A.VARIABLES[var]} — escala {A.ESCALAS[esc]}", fontsize=10)
        a.set_xlabel("Distancia a la estación usada (km)")
        a.set_ylabel(ETQ_MET[met])
        a.set_xlim(0, bins[-1])
        a.grid(alpha=0.3)
    ax.flat[0].legend(fontsize=7, loc="upper left")
    ax.flat[6].legend(fontsize=7, loc="lower left")
    fig.suptitle("Error al estimar una estación INUMET según la distancia (octubre–abril; medianas por tramo)", y=0.995)
    fig.tight_layout()
    fig.savefig(A.FIG / "error_vs_distancia.png", dpi=130)
    plt.close(fig)


def recomendacion(var):
    f = FORMULA[var]
    fuente = "pluviómetros INUMET" if var == "pp" else "estaciones INUMET"
    grilla = "Open-Meteo corregido por cuantiles" if f["grilla"] == "om_qm" else "Open-Meteo"
    peso = "1/d" if f["p"] == 1 else f"1/d^{f['p']}"
    return f"3 {fuente} más cercanos con dato ({peso}) + {grilla} como estación a {f['L']} km"


def peso_openmeteo(d3, var, d_max):
    """Fracción del valor final que aporta Open-Meteo, dadas las distancias a las 3 estaciones más cercanas."""
    f = FORMULA[var]
    d3 = np.maximum(d3, 1.0)
    ws = np.where(np.isfinite(d3) & (d3 <= d_max), 1 / d3 ** f["p"], 0).sum(1)
    return (f["L"] ** -f["p"] / (ws + f["L"] ** -f["p"])).round(2)


def tabla_muestras():
    meta, tx, _, _ = datos.series_convencionales()
    conv = meta[meta.nombre.isin(tx.columns)]
    mp, pp = datos.pluviometros()
    mp = mp[mp.id.isin(pp.columns[pp.notna().sum() >= 200])]
    m = datos.muestras()
    dc = datos.distancia_km(m.lat.values[:, None], m.lon.values[:, None], conv.lat.values[None], conv.lon.values[None])
    dp = datos.distancia_km(m.lat.values[:, None], m.lon.values[:, None], mp.lat.values[None], mp.lon.values[None])
    m["estacion_cercana"] = conv.nombre.values[dc.argmin(1)]
    m["d_estacion_km"] = dc.min(1).round(1)
    # estación más cercana con ≥80 % de días con dato en el ciclo de la muestra (1 oct del año anterior → muestreo)
    _, obs, _, _ = A.observadas()
    for v, suf in (("tx", "t"), ("hr", "hr")):
        cob = []
        for _, r in m.iterrows():
            fin = r.fecha if pd.notna(r.fecha) else pd.Timestamp(f"{r.anio}-04-30")
            x = obs[v].reindex(columns=conv.nombre).loc[f"{r.anio - 1}-10-01":fin]
            cob.append((x.notna().mean() >= 0.8).values)
        dd = np.where(np.array(cob), dc, np.inf)
        m[f"estacion_{suf}_ciclo"] = np.where(np.isfinite(dd.min(1)), conv.nombre.values[dd.argmin(1)], "")
        m[f"d_estacion_{suf}_ciclo_km"] = dd.min(1).round(1)
        orden = np.argsort(dd, 1)[:, :3]
        d3 = np.take_along_axis(dd, orden, 1)
        m[f"estaciones_{suf}_ciclo"] = [" / ".join(conv.nombre.values[o][np.isfinite(x)]) for o, x in zip(orden, d3)]
        m[f"d_estaciones_{suf}_ciclo_km"] = [" / ".join(f"{x:.0f}" for x in fila if np.isfinite(x)) for fila in d3]
        for var in (("tx", "tn") if v == "tx" else ("hr",)):
            m[f"peso_openmeteo_{var}"] = peso_openmeteo(d3, var, 200)
    cob = []
    for _, r in m.iterrows():
        x = pp.reindex(columns=mp.id).loc[f"{r.anio - 1}-10-01":r.fecha]
        cob.append((x.notna().mean() >= 0.8).values)
    dp = np.where(np.array(cob), dp, np.inf)
    orden = np.argsort(dp, 1)[:, :3]
    m["pluviometro_cercano"] = mp.nombre.values[orden[:, 0]]
    m["d_pluviometro_km"] = dp.min(1).round(1)
    m["pluviometros_3"] = [" / ".join(mp.nombre.values[o]) for o in orden]
    m["d_pluviometros_3_km"] = [" / ".join(f"{dp[i, j]:.0f}" for j in o) for i, o in enumerate(orden)]
    m["peso_openmeteo_pp"] = peso_openmeteo(np.take_along_axis(dp, orden, 1), "pp", 120)
    m["temperatura_maxima"] = recomendacion("tx")
    m["temperatura_minima"] = recomendacion("tn")
    m["humedad"] = recomendacion("hr")
    m["lluvia"] = recomendacion("pp")
    return m


def figura_mapa(m):
    meta, tx, _, _ = datos.series_convencionales()
    conv = meta[meta.nombre.isin(tx.columns)]
    mp, _ = datos.pluviometros()
    fig, ax = plt.subplots(1, 2, figsize=(14, 6.5))
    a = ax[0]
    a.scatter(mp.lon, mp.lat, marker="^", s=18, color="tab:blue", label="Pluviómetro INUMET")
    a.scatter(conv.lon, conv.lat, marker="s", s=40, color="k", label="Estación convencional INUMET")
    sc = a.scatter(m.lon, m.lat, c=m.d_estacion_km, cmap="viridis_r", s=30, edgecolor="r", vmin=0, vmax=70,
                   label="Muestra de maíz")
    plt.colorbar(sc, ax=a, label="Distancia a la estación convencional más cercana (km)")
    a.set_aspect(1 / np.cos(np.radians(-32.5)))
    a.legend(fontsize=8, loc="upper right")
    a.set_title("Estaciones, pluviómetros y muestras")
    b = ax[1]
    b.hist([m.d_estacion_t_ciclo_km, m.d_estacion_hr_ciclo_km.clip(upper=139), m.d_pluviometro_km],
           bins=np.arange(0, 145, 10), color=["k", "tab:green", "tab:blue"],
           label=["estación con temperatura", "estación con humedad", "pluviómetro"])
    b.set_xlabel("Distancia al dato INUMET con ≥80 % de cobertura en el ciclo de la muestra (km)")
    b.set_ylabel("Muestras")
    b.legend(fontsize=8)
    b.set_title("¿A qué distancia está el dato INUMET de cada muestra?")
    fig.tight_layout()
    fig.savefig(A.FIG / "mapa_distancias.png", dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    res = resultados()
    figura_curvas(res)
    salida = []
    for var, esc, met in PANELES + [("hr80", "M", "mae"), ("tn", "M", "mae"), ("tx", "X", "mae"), ("hr", "X", "mae")]:
        dec = 3 if var == "hr80" else 2
        salida.append(f"\n### {A.VARIABLES[var]} — {A.ESCALAS[esc]} — {met}\n\n" + a_md(tabla(res, var, esc, met), dec))
    meta, conv, _, _, gc, _ = A.cargar_todo()
    for var, u, sg, txt in (("tx", 30, 1, "TX ≥ 30 °C"), ("tx", 32, 1, "TX ≥ 32 °C"), ("tn", 5, -1, "TN ≤ 5 °C"),
                            ("hr", 80, 1, "HR media diurna ≥ 80 %")):
        c = A.conteos_umbral(meta, conv, gc, var, u, sg)
        t = c.groupby(["metodo", pd.cut(c.d, [0, 60, 120])], observed=True)[["sesgo", "mae"]].median().unstack()
        t.columns = [f"{'sesgo' if a == 'sesgo' else 'error abs.'} {int(i.left)}–{int(i.right)} km" for a, i in t.columns]
        t.index = [METODOS[i] for i in t.index]
        salida.append(f"\n### Días por campaña (oct–abr) con {txt} — media observada {c.dias_obs.mean():.1f} días\n\n"
                      + a_md(t, 1))
    (A.AQUI / "tablas.md").write_text("\n".join(salida), encoding="utf-8")
    m = tabla_muestras()
    figura_mapa(m)
    m.to_csv(A.AQUI / "recomendacion_por_muestra.csv", index=False, encoding="utf-8-sig")
    u = m.drop_duplicates(["lat", "lon"])
    print(len(m), "muestras,", len(u), "ubicaciones")
    print(m[["d_estacion_t_ciclo_km", "d_estacion_hr_ciclo_km", "d_pluviometro_km", "peso_openmeteo_tx",
             "peso_openmeteo_tn", "peso_openmeteo_hr", "peso_openmeteo_pp"]].describe().round(2).to_string())
