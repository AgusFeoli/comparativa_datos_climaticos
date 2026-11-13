"""Comparación NASA POWER (MERRA-2) vs INUMET - Estación Colonia, y cara a cara contra Open-Meteo.

Fuentes evaluadas:
  - nasa_archivo : "Comparación datos INUMET vs NASA - NASA.csv" (punto de la estación San José, 2025, hora LST)
  - nasa_colonia : NASA POWER descargado para las coordenadas de la estación Colonia (2017-2025, UTC)
  - open_meteo   : open-meteo-34.41S57.74W25m.csv

Uso: python comparacion_nasa.py   (requiere pandas, numpy, openpyxl, scipy, matplotlib)
"""
import json
import sys
import urllib.request
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
sys.path.insert(0, str(BASE / "analisis_open_meteo_vs_inumet"))
from comparacion import (HORAS_OBS, KT_A_KMH, anio, cargar_inumet, cargar_open_meteo, contingencia,  # noqa: E402
                         dif_angular, estacion_ano, metricas, periodo, por_grupo, sector8)

FIG = OUT / "figuras"
FIG.mkdir(exist_ok=True)
DATOS = OUT / "datos_nasa_colonia"
DATOS.mkdir(exist_ok=True)
NASA_ARCHIVO = BASE / "Comparación datos INUMET vs NASA - NASA.csv"
LAT_COLONIA, LON_COLONIA = -34.4518742, -57.7677703
ANIOS = [2017, 2018, 2019, 2024, 2025]
API = "https://power.larc.nasa.gov/api/temporal"
COLORES = {"INUMET": "k", "Open-Meteo": "tab:orange", "NASA Colonia": "tab:green", "NASA archivo (San José)": "tab:purple"}


# ----------------------------------------------------------------- carga NASA
def _leer_power(path):
    lineas = Path(path).read_text().splitlines()
    i = [k for k, l in enumerate(lineas) if l.startswith("-END HEADER")][0]
    return pd.read_csv(path, skiprows=i + 1).replace(-999, np.nan)


def descargar_nasa_colonia():
    base = f"community=AG&longitude={LON_COLONIA}&latitude={LAT_COLONIA}&format=CSV"
    pedidos = {f"h_{a}.csv": f"{API}/hourly/point?parameters=T2M,RH2M,WS2M,WD2M,WS10M,WD10M,PRECTOTCORR"
                              f"&start={a}0101&end={a}1231&time-standard=UTC&{base}" for a in ANIOS}
    pedidos["d_all.csv"] = (f"{API}/daily/point?parameters=T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS10M"
                            f"&start=20170101&end=20251231&{base}")
    for nombre, url in pedidos.items():
        if not (DATOS / nombre).exists():
            urllib.request.urlretrieve(url, DATOS / nombre)


def cargar_nasa_colonia():
    descargar_nasa_colonia()
    h = pd.concat([_leer_power(DATOS / f"h_{a}.csv") for a in ANIOS])
    # UTC -> hora local Uruguay (UTC-3)
    h.index = pd.to_datetime(dict(year=h.YEAR, month=h.MO, day=h.DY, hour=h.HR)) - pd.Timedelta(hours=3)
    d = _leer_power(DATOS / "d_all.csv")
    d.index = pd.to_datetime(d.YEAR.astype(str), format="%Y") + pd.to_timedelta(d.DOY - 1, unit="D")
    return h, d


def cargar_nasa_archivo():
    raw = pd.read_csv(NASA_ARCHIVO, skiprows=6, header=0)
    d = raw.iloc[:, 0:4].dropna()
    d.columns = ["Y", "DOY", "TX", "TN"]
    d.index = pd.to_datetime(d.Y.astype(int).astype(str), format="%Y") + pd.to_timedelta(d.DOY.astype(int) - 1, unit="D")
    h = raw.iloc[:, 5:12].dropna()
    h.columns = ["Y", "MO", "DY", "HR", "RH", "WS", "WD"]
    # LST de NASA en San José = UTC-4 -> hora local Uruguay (UTC-3) = LST + 1 h
    h.index = pd.to_datetime(dict(year=h.Y.astype(int), month=h.MO.astype(int), day=h.DY.astype(int),
                                  hour=h.HR.astype(int))) + pd.Timedelta(hours=1)
    return d[["TX", "TN"]].astype(float), h[["RH", "WS", "WD"]].astype(float)


# ----------------------------------------------------------------- fuentes homogéneas
def pp_07_07(serie_horaria, desplazamiento):
    """Lluvia de 07 h del día D a 07 h del día D+1, rotulada D (convención INUMET)."""
    return serie_horaria.shift(-desplazamiento).resample("D").sum(min_count=24).round(1)


