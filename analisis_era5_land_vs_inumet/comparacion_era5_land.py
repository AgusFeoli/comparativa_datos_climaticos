"""Comparación ERA5-Land (Copernicus) vs INUMET - Estación Colonia, y cara a cara con Open-Meteo y NASA POWER.

Primero correr descargar_era5_land.py. Uso: python comparacion_era5_land.py
"""
import json
import sys
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
sys.path.insert(0, str(BASE / "analisis_open_meteo_vs_inumet"))
sys.path.insert(0, str(BASE / "analisis_nasa_vs_inumet"))
from comparacion import HORAS_OBS, KT_A_KMH, cargar_inumet, metricas  # noqa: E402
from comparacion_nasa import ANIOS, correccion_sesgo, evaluar, fuentes, limpiar, pp_07_07  # noqa: E402

FIG = OUT / "figuras"
FIG.mkdir(exist_ok=True)
DATOS = OUT / "datos_era5_land"
COLORES = {"INUMET": "k", "Open-Meteo": "tab:orange", "NASA Colonia": "tab:green", "ERA5-Land": "tab:blue"}
ORDEN = ["Open-Meteo", "ERA5-Land", "NASA Colonia"]


def humedad_relativa(t_c, td_c):
    """Magnus-Tetens (Alduchov y Eskridge, 1996)."""
    es = lambda x: np.exp(17.625 * x / (243.04 + x))  # noqa: E731
    return (100 * es(td_c) / es(t_c)).clip(upper=100)


def cargar_era5_land():
    partes = []
    for z in sorted(DATOS.glob("*.zip")):
        with zipfile.ZipFile(z) as zf:
            dfs = [pd.read_csv(zf.open(n), parse_dates=["valid_time"]).set_index("valid_time")
                   for n in zf.namelist() if n.endswith(".csv")]
        meta = dfs[0][["latitude", "longitude"]].iloc[0].round(3).to_dict()
        partes.append(pd.concat([d.drop(columns=["latitude", "longitude"]) for d in dfs], axis=1))
    h = pd.concat(partes).sort_index()
    h.index = h.index - pd.Timedelta(hours=3)  # UTC -> hora local Uruguay
    t = h.t2m - 273.15
    td = h.d2m - 273.15
    era = {"tx": t.resample("D").max(), "tn": t.resample("D").min(),
           "rh": humedad_relativa(t, td),
           "ws": np.hypot(h.u10, h.v10) * 3.6,
           "wd": (270 - np.degrees(np.arctan2(h.v10, h.u10))) % 360,
           # tp horario en m; la hora t acumula (t-1, t]
           "pp": pp_07_07(h.tp.clip(lower=0) * 1000, 8)}
    return era, meta, h


def diagnostico_alineacion(h, hr_obs, pp):
    t = h.t2m - 273.15
    rh = humedad_relativa(t, h.d2m - 273.15)
    out = {"hr_desfase": {}, "pp_desplazamiento": {}}
    for k in range(-3, 4):
        a = rh.shift(-k).reindex(hr_obs.index)
        out["hr_desfase"][k] = round(float(hr_obs.corr(a)), 3)
    tp = h.tp.clip(lower=0) * 1000
    for s in range(5, 12):
        m = tp.shift(-s).resample("D").sum(min_count=24).reindex(pp.index)
        ok = m.notna()
        out["pp_desplazamiento"][s] = round(float(pp.mm[ok].corr(m[ok])), 3)
    return out


