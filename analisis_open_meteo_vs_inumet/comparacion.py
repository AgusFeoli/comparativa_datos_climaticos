"""Comparación Open-Meteo vs INUMET - Estación Colonia (Aeropuerto Laguna de los Patos).

Uso: python comparacion.py   (requiere pandas, numpy, openpyxl, scipy, matplotlib)
Genera figuras en ./figuras y métricas en ./metricas.json
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
FIG = OUT / "figuras"
FIG.mkdir(exist_ok=True)
OM_CSV = BASE / "open-meteo-34.41S57.74W25m.csv"
INUMET_XLSX = BASE / "1793295547972-CLIM-2026-0000193.xlsx"
ESTACION = "Colonia"
KT_A_KMH = 1.852
HORAS_OBS = range(7, 20)
ESTACIONES_DEL_ANO = {12: "DEF", 1: "DEF", 2: "DEF", 3: "MAM", 4: "MAM", 5: "MAM",
                      6: "JJA", 7: "JJA", 8: "JJA", 9: "SON", 10: "SON", 11: "SON"}


# ----------------------------------------------------------------- carga
def _col_estacion(fila, nombre):
    return [i for i, v in enumerate(fila) if v and str(v).strip() == nombre][0]


def _pad(r, n):
    return list(r) + [None] * max(0, n - len(r))


def cargar_inumet(estacion=ESTACION, archivo_pp="Precipitación diaria.xlsx"):
    wb = openpyxl.load_workbook(INUMET_XLSX, read_only=True, data_only=True)

    rows = list(wb["TxTn"].iter_rows(values_only=True))
    i = [k for k, r in enumerate(rows) if r and r[0] == "Fecha"][0]
    c = _col_estacion(rows[i - 1], estacion)
    txtn = pd.DataFrame([(r[0], *_pad(r, c + 2)[c:c + 2]) for r in rows[i + 1:] if r and r[0] is not None],
                        columns=["fecha", "TX", "TN"]).set_index("fecha")

    rows = list(wb["HR"].iter_rows(values_only=True))
    i = [k for k, r in enumerate(rows) if r and r[0] == "Fecha/hora"][0]
    c = _col_estacion(rows[i], estacion)
    hr = pd.DataFrame([(r[0], _pad(r, c + 1)[c]) for r in rows[i + 1:] if r and r[0] is not None],
                      columns=["fecha", "HR"]).set_index("fecha").HR.dropna()

    rows = list(wb["Viento"].iter_rows(values_only=True))
    i = [k for k, r in enumerate(rows) if r and r[0] == "Fecha"][0]
    c = _col_estacion(rows[i - 1], estacion)
    viento = pd.DataFrame([(r[0], *_pad(r, c + 2)[c:c + 2]) for r in rows[i + 1:] if r and r[0] is not None],
                          columns=["fecha", "DirV", "IntV"]).set_index("fecha")

    pp = []
    for periodo in ["2017-2019", "2024-2025"]:
        wb2 = openpyxl.load_workbook(BASE / periodo / archivo_pp, read_only=True, data_only=True)
        rows = list(wb2[estacion].iter_rows(values_only=True))
        pp.append(pd.DataFrame([r[:5] for r in rows[1:]], columns=list(rows[0])[:5]))
    pp = pd.concat(pp)
    pp["traza"] = pp["[mm]"].astype(str).str.upper().eq("TRAZA")
    pp["mm"] = pd.to_numeric(pp["[mm]"].where(~pp.traza, "0"), errors="coerce")
    pp = pp.set_index("Fecha")[["mm", "traza"]].dropna(subset=["mm"])
    return txtn, hr, viento, pp


def cargar_open_meteo():
    with open(OM_CSV, encoding="utf-8") as f:
        lineas = f.read().splitlines()
    meta = dict(zip(lineas[0].split(","), lineas[1].split(",")))
    vacias = [k for k, l in enumerate(lineas) if l.strip() == ""]
    h = pd.read_csv(OM_CSV, skiprows=vacias[0] + 1, nrows=vacias[1] - vacias[0] - 2, parse_dates=["time"])
    d = pd.read_csv(OM_CSV, skiprows=vacias[1] + 1, parse_dates=["time"])
    return meta, h.set_index("time"), d.set_index("time")


# ----------------------------------------------------------------- métricas
def anio(idx):
    return idx.year


def metricas(obs, mod, tolerancias=()):
    df = pd.concat([obs.rename("o"), mod.rename("m")], axis=1, sort=True).dropna()
    e = df.m - df.o
    r = {"n": int(len(df)), "media_inumet": df.o.mean(), "media_om": df.m.mean(),
         "sesgo": e.mean(), "mae": e.abs().mean(), "rmse": float(np.sqrt((e ** 2).mean())),
         "r": df.o.corr(df.m), "p95_err_abs": e.abs().quantile(0.95), "max_err_abs": e.abs().max()}
    for t in tolerancias:
        r[f"pct_dentro_{t}"] = 100 * (e.abs() <= t).mean()
    return {k: (round(float(v), 3) if not isinstance(v, int) else v) for k, v in r.items()}


def por_grupo(obs, mod, grupos, tol=()):
    df = pd.concat([obs.rename("o"), mod.rename("m")], axis=1, sort=True).dropna()
    g = grupos(df.index)
    return {str(k): metricas(sub.o, sub.m, tol) for k, sub in df.groupby(g)}


def periodo(idx):
    return np.where(idx.year <= 2019, "2017-2019", "2024-2025")


def estacion_ano(idx):
    return idx.month.map(ESTACIONES_DEL_ANO)


def contingencia(obs, mod, umbral):
    o, m = obs >= umbral, mod >= umbral
    a, b, c, d = (o & m).sum(), (~o & m).sum(), (o & ~m).sum(), (~o & ~m).sum()
    return {"umbral_mm": umbral, "dias_inumet": int(o.sum()), "dias_om": int(m.sum()),
            "aciertos": int(a), "falsas_alarmas": int(b), "no_detectados": int(c),
            "POD": round(a / (a + c), 3) if a + c else None,
            "FAR": round(b / (a + b), 3) if a + b else None,
            "CSI": round(a / (a + b + c), 3) if a + b + c else None,
            "sesgo_frecuencia": round((a + b) / (a + c), 3) if a + c else None,
            "pct_acierto_total": round(100 * (a + d) / len(o), 1)}


def dif_angular(a, b):
    return (b - a + 180) % 360 - 180


def sector8(deg):
    nombres = np.array(["N", "NE", "E", "SE", "S", "SO", "O", "NO"])
    return nombres[(((deg % 360) + 22.5) // 45).astype(int) % 8]


# ----------------------------------------------------------------- análisis
def main():
    meta, h, d = cargar_open_meteo()
    txtn, hr_obs, viento, pp = cargar_inumet()
    # La estación observa en horario 07-19 h; las pocas lecturas fuera de ese rango se descartan
    hr_obs = hr_obs[hr_obs.index.hour.isin(HORAS_OBS)]
    viento = viento[viento.index.hour.isin(HORAS_OBS)]
    R = {"open_meteo_punto": meta}

    # --- Temperatura máx/mín diaria (día calendario local)
    T = h["temperature_2m (°C)"]
    om_tx = T.resample("D").max()
    om_tn = T.resample("D").min()
    tol = (1, 2, 3)
    R["TX"] = {"global": metricas(txtn.TX, om_tx, tol),
               "estacion": por_grupo(txtn.TX, om_tx, estacion_ano, tol),
               "periodo": por_grupo(txtn.TX, om_tx, periodo, tol),
               "anio": por_grupo(txtn.TX, om_tx, anio, tol)}
    R["TN"] = {"global": metricas(txtn.TN, om_tn, tol),
               "estacion": por_grupo(txtn.TN, om_tn, estacion_ano, tol),
               "periodo": por_grupo(txtn.TN, om_tn, periodo, tol),
               "anio": por_grupo(txtn.TN, om_tn, anio, tol)}

    # Corrección de sesgo mensual: calibrada en 2017-2019, validada en 2024-2025
    corr = {}
    for var, om in [("TX", om_tx), ("TN", om_tn)]:
        df = pd.concat([txtn[var].rename("o"), om.rename("m")], axis=1, sort=True).dropna()
        cal, val = df[df.index.year <= 2019], df[df.index.year >= 2024]
        sesgo_mes = (cal.m - cal.o).groupby(cal.index.month).mean()
        val_corr = val.m - val.index.month.map(sesgo_mes).values
        corr[var] = {"sesgo_mensual_2017_2019": sesgo_mes.round(2).to_dict(),
                     "validacion_2024_2025_sin_corregir": metricas(val.o, val.m, tol),
                     "validacion_2024_2025_corregido": metricas(val.o, val_corr, tol)}
    R["correccion_temperatura"] = corr

    # Extremos
    df = pd.concat([txtn, om_tx.rename("omTX"), om_tn.rename("omTN")], axis=1, sort=True).dropna()
    R["extremos"] = {
        "dias_TX>=35": {"inumet": int((df.TX >= 35).sum()), "om": int((df.omTX >= 35).sum()),
                        "coinciden": int(((df.TX >= 35) & (df.omTX >= 35)).sum())},
        "dias_TX>=30": {"inumet": int((df.TX >= 30).sum()), "om": int((df.omTX >= 30).sum()),
                        "coinciden": int(((df.TX >= 30) & (df.omTX >= 30)).sum())},
        "dias_TN<=0 (helada)": {"inumet": int((df.TN <= 0).sum()), "om": int((df.omTN <= 0).sum()),
                               "coinciden": int(((df.TN <= 0) & (df.omTN <= 0)).sum())},
        "dias_TN<=3": {"inumet": int((df.TN <= 3).sum()), "om": int((df.omTN <= 3).sum()),
                       "coinciden": int(((df.TN <= 3) & (df.omTN <= 3)).sum())},
        "TX_max_absoluta": {"inumet": float(df.TX.max()), "om": float(df.omTX.max())},
        "TN_min_absoluta": {"inumet": float(df.TN.min()), "om": float(df.omTN.min())},
    }
    q = [0.01, 0.05, 0.5, 0.95, 0.99]
    R["percentiles_temp"] = {"TX_inumet": df.TX.quantile(q).round(1).to_dict(),
                             "TX_om": df.omTX.quantile(q).round(1).to_dict(),
                             "TN_inumet": df.TN.quantile(q).round(1).to_dict(),
                             "TN_om": df.omTN.quantile(q).round(1).to_dict()}

    # --- Humedad relativa horaria (INUMET observa 07-19 h local)
    RH = h["relative_humidity_2m (%)"]
    R["HR"] = {"global": metricas(hr_obs, RH, (5, 10, 15)),
               "estacion": por_grupo(hr_obs, RH, estacion_ano, (5, 10, 15)),
               "periodo": por_grupo(hr_obs, RH, periodo, (5, 10, 15)),
               "anio": por_grupo(hr_obs, RH, anio, (5, 10, 15)),
               "hora": por_grupo(hr_obs, RH, lambda i: i.hour, (5, 10, 15))}
    hr_d_obs = hr_obs.resample("D").mean()[hr_obs.resample("D").count() >= 10]
    hr_d_om = RH[RH.index.hour.isin(range(7, 20))].resample("D").mean()
    R["HR"]["media_diurna_diaria"] = metricas(hr_d_obs, hr_d_om, (5, 10))

    # --- Viento
    ws_obs = viento.IntV.astype(float) * KT_A_KMH
    WS = h["wind_speed_10m (km/h)"]
    WD = h["wind_direction_10m (°)"]
    R["viento_vel"] = {"global": metricas(ws_obs, WS, (5, 10)),
                       "estacion": por_grupo(ws_obs, WS, estacion_ano, (5, 10)),
                       "periodo": por_grupo(ws_obs, WS, periodo, (5, 10)),
                       "anio": por_grupo(ws_obs, WS, anio, (5, 10)),
                       "hora": por_grupo(ws_obs, WS, lambda i: i.hour, (5, 10))}
    ws_d_obs = ws_obs.dropna().resample("D").mean()[ws_obs.dropna().resample("D").count() >= 10]
    ws_d_om = WS[WS.index.hour.isin(range(7, 20))].resample("D").mean()
    R["viento_vel"]["media_diurna_diaria"] = metricas(ws_d_obs, ws_d_om, (3, 5))
    dfw = pd.concat([ws_obs.rename("o"), WS.rename("m")], axis=1, sort=True).dropna()
    R["viento_vel"]["percentiles"] = {"inumet": dfw.o.quantile([.5, .9, .99]).round(1).to_dict(),
                                      "om": dfw.m.quantile([.5, .9, .99]).round(1).to_dict()}

    dir_obs = pd.to_numeric(viento.DirV, errors="coerce")
    dfd = pd.concat([dir_obs.rename("o"), WD.rename("m"), ws_obs.rename("vo")], axis=1, sort=True).dropna()
    dfd = dfd[dfd.vo >= 2 * KT_A_KMH]  # sin calmas
    dd_err = dif_angular(dfd.o, dfd.m)
    R["viento_dir"] = {"n": int(len(dfd)), "error_medio_abs_grados": round(float(dd_err.abs().mean()), 1),
                       "mediana_error_abs": round(float(dd_err.abs().median()), 1),
                       "pct_dentro_45": round(float(100 * (dd_err.abs() <= 45).mean()), 1),
                       "pct_dentro_90": round(float(100 * (dd_err.abs() <= 90).mean()), 1),
                       "pct_mismo_sector8": round(float(100 * (sector8(dfd.o.values) == sector8(dfd.m.values)).mean()), 1),
                       "frec_sector_inumet": (pd.Series(sector8(dfd.o.values)).value_counts(normalize=True) * 100).round(1).to_dict(),
                       "frec_sector_om": (pd.Series(sector8(dfd.m.values)).value_counts(normalize=True) * 100).round(1).to_dict()}

    # --- Precipitación (INUMET: 24 h de 07 h del día D a 07 h del día D+1, rotulada D)
    P = h["precipitation (mm)"]
    om_pp = P.shift(-8).resample("D").sum(min_count=24)  # hora t acumula (t-1,t] -> ventana 07-07
    om_pp = om_pp.round(1)
    dfp = pd.concat([pp.mm.rename("o"), om_pp.rename("m")], axis=1, sort=True).dropna()
    R["PP_diaria"] = {"global": metricas(dfp.o, dfp.m, (1, 5)),
                      "spearman": round(float(dfp.o.corr(dfp.m, method="spearman")), 3),
                      "contingencia": [contingencia(dfp.o, dfp.m, u) for u in (0.1, 1, 5, 10, 20, 50)],
                      "dias_con_traza_inumet": int(pp.traza.sum())}
    # mismo-día-calendario (para quien use la serie diaria de Open-Meteo sin ajustar)
    om_pp_cal = P.resample("D").sum()
    dfc = pd.concat([pp.mm.rename("o"), om_pp_cal.rename("m")], axis=1, sort=True).dropna()
    R["PP_diaria_sin_alinear"] = {"r": round(float(dfc.o.corr(dfc.m)), 3),
                                  "CSI_1mm": contingencia(dfc.o, dfc.m, 1)["CSI"]}
    # tolerancia +-1 día
    o1 = dfp.o >= 1
    m_win = (dfp.m.shift(1).fillna(0).ge(1) | dfp.m.ge(1) | dfp.m.shift(-1).fillna(0).ge(1))
    R["PP_diaria"]["POD_1mm_tolerancia_1dia"] = round(float((o1 & m_win).sum() / o1.sum()), 3)

    for nombre, regla in [("PP_semanal", "W"), ("PP_mensual", "MS")]:
        g = dfp.resample(regla)
        cnt = g.o.count()
        agg = g.sum()[cnt >= (6 if regla == "W" else 26)]
        agg = agg[agg.index.year.isin([2017, 2018, 2019, 2024, 2025])]
        e = agg.m - agg.o
        R[nombre] = {**metricas(agg.o, agg.m),
                     "sesgo_pct": round(float(100 * e.sum() / agg.o.sum()), 1),
                     "pct_dentro_20pct_o_10mm": round(float(100 * ((e.abs() <= np.maximum(0.2 * agg.o, 10)).mean())), 1)}
        if regla == "MS":
            mensual = agg
    anual = dfp.groupby(dfp.index.year).agg(o=("o", "sum"), m=("m", "sum"), dias=("o", "count"))
    anual["dif_pct"] = (100 * (anual.m - anual.o) / anual.o).round(1)
    R["PP_anual"] = anual.round(1).reset_index().rename(columns={"index": "año"}).to_dict(orient="records")
    clim = dfp.groupby(dfp.index.month)[["o", "m"]].sum() / dfp.groupby(dfp.index.year).ngroups
    R["PP_climatologia_mensual_media"] = clim.round(1).to_dict()
    top = dfp.sort_values("o", ascending=False).head(15)
    R["PP_top15_inumet"] = [{"fecha": str(i.date()), "inumet": float(r.o), "om": float(r.m)} for i, r in top.iterrows()]

    (OUT / "metricas.json").write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str))

    # ----------------------------------------------------------------- figuras
    plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": .3})

    fig, ax = plt.subplots(1, 2, figsize=(11, 5))
    for a, var, om, col in [(ax[0], "TX", om_tx, "tab:red"), (ax[1], "TN", om_tn, "tab:blue")]:
        x = pd.concat([txtn[var].rename("o"), om.rename("m")], axis=1, sort=True).dropna()
        a.scatter(x.o, x.m, s=5, alpha=.4, c=col)
        lim = [x.min().min() - 1, x.max().max() + 1]
        a.plot(lim, lim, "k--", lw=1)
        a.set(xlim=lim, ylim=lim, xlabel=f"INUMET {var} (°C)", ylabel=f"Open-Meteo {var} (°C)",
              title=f"{var} diaria  r={x.o.corr(x.m):.3f}  MAE={(x.m - x.o).abs().mean():.2f} °C")
    fig.tight_layout(); fig.savefig(FIG / "temp_dispersion.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    for var, om, col in [("TX", om_tx, "tab:red"), ("TN", om_tn, "tab:blue")]:
        x = pd.concat([txtn[var].rename("o"), om.rename("m")], axis=1, sort=True).dropna()
        b = (x.m - x.o).groupby(x.index.month)
        ax.errorbar(b.mean().index, b.mean(), yerr=b.std(), marker="o", capsize=3, color=col,
                    label=f"{var} (media ± desvío)")
    ax.axhline(0, color="k", lw=1)
    ax.set(xticks=range(1, 13), xlabel="Mes", ylabel="Open-Meteo − INUMET (°C)",
           title="Sesgo mensual de la temperatura")
    ax.legend(); fig.tight_layout(); fig.savefig(FIG / "temp_sesgo_mensual.png"); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    x = pd.concat([hr_obs.rename("o"), RH.rename("m")], axis=1, sort=True).dropna()
    ax[0].plot(x.groupby(x.index.hour).o.mean(), "o-", label="INUMET")
    ax[0].plot(x.groupby(x.index.hour).m.mean(), "s-", label="Open-Meteo")
    ax[0].set(xlabel="Hora local", ylabel="HR media (%)", title="Ciclo diurno de humedad relativa"); ax[0].legend()
    ax[1].hist2d(x.o, x.m, bins=40, cmap="viridis", cmin=1)
    ax[1].plot([20, 100], [20, 100], "w--")
    ax[1].set(xlabel="INUMET HR (%)", ylabel="Open-Meteo HR (%)", title=f"HR horaria r={x.o.corr(x.m):.3f}")
    fig.tight_layout(); fig.savefig(FIG / "humedad.png"); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    ax[0].plot(dfw.groupby(dfw.index.hour).o.mean(), "o-", label="INUMET")
    ax[0].plot(dfw.groupby(dfw.index.hour).m.mean(), "s-", label="Open-Meteo")
    ax[0].set(xlabel="Hora local", ylabel="km/h", title="Velocidad media del viento por hora"); ax[0].legend()
    bins = (np.arange(0, 32, 2) - 0.5) * KT_A_KMH  # INUMET reporta nudos enteros
    ax[1].hist(dfw.o, bins, alpha=.6, density=True, label="INUMET")
    ax[1].hist(dfw.m, bins, alpha=.6, density=True, label="Open-Meteo")
    ax[1].set(xlabel="km/h", ylabel="frecuencia", title="Distribución de velocidad"); ax[1].legend()
    fig.tight_layout(); fig.savefig(FIG / "viento_velocidad.png"); plt.close(fig)

    sect = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    fo = pd.Series(R["viento_dir"]["frec_sector_inumet"]).reindex(sect).fillna(0)
    fm = pd.Series(R["viento_dir"]["frec_sector_om"]).reindex(sect).fillna(0)
    ang = np.deg2rad(np.arange(0, 360, 45))
    fig = plt.figure(figsize=(6, 6)); a = fig.add_subplot(projection="polar")
    a.set_theta_zero_location("N"); a.set_theta_direction(-1)
    a.bar(ang - .12, fo, width=.24, label="INUMET", alpha=.8)
    a.bar(ang + .12, fm, width=.24, label="Open-Meteo", alpha=.8)
    a.set_xticks(ang); a.set_xticklabels(sect); a.set_title("Frecuencia de dirección del viento (%)")
    a.legend(loc="lower right", bbox_to_anchor=(1.15, -0.1)); fig.tight_layout(); fig.savefig(FIG / "viento_rosa.png"); plt.close(fig)

    fig, ax = plt.subplots(2, 1, figsize=(12, 7))
    for a, años in [(ax[0], [2017, 2018, 2019]), (ax[1], [2024, 2025])]:
        sub = mensual[mensual.index.year.isin(años)]
        xs = np.arange(len(sub))
        a.bar(xs - .2, sub.o, .4, label="INUMET"); a.bar(xs + .2, sub.m, .4, label="Open-Meteo")
        a.set_xticks(xs); a.set_xticklabels([i.strftime("%m-%y") for i in sub.index], rotation=90, fontsize=7)
        a.set_ylabel("mm/mes"); a.legend()
    ax[0].set_title("Precipitación mensual (meses con ≥26 días observados)")
    fig.tight_layout(); fig.savefig(FIG / "pp_mensual.png"); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(11, 5))
    ax[0].scatter(dfp.o, dfp.m, s=6, alpha=.5)
    lim = [0, max(dfp.o.max(), dfp.m.max()) + 5]
    ax[0].plot(lim, lim, "k--", lw=1)
    ax[0].set(xlim=lim, ylim=lim, xlabel="INUMET (mm/día)", ylabel="Open-Meteo (mm/día)",
              title=f"Precipitación diaria r={dfp.o.corr(dfp.m):.2f}")
    ax[1].scatter(mensual.o, mensual.m, s=20)
    lim = [0, max(mensual.o.max(), mensual.m.max()) + 10]
    ax[1].plot(lim, lim, "k--", lw=1)
    ax[1].set(xlim=lim, ylim=lim, xlabel="INUMET (mm/mes)", ylabel="Open-Meteo (mm/mes)",
              title=f"Precipitación mensual r={mensual.o.corr(mensual.m):.2f}")
    fig.tight_layout(); fig.savefig(FIG / "pp_dispersion.png"); plt.close(fig)

    print(json.dumps(R, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