def fuentes():
    _, h, _ = cargar_open_meteo()
    om = {"tx": h["temperature_2m (°C)"].resample("D").max(),
          "tn": h["temperature_2m (°C)"].resample("D").min(),
          "rh": h["relative_humidity_2m (%)"],
          "ws": h["wind_speed_10m (km/h)"],
          "wd": h["wind_direction_10m (°)"],
          # hora t de Open-Meteo acumula (t-1, t]
          "pp": pp_07_07(h["precipitation (mm)"], 8)}

    hn, dn = cargar_nasa_colonia()
    nc = {"tx": dn.T2M_MAX, "tn": dn.T2M_MIN, "rh": hn.RH2M, "ws": hn.WS10M * 3.6, "wd": hn.WD10M,
          # hora t de MERRA-2 promedia [t, t+1)
          "pp": pp_07_07(hn.PRECTOTCORR, 7), "pp_dia_nasa": dn.PRECTOTCORR,
          "ws2": hn.WS2M * 3.6}

    da, ha = cargar_nasa_archivo()
    factor_2_a_10 = float((hn.WS10M / hn.WS2M).replace([np.inf, -np.inf], np.nan).median())
    na = {"tx": da.TX, "tn": da.TN, "rh": ha.RH, "ws": ha.WS * 3.6 * factor_2_a_10, "ws2": ha.WS * 3.6,
          "wd": ha.WD}
    return {"Open-Meteo": om, "NASA Colonia": nc, "NASA archivo (San José)": na}, factor_2_a_10


# ----------------------------------------------------------------- evaluación
def evaluar(src, txtn, hr_obs, viento, pp, anios=None, extendido=True):
    def rec(s):
        s = s.dropna()
        return s[s.index.year.isin(anios)] if anios else s

    ws_obs = rec(viento.IntV.astype(float) * KT_A_KMH)
    R = {}
    for var in ["tx", "tn"]:
        obs = rec(txtn[var.upper()])
        R[var] = {"global": metricas(obs, src[var], (1, 2, 3))}
        if extendido:
            R[var] |= {"estacion": por_grupo(obs, src[var], estacion_ano, (1, 2, 3)),
                       "anio": por_grupo(obs, src[var], anio, (1, 2, 3))}
    df = pd.concat([rec(txtn.TX), rec(txtn.TN), src["tx"].rename("mTX"), src["tn"].rename("mTN")],
                   axis=1, sort=True).dropna()
    R["extremos"] = {
        "TX>=30": [int((df.TX >= 30).sum()), int((df.mTX >= 30).sum())],
        "TX>=35": [int((df.TX >= 35).sum()), int((df.mTX >= 35).sum())],
        "TN<=3": [int((df.TN <= 3).sum()), int((df.mTN <= 3).sum())],
        "TN<=0": [int((df.TN <= 0).sum()), int((df.mTN <= 0).sum())]}

    hro = rec(hr_obs)
    R["rh"] = {"global": metricas(hro, src["rh"], (5, 10, 15)),
               "diaria": metricas(hro.resample("D").mean()[hro.resample("D").count() >= 10],
                                  src["rh"][src["rh"].index.hour.isin(HORAS_OBS)].resample("D").mean(), (5, 10))}
    if extendido:
        R["rh"] |= {"estacion": por_grupo(hro, src["rh"], estacion_ano, (5, 10, 15)),
                    "anio": por_grupo(hro, src["rh"], anio, (5, 10, 15))}

    R["ws"] = {"global": metricas(ws_obs, src["ws"], (5, 10)),
               "diaria": metricas(ws_obs.resample("D").mean()[ws_obs.resample("D").count() >= 10],
                                  src["ws"][src["ws"].index.hour.isin(HORAS_OBS)].resample("D").mean(), (3, 5))}
    if "ws2" in src:
        R["ws"]["sin_ajustar_2m"] = metricas(ws_obs, src["ws2"], (5, 10))
    dfw = pd.concat([ws_obs.rename("o"), src["ws"].rename("m")], axis=1, sort=True).dropna()
    R["ws"]["percentiles"] = {"inumet": dfw.o.quantile([.5, .9, .99]).round(1).to_dict(),
                              "fuente": dfw.m.quantile([.5, .9, .99]).round(1).to_dict()}
    if extendido:
        R["ws"]["anio"] = por_grupo(ws_obs, src["ws"], anio, (5, 10))

    dir_obs = rec(pd.to_numeric(viento.DirV, errors="coerce"))
    dfd = pd.concat([dir_obs.rename("o"), src["wd"].rename("m"), ws_obs.rename("vo")], axis=1, sort=True).dropna()
    dfd = dfd[dfd.vo >= 2 * KT_A_KMH]
    e = dif_angular(dfd.o, dfd.m)
    R["wd"] = {"n": int(len(dfd)), "mediana_error": round(float(e.abs().median()), 1),
               "error_medio": round(float(e.abs().mean()), 1),
               "pct_dentro_45": round(float(100 * (e.abs() <= 45).mean()), 1),
               "pct_mismo_sector8": round(float(100 * (sector8(dfd.o.values) == sector8(dfd.m.values)).mean()), 1),
               "frec_inumet": (pd.Series(sector8(dfd.o.values)).value_counts(normalize=True) * 100).round(1).to_dict(),
               "frec_fuente": (pd.Series(sector8(dfd.m.values)).value_counts(normalize=True) * 100).round(1).to_dict()}

    if "pp" in src and pp is not None:
        dfp = pd.concat([rec(pp.mm).rename("o"), src["pp"].rename("m")], axis=1, sort=True).dropna()
        R["pp"] = {"diaria": metricas(dfp.o, dfp.m, (1, 5)),
                   "contingencia": [contingencia(dfp.o, dfp.m, u) for u in (0.1, 1, 5, 10, 20, 50)]}
        for nombre, regla, minimo in [("semanal", "W", 6), ("mensual", "MS", 26)]:
            g = dfp.resample(regla)
            agg = g.sum()[g.o.count() >= minimo]
            agg = agg[agg.index.year.isin(anios or ANIOS)]
            err = agg.m - agg.o
            R["pp"][nombre] = {**metricas(agg.o, agg.m), "sesgo_pct": round(float(100 * err.sum() / agg.o.sum()), 1),
                               "pct_dentro_20pct_o_10mm": round(float(100 * (err.abs() <= np.maximum(0.2 * agg.o, 10)).mean()), 1)}
        an = dfp.groupby(dfp.index.year)[["o", "m"]].sum()
        an["dif_pct"] = 100 * (an.m - an.o) / an.o
        R["pp"]["anual"] = an.round(1).to_dict(orient="index")
        R["pp"]["clim_mensual"] = (dfp.groupby(dfp.index.month)[["o", "m"]].sum() / dfp.index.year.nunique()).round(1).to_dict()
        top = dfp.sort_values("o", ascending=False).head(15)
        R["pp"]["top15"] = [[str(i.date()), float(r.o), float(r.m)] for i, r in top.iterrows()]
        R["_dfp"] = dfp
    return R