def figuras(F, txtn, hr_obs, viento, full):
    plt.rcParams.update({"figure.dpi": 110, "axes.grid": True, "grid.alpha": .3})
    era = F["ERA5-Land"]

    fig, ax = plt.subplots(1, 2, figsize=(11, 5))
    for a, var, col in [(ax[0], "TX", "tab:red"), (ax[1], "TN", "tab:blue")]:
        x = pd.concat([txtn[var].rename("o"), era[var.lower()].rename("m")], axis=1, sort=True).dropna()
        a.scatter(x.o, x.m, s=5, alpha=.4, c=col)
        lim = [x.min().min() - 1, x.max().max() + 1]
        a.plot(lim, lim, "k--", lw=1)
        a.set(xlim=lim, ylim=lim, xlabel=f"INUMET {var} (°C)", ylabel=f"ERA5-Land {var} (°C)",
              title=f"ERA5-Land {var}  r={x.o.corr(x.m):.3f}  MAE={(x.m - x.o).abs().mean():.2f} °C")
    fig.tight_layout(); fig.savefig(FIG / "era5_temp_dispersion.png"); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for a, var in [(ax[0], "TX"), (ax[1], "TN")]:
        for n in ORDEN:
            x = pd.concat([txtn[var].rename("o"), F[n][var.lower()].rename("m")], axis=1, sort=True).dropna()
            x = x[x.index.year.isin(ANIOS)]
            b = (x.m - x.o).groupby(x.index.month).mean()
            a.plot(b.index, b.values, "o-", color=COLORES[n], label=n)
        a.axhline(0, color="k", lw=1)
        a.set(xticks=range(1, 13), xlabel="Mes", title=f"Sesgo mensual {var} (fuente − INUMET)"); a.legend()
    ax[0].set_ylabel("°C")
    fig.tight_layout(); fig.savefig(FIG / "temp_sesgo_mensual_3fuentes.png"); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    ax[0].plot(hr_obs.groupby(hr_obs.index.hour).mean(), "o-", color="k", label="INUMET")
    ws_obs = (viento.IntV.astype(float) * KT_A_KMH).dropna()
    ax[1].plot(ws_obs.groupby(ws_obs.index.hour).mean(), "o-", color="k", label="INUMET")
    for n in ORDEN:
        s = F[n]["rh"].reindex(hr_obs.index)
        ax[0].plot(s.groupby(s.index.hour).mean(), "s-", color=COLORES[n], label=n)
        s = F[n]["ws"].reindex(ws_obs.index)
        ax[1].plot(s.groupby(s.index.hour).mean(), "s-", color=COLORES[n], label=n)
    ax[0].set(xlabel="Hora local", ylabel="HR media (%)", title="Ciclo diurno de humedad (5 años)")
    ax[1].set(xlabel="Hora local", ylabel="km/h", title="Ciclo diurno de viento (5 años)")
    ax[0].legend(fontsize=8); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "ciclo_diurno_3fuentes.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    anual = pd.DataFrame({n: {int(a): v["m"] for a, v in full[n]["pp"]["anual"].items()} for n in ORDEN})
    anual.insert(0, "INUMET", {int(a): v["o"] for a, v in full["Open-Meteo"]["pp"]["anual"].items()})
    xs = np.arange(len(anual))
    for k, n in enumerate(anual.columns):
        ax.bar(xs + (k - 1.5) * .2, anual[n], .2, color=COLORES[n], label=n)
    ax.set_xticks(xs); ax.set_xticklabels(anual.index); ax.set_ylabel("mm/año"); ax.legend()
    ax.set_title("Lluvia anual por fuente")
    fig.tight_layout(); fig.savefig(FIG / "pp_anual_3fuentes.png"); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(11, 5))
    for n, mk in zip(ORDEN, ["o", "^", "s"]):
        d = full[n]["_dfp"]
        m = d.resample("MS").sum()[d.resample("MS").o.count() >= 26]
        ax[0].scatter(d.o, d.m, s=6, alpha=.4, marker=mk, color=COLORES[n], label=f"{n} r={d.o.corr(d.m):.2f}")
        ax[1].scatter(m.o, m.m, s=20, marker=mk, color=COLORES[n], label=f"{n} r={m.o.corr(m.m):.2f}")
    ax[0].plot([0, 150], [0, 150], "k--", lw=1); ax[0].set(xlim=[0, 150], ylim=[0, 150], xlabel="INUMET (mm/día)",
                                                          ylabel="Fuente (mm/día)", title="Lluvia diaria (07-07 h)")
    ax[1].plot([0, 420], [0, 420], "k--", lw=1); ax[1].set(xlim=[0, 420], ylim=[0, 420], xlabel="INUMET (mm/mes)",
                                                          ylabel="Fuente (mm/mes)", title="Lluvia mensual")
    ax[0].legend(fontsize=8); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "pp_dispersion_3fuentes.png"); plt.close(fig)


def figura_resumen(tabla):
    fig, ax = plt.subplots(1, len(tabla.index), figsize=(3.1 * len(tabla.index), 3.8))
    for a, v in zip(ax, tabla.index):
        fila = tabla.loc[v]
        a.bar(range(len(fila)), fila.values, color=[COLORES[n] for n in fila.index])
        a.set_xticks(range(len(fila))); a.set_xticklabels(fila.index, rotation=30, ha="right", fontsize=8)
        a.set_title(v, fontsize=9)
    fig.suptitle("Error medio absoluto vs INUMET Colonia, 2017-2019 + 2024-2025 (menor = mejor)")
    fig.tight_layout(); fig.savefig(FIG / "resumen_mae_3fuentes.png"); plt.close(fig)


def main():
    F, _ = fuentes()
    F.pop("NASA archivo (San José)")
    era, meta, h_era = cargar_era5_land()
    F["ERA5-Land"] = era
    txtn, hr_obs, viento, pp = cargar_inumet("Colonia")
    hr_obs = hr_obs[hr_obs.index.hour.isin(HORAS_OBS)]
    viento = viento[viento.index.hour.isin(HORAS_OBS)]

    R = {"punto_era5_land": meta, "alineacion": diagnostico_alineacion(h_era, hr_obs, pp)}
    full = {n: evaluar(F[n], txtn, hr_obs, viento, pp, ANIOS) for n in ORDEN}
    R["periodo_completo"] = full
    R["correccion_temperatura"] = {n: correccion_sesgo(F[n], txtn) for n in ORDEN}

    figuras(F, txtn, hr_obs, viento, full)
    tabla = pd.DataFrame({n: {"TX (°C)": full[n]["tx"]["global"]["mae"], "TN (°C)": full[n]["tn"]["global"]["mae"],
                              "HR horaria (%)": full[n]["rh"]["global"]["mae"],
                              "Viento horario (km/h)": full[n]["ws"]["global"]["mae"],
                              "Dirección (mediana °)": full[n]["wd"]["mediana_error"],
                              "Lluvia diaria (mm)": full[n]["pp"]["diaria"]["mae"],
                              "Lluvia mensual (mm)": full[n]["pp"]["mensual"]["mae"]} for n in ORDEN})
    figura_resumen(tabla)
    (OUT / "metricas_era5_land.json").write_text(json.dumps(limpiar(R), ensure_ascii=False, indent=1, default=str))
    print(json.dumps(R["alineacion"]), meta)
    print(tabla.round(2).to_string())


if __name__ == "__main__":
    main()