def correccion_sesgo(src, txtn):
    out = {}
    for var in ["TX", "TN"]:
        df = pd.concat([txtn[var].rename("o"), src[var.lower()].rename("m")], axis=1, sort=True).dropna()
        cal, val = df[df.index.year <= 2019], df[df.index.year >= 2024]
        sm = (cal.m - cal.o).groupby(cal.index.month).mean()
        out[var] = {"sesgo_mensual": sm.round(2).to_dict(),
                    "validacion_sin_corregir": metricas(val.o, val.m, (1, 2, 3)),
                    "validacion_corregido": metricas(val.o, val.m - val.index.month.map(sm).values, (1, 2, 3))}
    return out


# ----------------------------------------------------------------- figuras
def figuras(F, txtn, hr_obs, viento, R_full):
    plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": .3})
    nc = F["NASA Colonia"]

    fig, ax = plt.subplots(1, 2, figsize=(11, 5))
    for a, var, col in [(ax[0], "TX", "tab:red"), (ax[1], "TN", "tab:blue")]:
        x = pd.concat([txtn[var].rename("o"), nc[var.lower()].rename("m")], axis=1, sort=True).dropna()
        x = x[x.index.year.isin(ANIOS)]
        a.scatter(x.o, x.m, s=5, alpha=.4, c=col)
        lim = [x.min().min() - 1, x.max().max() + 1]
        a.plot(lim, lim, "k--", lw=1)
        a.set(xlim=lim, ylim=lim, xlabel=f"INUMET {var} (°C)", ylabel=f"NASA {var} (°C)",
              title=f"NASA Colonia {var}  r={x.o.corr(x.m):.3f}  MAE={(x.m - x.o).abs().mean():.2f} °C")
    fig.tight_layout(); fig.savefig(FIG / "nasa_temp_dispersion.png"); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for a, var in [(ax[0], "TX"), (ax[1], "TN")]:
        for nombre in ["Open-Meteo", "NASA Colonia"]:
            x = pd.concat([txtn[var].rename("o"), F[nombre][var.lower()].rename("m")], axis=1, sort=True).dropna()
            x = x[x.index.year.isin(ANIOS)]
            b = (x.m - x.o).groupby(x.index.month).mean()
            a.plot(b.index, b.values, "o-", color=COLORES[nombre], label=nombre)
        a.axhline(0, color="k", lw=1)
        a.set(xticks=range(1, 13), xlabel="Mes", title=f"Sesgo mensual {var} (fuente − INUMET)")
        a.legend()
    ax[0].set_ylabel("°C")
    fig.tight_layout(); fig.savefig(FIG / "temp_sesgo_mensual_comparado.png"); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    hro = hr_obs[hr_obs.index.year == 2025]
    ax[0].plot(hro.groupby(hro.index.hour).mean(), "o-", color="k", label="INUMET")
    for nombre in F:
        s = F[nombre]["rh"].reindex(hro.index)
        ax[0].plot(s.groupby(s.index.hour).mean(), "s-", color=COLORES[nombre], label=nombre)
    ax[0].set(xlabel="Hora local", ylabel="HR media (%)", title="Ciclo diurno de humedad (2025)"); ax[0].legend(fontsize=8)
    ws_obs = (viento.IntV.astype(float) * KT_A_KMH).dropna()
    wso = ws_obs[ws_obs.index.year == 2025]
    ax[1].plot(wso.groupby(wso.index.hour).mean(), "o-", color="k", label="INUMET (10 m)")
    for nombre in F:
        s = F[nombre]["ws"].reindex(wso.index)
        ax[1].plot(s.groupby(s.index.hour).mean(), "s-", color=COLORES[nombre], label=nombre)
    ax[1].set(xlabel="Hora local", ylabel="km/h", title="Ciclo diurno de viento (2025)"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "ciclo_diurno_hr_viento.png"); plt.close(fig)

    sect = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    ang = np.deg2rad(np.arange(0, 360, 45))
    fig = plt.figure(figsize=(6.5, 6.5)); a = fig.add_subplot(projection="polar")
    a.set_theta_zero_location("N"); a.set_theta_direction(-1)
    series = [("INUMET", R_full["Open-Meteo"]["wd"]["frec_inumet"])] + \
             [(n, R_full[n]["wd"]["frec_fuente"]) for n in ["Open-Meteo", "NASA Colonia"]]
    for k, (n, fr) in enumerate(series):
        a.bar(ang + (k - 1) * .2, pd.Series(fr).reindex(sect).fillna(0), width=.2, color=COLORES[n], alpha=.8, label=n)
    a.set_xticks(ang); a.set_xticklabels(sect); a.set_title("Frecuencia de dirección del viento (%)")
    a.legend(loc="lower right", bbox_to_anchor=(1.2, -0.1)); fig.tight_layout()
    fig.savefig(FIG / "viento_rosa_comparada.png"); plt.close(fig)

    fig, ax = plt.subplots(2, 1, figsize=(13, 7.5))
    dn, do = R_full["NASA Colonia"]["_dfp"], R_full["Open-Meteo"]["_dfp"]
    mn = dn.resample("MS").sum()[dn.resample("MS").o.count() >= 26]
    mo = do.resample("MS").sum().reindex(mn.index)
    for a, anios in [(ax[0], [2017, 2018, 2019]), (ax[1], [2024, 2025])]:
        sel = mn.index.year.isin(anios)
        xs = np.arange(sel.sum())
        a.bar(xs - .27, mn.o[sel], .27, color="k", label="INUMET")
        a.bar(xs, mn.m[sel], .27, color=COLORES["NASA Colonia"], label="NASA Colonia")
        a.bar(xs + .27, mo.m[sel], .27, color=COLORES["Open-Meteo"], label="Open-Meteo")
        a.set_xticks(xs); a.set_xticklabels([i.strftime("%m-%y") for i in mn.index[sel]], rotation=90, fontsize=7)
        a.set_ylabel("mm/mes"); a.legend()
    ax[0].set_title("Precipitación mensual")
    fig.tight_layout(); fig.savefig(FIG / "pp_mensual_comparada.png"); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(11, 5))
    lim = [0, 150]
    for nombre, mk in [("Open-Meteo", "o"), ("NASA Colonia", "s")]:
        d = R_full[nombre]["_dfp"]
        ax[0].scatter(d.o, d.m, s=7, alpha=.45, marker=mk, color=COLORES[nombre],
                      label=f"{nombre} r={d.o.corr(d.m):.2f}")
        m = d.resample("MS").sum()[d.resample("MS").o.count() >= 26]
        ax[1].scatter(m.o, m.m, s=22, marker=mk, color=COLORES[nombre], label=f"{nombre} r={m.o.corr(m.m):.2f}")
    ax[0].plot(lim, lim, "k--", lw=1); ax[0].set(xlim=lim, ylim=lim, xlabel="INUMET (mm/día)", ylabel="Fuente (mm/día)",
                                                 title="Precipitación diaria (07-07 h)")
    ax[1].plot([0, 420], [0, 420], "k--", lw=1); ax[1].set(xlim=[0, 420], ylim=[0, 420], xlabel="INUMET (mm/mes)",
                                                           ylabel="Fuente (mm/mes)", title="Precipitación mensual")
    ax[0].legend(); ax[1].legend()
    fig.tight_layout(); fig.savefig(FIG / "pp_dispersion_comparada.png"); plt.close(fig)


def figura_resumen(tabla):
    vars_ = list(tabla.index)
    fig, ax = plt.subplots(1, len(vars_), figsize=(3.1 * len(vars_), 3.8))
    for a, v in zip(ax, vars_):
        fila = tabla.loc[v].dropna()
        a.bar(range(len(fila)), fila.values, color=[COLORES[n] for n in fila.index])
        a.set_xticks(range(len(fila))); a.set_xticklabels([n.replace(" (San José)", "\n(San José)") for n in fila.index],
                                                          rotation=30, ha="right", fontsize=7)
        a.set_title(v, fontsize=9)
    fig.suptitle("Error medio absoluto vs INUMET Colonia, año 2025 (menor = mejor)")
    fig.tight_layout(); fig.savefig(FIG / "resumen_mae_2025.png"); plt.close(fig)


# ----------------------------------------------------------------- main
def limpiar(R):
    if isinstance(R, dict):
        return {str(k): limpiar(v) for k, v in R.items() if not str(k).startswith("_")}
    if isinstance(R, list):
        return [limpiar(v) for v in R]
    return R


def main():
    F, factor = fuentes()
    txtn, hr_obs, viento, pp = cargar_inumet("Colonia")
    hr_obs = hr_obs[hr_obs.index.hour.isin(HORAS_OBS)]
    viento = viento[viento.index.hour.isin(HORAS_OBS)]

    R = {"factor_viento_2m_a_10m": round(factor, 3)}
    full = {n: evaluar(F[n], txtn, hr_obs, viento, pp, ANIOS) for n in ["Open-Meteo", "NASA Colonia"]}
    R["periodo_completo"] = full
    R["correccion_temperatura"] = {n: correccion_sesgo(F[n], txtn) for n in ["Open-Meteo", "NASA Colonia"]}
    R["nasa_pp_dia_calendario"] = metricas(pp.mm, F["NASA Colonia"]["pp_dia_nasa"], (1, 5))

    # Cara a cara 2025: las tres fuentes sobre exactamente los mismos días/horas
    R["cara_a_cara_2025"] = {n: evaluar(F[n], txtn, hr_obs, viento, pp, [2025], extendido=False) for n in F}

    # Diagnóstico: el archivo del usuario contra la estación San José (de donde son sus coordenadas)
    t_sj, hr_sj, v_sj, _ = cargar_inumet("San José", "Precipitación diaria 2.xlsx")
    hr_sj = hr_sj[hr_sj.index.hour.isin(HORAS_OBS)]
    v_sj = v_sj[v_sj.index.hour.isin(HORAS_OBS)]
    R["archivo_vs_estacion_san_jose_2025"] = evaluar(F["NASA archivo (San José)"], t_sj, hr_sj, v_sj, None, [2025],
                                                     extendido=False)

    figuras(F, txtn, hr_obs, viento, full)
    c = R["cara_a_cara_2025"]
    tabla = pd.DataFrame({n: {"TX (°C)": c[n]["tx"]["global"]["mae"], "TN (°C)": c[n]["tn"]["global"]["mae"],
                              "HR horaria (%)": c[n]["rh"]["global"]["mae"],
                              "Viento horario (km/h)": c[n]["ws"]["global"]["mae"],
                              "Dirección (mediana °)": c[n]["wd"]["mediana_error"],
                              "Lluvia diaria (mm)": c[n].get("pp", {}).get("diaria", {}).get("mae", np.nan)}
                          for n in F})
    figura_resumen(tabla)

    (OUT / "metricas_nasa.json").write_text(json.dumps(limpiar(R), ensure_ascii=False, indent=1, default=str))
    print(tabla.round(2).to_string())


if __name__ == "__main__":
    main()
