"""¿Cuánto peso darle a la estación INUMET según lo lejos que esté?

Validación cruzada sobre las propias estaciones (como analisis.py): cada estación B se estima con las estaciones
vecinas y la grilla en B. Una "configuración" es (objetivo B, rango r): se hace de cuenta que las r estaciones más
cercanas a B no existen, de modo que la más cercana disponible queda a d1 km, la segunda a d2 y la tercera a d3.

Familias de pesos probadas (x_i = estación i, g = grilla en B):
  - fija:  w·x1 + (1−w)·g, con w constante (50/50 es w = 0.5).
  - exp:   igual, con w = exp(−d1/L).
  - idw:   la grilla entra como una "estación virtual" ubicada a L km:
             estimación = (Σ x_i/(d0^p + d_i^p) + g/L^p) / (Σ 1/(d0^p + d_i^p) + 1/L^p),  i = 1..k
           Con k = 1 y d0 = 0 el peso de la estación es w = 1/(1+(d1/L)^p). L = ∞ es IDW de estaciones sin grilla.
           d0 es una "pepita": la distancia que ya separa a una estación de un punto vecino aunque esté pegada.
Los parámetros se eligen minimizando el error con todas las estaciones menos B y se evalúan en B
(validación cruzada dejando una estación afuera). Sólo octubre–abril.

Salidas: tablas_peso_distancia.md, figuras/peso_vs_distancia.png, figuras/error_formula_vs_distancia.png
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import analisis as A
import datos

CACHE = datos.CACHE / "peso_distancia.pkl"
CACHE_CV = datos.CACHE / "peso_distancia_cv.pkl"
K_MAX = 3
D_CFG = {"tx": 150, "tn": 150, "hr": 150, "hr80": 150, "pp": 120}
LS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 170, 200, 250, 300, 400, np.inf]
WS = np.round(np.arange(0, 1.0001, 0.05), 2)
PS = {"conv": [0.5, 1, 1.5, 2, 3], "pp": [1, 1.5, 2]}
D0S = {"conv": [0, 5, 10, 20, 30, 50], "pp": [0, 10, 30]}
GRILLAS_PP = ["om", "om_nasa", "ens"]
BINS = {"conv": [0, 30, 60, 90, 120, 150], "pp": [0, 10, 20, 30, 45, 60, 80, 120]}
OBJETIVO = {"tx": "mae_D", "tn": "mae_D", "hr": "mae_D", "hr80": "mae_D", "pp": "rel_X"}
VARS = ["tx", "tn", "hr", "hr80", "pp"]

# Fórmula final por variable (k = 3 estaciones más cercanas con dato + Open-Meteo como estación virtual a L km).
# "om_qm" = Open-Meteo corregido por cuantiles mensuales contra la estación más cercana.
FORMULA = {"tx": {"p": 1, "L": 20, "grilla": "om_qm"},
           "tn": {"p": 1, "L": 30, "grilla": "om"},
           "hr": {"p": 1, "L": 30, "grilla": "om"},
           "hr80": {"p": 1, "L": 50, "grilla": "om"},
           "pp": {"p": 2, "L": 80, "grilla": "om"}}
# Recomendación anterior (peso fijo), para comparar.
REFERENCIA = {"tx": ("fija50", "om_qm"), "tn": ("fija50", "om"), "hr": ("fija50", "om"), "hr80": ("fija50", "om"),
              "pp": ("idw3_sin_grilla_p2", "om")}


def combinar(X, dist, g, p, L, d0=0.0):
    """Estaciones (filas de X, a `dist` km; dist puede variar por día) + grilla g como estación virtual a L km.
    Devuelve (estimación, peso total de las estaciones). Días sin ninguna estación: queda la grilla sola."""
    hay = ~np.isnan(X)
    dist = np.maximum(np.asarray(dist, float), 1.0)  # una estación a <1 km cuenta como a 1 km (evita 1/0)
    if dist.ndim == 1:
        dist = dist[:, None]
    with np.errstate(invalid="ignore"):
        W = np.where(hay, 1 / (d0 ** p + dist ** p), 0.0)
    wg = np.where(np.isnan(g), 0.0, 0.0 if np.isinf(L) else float(L) ** -p)
    g = np.nan_to_num(g)
    num, den = (W * np.where(hay, X, 0)).sum(0), W.sum(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (num + wg * g) / (den + wg), den / (den + wg)


# ----------------------------------------------------------------- datos por variable
def preparar(var, todo):
    meta, conv, mp, pp, gc, gp = todo
    if var == "pp":
        obs, coords, grids = pp, mp, gp
    else:
        obs, coords, grids = conv[var], meta, gc
    est = [s for s in obs.columns if obs[s].notna().sum() >= 200 and s in grids]
    idx = grids[est[0]]["om"].index
    idx = idx[idx.month.isin(A.MESES)]
    O = obs[est].reindex(idx)
    if var == "pp":
        G = {}
        for s in est:
            gs = A.series_grilla(grids[s], "pp")
            gs["om_nasa"] = (gs["om"] + gs["nasa"]) / 2
            G[s] = {g: gs[g].reindex(idx) for g in GRILLAS_PP}
    else:
        G = {s: grids[s]["om"][var].reindex(idx) for s in est}
    c = coords.loc[est]
    D = pd.DataFrame(datos.distancia_km(c.lat.values[:, None], c.lon.values[:, None],
                                        c.lat.values[None], c.lon.values[None]), est, est)
    return est, idx, O, G, D


def configuraciones(var, est, D):
    cfgs = []
    for b in est:
        don = D.loc[b].drop(b)
        don = don[(don > 2) & (don <= A.D_MAX[var])].sort_values()
        for r in range(len(don)):
            if don.iloc[r] > D_CFG[var]:
                break
            sel = don.iloc[r:r + K_MAX]
            cfgs.append({"objetivo": b, "rank": r, "donantes": list(sel.index), "dist": sel.values})
    return cfgs


def series_config(var, todo):
    """Por configuración: observado en B, estaciones donantes (k, T), distancias y grillas en B (series completas)."""
    est, idx, O, G, D = preparar(var, todo)
    gc = todo[4]
    for i, cfg in enumerate(configuraciones(var, est, D)):
        b, don = cfg["objetivo"], cfg["donantes"]
        if var == "pp":
            gs = {g: s.values for g, s in G[b].items()}
        else:
            a = don[0]
            gs = {"om": G[b].values,
                  "om_qm": A.mapeo_cuantiles(G[b], gc[a]["om"][var].reindex(idx), O[a]).values}
        yield i, cfg, idx, O[b].values, O[don].values.T, gs


def grupos(idx, escala):
    claves = np.asarray(A._grupo(idx, escala))
    u, cod = np.unique(claves, return_inverse=True)
    return cod, A._dias_por_grupo(escala).reindex(u).values


# ----------------------------------------------------------------- estimadores y métricas
def metodos(X, dist, G, ps, d0s):
    """Todas las estimaciones de una configuración. X: (k, T) estaciones; G: {tipo de grilla: (T,)}."""
    filas, est = [], []
    x1 = X[0]
    for gname, g in G.items():
        for w in WS:
            filas.append(("fija", 1, np.nan, np.nan, w, 0, gname, w))
            est.append(w * x1 + (1 - w) * g)
        for L in LS[:-1]:
            w = np.exp(-dist[0] / L)
            filas.append(("exp", 1, np.nan, L, np.nan, 0, gname, w))
            est.append(w * x1 + (1 - w) * g)
        for k in range(1, min(K_MAX, len(dist)) + 1):
            for p in ps:
                for d0 in d0s:
                    for L in LS:
                        if np.isinf(L) and (k == 1 or d0 > 0):
                            continue
                        e, w = combinar(X[:k], dist[:k], g, p, L, d0)
                        filas.append(("idw", k, p, L, np.nan, d0, gname, float(np.mean(w))))
                        est.append(e)
    cols = ["familia", "k", "p", "L", "w", "d0", "grilla", "peso_estaciones"]
    return pd.DataFrame(filas, columns=cols), np.vstack(est)


def puntuar(o, E, m, var, grp):
    err = E - o
    r = {"mae_D": np.abs(err).mean(1)}
    if var == "pp":
        r["rel_D"] = r["mae_D"] / o.mean()
        a, b = o >= A.UMBRAL_LLUVIA, E >= A.UMBRAL_LLUVIA
        r["csi_D"] = (a & b).sum(1) / np.maximum((a | b).sum(1), 1)
    for esc, (cod, completo) in grp.items():
        c = cod[m]
        n = np.bincount(c, minlength=len(completo))
        ok = np.flatnonzero(n >= 0.9 * completo)
        if len(ok) < 8:
            r[f"mae_{esc}"] = np.full(len(E), np.nan)
            if var == "pp":
                r[f"rel_{esc}"] = np.full(len(E), np.nan)
            continue
        H = (c[:, None] == ok[None]).astype(float)
        so, se = o @ H, E @ H
        if var != "pp":
            so, se = so / n[ok], se / n[ok]
        r[f"mae_{esc}"] = np.abs(se - so).mean(1)
        if var == "pp":
            r[f"rel_{esc}"] = r[f"mae_{esc}"] / so.mean()
    return r


def evaluar(var, todo):
    tipo = "pp" if var == "pp" else "conv"
    grp = None
    salida = []
    for i, cfg, idx, ob, X, gs in series_config(var, todo):
        grp = grp or {e: grupos(idx, e) for e in ("X", "M")}
        m = ~np.isnan(ob) & ~np.isnan(X[0])
        for g in gs.values():
            m &= ~np.isnan(g)
        if m.sum() < 60:
            continue
        tab, E = metodos(X[:, m], cfg["dist"], {k: v[m] for k, v in gs.items()}, PS[tipo], D0S[tipo])
        for k, v in puntuar(ob[m], E, m, var, grp).items():
            tab[k] = v
        tab["cfg"] = i
        tab["objetivo"] = cfg["objetivo"]
        tab["donantes"] = "|".join(map(str, cfg["donantes"]))
        tab["rank"] = cfg["rank"]
        for j in range(K_MAX):
            tab[f"d{j + 1}"] = cfg["dist"][j] if j < len(cfg["dist"]) else np.nan
        tab["n"] = int(m.sum())
        salida.append(tab)
    return pd.concat(salida, ignore_index=True)


# ----------------------------------------------------------------- ajuste y validación cruzada
CLAVE = ["familia", "k", "p", "L", "w", "d0", "grilla"]


def _id_metodo(df):
    return pd.Series([";".join(map(str, r)) for r in df[CLAVE].itertuples(index=False)], df.index)


def mejor_metodo(P, tramo, train):
    """Columna de P (configuración × método) con menor error medio, cada tramo de distancia pesa igual."""
    t = tramo[train]
    peso = 1 / t.map(t.value_counts())
    return (P[train].mul(peso, axis=0).sum() / peso.sum()).idxmin()


def _idw(k, p=None, d0=0, sin_grilla=False):
    def f(d):
        m = (d.familia == "idw") & (d.k == k) & (d.d0 == d0)
        if p is not None:
            m &= d.p == p
        return m & np.isinf(d.L) if sin_grilla else m
    return f


FAMILIAS = {
    "estacion": lambda d: (d.familia == "fija") & (d.w == 1.0),
    "grilla": lambda d: (d.familia == "fija") & (d.w == 0.0),
    "fija50": lambda d: (d.familia == "fija") & (d.w == 0.5),
    "fija_opt": lambda d: d.familia == "fija",
    "exp": lambda d: d.familia == "exp",
    "idw1": _idw(1),
    "idw1_p1": _idw(1, 1),
    "idw2_p1": _idw(2, 1),
    "idw3": _idw(3),
    "idw3_p1": _idw(3, 1),
    "idw3_p1.5": _idw(3, 1.5),
    "idw3_p2": _idw(3, 2),
    "idw3_pepita": lambda d: (d.familia == "idw") & (d.k == 3),
    "idw3_sin_grilla_p2": _idw(3, 2, sin_grilla=True),
}


def validacion_cruzada(df, var, familias=FAMILIAS):
    """Para cada estación objetivo B: elige el mejor método de la familia sin usar B, lo evalúa en B."""
    df = df.copy()
    df["mid"] = _id_metodo(df)
    info = df.drop_duplicates("cfg").set_index("cfg")
    info = info[info[OBJETIVO[var]].notna()]
    tramo = pd.cut(info.d1, BINS["pp" if var == "pp" else "conv"]).astype(str)
    dons = info.donantes.str.split("|")
    objetivos = info.objetivo.unique()
    train = {b: (info.objetivo != b) & ~dons.map(lambda l: str(b) in l) for b in objetivos}
    out, elegidos = [], []
    for fam, filtro in familias.items():
        for gname in df.grilla.unique():
            sub = df[filtro(df) & (df.grilla == gname) & df.cfg.isin(info.index)]
            if sub.empty:
                continue
            P = sub.pivot(index="cfg", columns="mid", values=OBJETIVO[var]).dropna()
            sub = sub.set_index(["cfg", "mid"])
            elegidos.append({"fam": fam, "grilla": gname, "objetivo": "TODOS",
                             "mid": mejor_metodo(P, tramo[P.index], pd.Series(True, P.index))})
            for b in objetivos:
                mejor = mejor_metodo(P, tramo[P.index], train[b][P.index])
                cfg_b = P.index[info.objetivo[P.index] == b]
                out.append(sub.loc[[(c, mejor) for c in cfg_b]].reset_index().assign(fam=fam))
                elegidos.append({"fam": fam, "grilla": gname, "objetivo": b, "mid": mejor})
    return pd.concat(out, ignore_index=True), pd.DataFrame(elegidos)


def resumen_cv(cv, var, metricas):
    bins = BINS["pp" if var == "pp" else "conv"]
    cv = cv.assign(tramo=pd.cut(cv.d1, bins))
    filas = []
    for (fam, g), x in cv.groupby(["fam", "grilla"]):
        fila = {"fam": fam, "grilla": g}
        for met in metricas:
            t = x.groupby("tramo", observed=False)[met].mean()
            for iv, v in t.items():
                fila[f"{met} {int(iv.left)}–{int(iv.right)}"] = v
            fila[f"{met} ponderado"] = t.mean()
        filas.append(fila)
    return pd.DataFrame(filas)


def bootstrap(cv, var, a, b, met, n=2000, semilla=0):
    """Diferencia media (a − b) ponderada por tramo, remuestreando estaciones objetivo. Devuelve media, IC 95 %,
    fracción de configuraciones en que a es mejor."""
    xa = cv[(cv.fam == a[0]) & (cv.grilla == a[1])].set_index("cfg")
    xb = cv[(cv.fam == b[0]) & (cv.grilla == b[1])].set_index("cfg")
    c = xa.index.intersection(xb.index)
    d = pd.DataFrame({"dif": xa.loc[c, met] - xb.loc[c, met], "objetivo": xa.loc[c, "objetivo"],
                      "tramo": pd.cut(xa.loc[c, "d1"], BINS["pp" if var == "pp" else "conv"]).astype(str)})
    if met == "csi_D":
        d["dif"] = -d.dif
    por_obj = {o: g for o, g in d.groupby("objetivo")}
    objs = np.array(list(por_obj))
    rng = np.random.default_rng(semilla)

    def estad(x):
        return x.groupby("tramo").dif.mean().mean()

    boot = [estad(pd.concat([por_obj[o] for o in rng.choice(objs, len(objs))])) for _ in range(n)]
    signo = -1 if met == "csi_D" else 1
    lo, hi = np.percentile(boot, [2.5, 97.5])
    ic = sorted((signo * lo, signo * hi))
    return signo * estad(d), ic[0], ic[1], float((d.dif < 0).mean()), len(d)


# ----------------------------------------------------------------- días sobre umbral
def conteos(var, todo, umbral, signo=1, d_max=120):
    """Error en el número de días por campaña (oct–abr) sobre/bajo un umbral, por método."""
    f = FORMULA[var]
    filas = []
    for i, cfg, idx, ob, X, gs in series_config(var, todo):
        if cfg["dist"][0] > d_max:
            continue
        cand = {"estacion": X[0], "fija50 om": 0.5 * X[0] + 0.5 * gs["om"],
                "fija50 om_qm": 0.5 * X[0] + 0.5 * gs["om_qm"],
                "formula": combinar(X, cfg["dist"], gs[f["grilla"]], f["p"], f["L"])[0]}
        m = ~np.isnan(ob) & ~np.isnan(X[0]) & ~np.isnan(gs["om_qm"])
        camp = np.where(idx.month >= 10, idx.year + 1, idx.year)[m]
        o = pd.Series(signo * ob[m] >= signo * umbral).groupby(camp)
        ok = o.count()[o.count() >= 150].index
        o = o.sum()[ok]
        for k, s in cand.items():
            e = pd.Series(signo * s[m] >= signo * umbral).groupby(camp).sum()[ok]
            filas.append({"cfg": i, "d1": cfg["dist"][0], "metodo": k, "dias_obs": o.mean(),
                          "sesgo": (e - o).mean(), "mae": (e - o).abs().mean()})
    return pd.DataFrame(filas)


# ----------------------------------------------------------------- figuras y tablas
NOMBRE_VAR = {"tx": "Temperatura máxima (°C)", "tn": "Temperatura mínima (°C)", "hr": "HR media diurna (%)",
              "hr80": "Fracción de horas diurnas con HR ≥ 80 %", "pp": "Lluvia: error relativo del total de 10 días"}


def peso_optimo_por_par(res, var, grilla):
    d = res[var]
    f = d[(d.familia == "fija") & (d.grilla == grilla)]
    return f.loc[f.groupby("cfg")[OBJETIVO[var]].idxmin(), ["cfg", "d1", "w"]]


def figura_pesos(res):
    fig, ax = plt.subplots(2, 2, figsize=(12, 9))
    dd = np.linspace(1, 150, 300)
    for a, var in zip(ax.flat, ["tx", "tn", "hr", "pp"]):
        f = FORMULA[var]
        b = peso_optimo_por_par(res, var, f["grilla"])
        bins = BINS["pp" if var == "pp" else "conv"]
        a.scatter(b.d1, b.w + np.random.default_rng(0).uniform(-0.012, 0.012, len(b)), s=10, color="k",
                  alpha=0.25 if var == "pp" else 0.5, label="peso óptimo de la estación en cada par")
        med = b.groupby(pd.cut(b.d1, bins), observed=True).w.median()
        a.plot([iv.mid for iv in med.index], med.values, "s--", color="tab:gray", label="mediana por tramo")
        a.plot(dd, 1 / (1 + (dd / f["L"]) ** f["p"]), color="tab:red", lw=2.5,
               label="fórmula elegida (caso de una sola estación)")
        a.axhline(0.5, color="tab:blue", ls=":", label="50/50 (recomendación anterior)")
        a.set_xlim(0, bins[-1])
        a.set_ylim(-0.03, 1.03)
        expo = "" if f["p"] == 1 else f"^{f['p']}"
        a.set_title(f"{NOMBRE_VAR[var].split(':')[0]} — curva roja: w = 1 / (1 + (d/{f['L']}){expo})", fontsize=10)
        a.set_xlabel("Distancia a la estación / pluviómetro más cercano (km)")
        a.set_ylabel("Peso de la estación (resto: Open-Meteo)")
        a.grid(alpha=0.3)
    ax.flat[0].legend(fontsize=7.5, loc="upper right")
    fig.suptitle("¿Cuánto pesa la estación según su distancia? Peso que minimiza el error en cada par de estaciones INUMET",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(A.FIG / "peso_vs_distancia.png", dpi=130)
    plt.close(fig)


def figura_error(cvs):
    fig, ax = plt.subplots(2, 2, figsize=(12, 9))
    estilos = [("estacion", "Estación / pluviómetro más cercano solo", "k", "-"),
               ("grilla", "Open-Meteo solo", "tab:blue", "--"),
               ("referencia", "Recomendación anterior (peso fijo)", "tab:orange", "-"),
               ("formula", "Fórmula según distancia (3 estaciones + Open-Meteo)", "tab:red", "-")]
    for a, var in zip(ax.flat, ["tx", "tn", "hr", "pp"]):
        cv = cvs[var]
        bins = BINS["pp" if var == "pp" else "conv"]
        centro = [(x + y) / 2 for x, y in zip(bins[:-1], bins[1:])]
        for clave, etq, color, ls in estilos:
            fam, g = _fam(var, clave)
            x = cv[(cv.fam == fam) & (cv.grilla == g)]
            t = x.groupby(pd.cut(x.d1, bins), observed=False)[OBJETIVO[var]].mean()
            a.plot(centro, t.values, "o" + ls, color=color, label=etq, lw=2, ms=4)
        a.set_title(NOMBRE_VAR[var], fontsize=10)
        a.set_xlabel("Distancia a la estación / pluviómetro más cercano (km)")
        a.set_ylabel("Error absoluto medio diario" if var != "pp" else "Error relativo")
        a.grid(alpha=0.3)
    ax.flat[0].legend(fontsize=8)
    fig.suptitle("Error en validación cruzada (cada estación estimada sin usarla para ajustar), octubre–abril",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(A.FIG / "error_formula_vs_distancia.png", dpi=130)
    plt.close(fig)


def _fam(var, clave):
    f = FORMULA[var]
    return {"estacion": ("estacion", f["grilla"]), "grilla": ("grilla", "om"),
            "referencia": REFERENCIA[var],
            "formula": (f"idw3_p{f['p']}", f["grilla"])}[clave]


def a_md(t, dec=2):
    cab = "| | " + " | ".join(map(str, t.columns)) + " |\n|---|" + "---:|" * len(t.columns) + "\n"
    filas = ["| " + str(i) + " | " + " | ".join("—" if pd.isna(v) else (v if isinstance(v, str) else f"{v:.{dec}f}")
                                              for v in r) + " |" for i, r in t.iterrows()]
    return cab + "\n".join(filas)


ETQ_FAM = {"estacion": "Estación más cercana sola", "grilla": "Grilla sola", "fija50": "50 % estación + 50 % grilla",
           "fija_opt": "Peso fijo óptimo", "exp": "Peso exp(−d/L)", "idw1": "1 estación + grilla, 1/(1+(d/L)^p)",
           "idw1_p1": "1 estación + grilla, p = 1", "idw2_p1": "2 estaciones + grilla, p = 1",
           "idw3": "3 estaciones + grilla, p libre", "idw3_p1": "3 estaciones + grilla, p = 1",
           "idw3_p1.5": "3 estaciones + grilla, p = 1.5", "idw3_p2": "3 estaciones + grilla, p = 2",
           "idw3_pepita": "3 estaciones + grilla, p y pepita d0 libres",
           "idw3_sin_grilla_p2": "IDW 3 estaciones (1/d²) sin grilla"}
ETQ_GRILLA = {"om": "Open-Meteo", "om_qm": "Open-Meteo corregido por cuantiles", "ens": "promedio 3 grillas",
              "om_nasa": "promedio Open-Meteo + NASA"}


def _parametros(mid):
    fam, k, p, L, w, d0, g = mid.split(";")
    if fam == "fija":
        return f"w = {float(w):.2f}"
    if fam == "exp":
        return f"L = {float(L):.0f} km"
    s = f"p = {float(p):g}, L = {'∞' if L == 'inf' else f'{float(L):.0f} km'}"
    return s + (f", d0 = {float(d0):.0f} km" if float(d0) > 0 else "")


def tabla_cv(cv, el, var, met, filas):
    r = resumen_cv(cv, var, [met])
    r = r.merge(el[el.objetivo == "TODOS"][["fam", "grilla", "mid"]], on=["fam", "grilla"])
    r = r.set_index(["fam", "grilla"]).loc[[f for f in filas if f in r.set_index(["fam", "grilla"]).index]]
    t = r[[c for c in r if c.startswith(met)]].copy()
    t.columns = [c.replace(met + " ", "").replace("ponderado", "promedio de tramos") for c in t.columns]
    t.insert(0, "parámetros (con todos los datos)", [_parametros(m) for m in r.mid])
    t.index = [f"{ETQ_FAM[f]} ({ETQ_GRILLA[g]})" for f, g in t.index]
    return t


def estabilidad(el, fam, grilla):
    e = el[(el.fam == fam) & (el.grilla == grilla) & (el.objetivo != "TODOS")]
    L = e.mid.str.split(";").str[3].astype(float)
    return f"L elegido en los {len(e)} pliegues: mediana {L.median():.0f} km, rango {L.min():.0f}–{L.max():.0f} km"


if __name__ == "__main__":
    todo = None
    if CACHE.exists():
        res = pd.read_pickle(CACHE)
    else:
        todo = A.cargar_todo()
        res = {}
        for v in VARS:
            res[v] = evaluar(v, todo)
            print(v, res[v].cfg.nunique(), "configuraciones", len(res[v]), "filas", flush=True)
        pd.to_pickle(res, CACHE)
    if CACHE_CV.exists():
        cvs = pd.read_pickle(CACHE_CV)
    else:
        cvs = {}
        for v in VARS:
            fams = FAMILIAS if v != "pp" else {k: f for k, f in FAMILIAS.items()
                                               if k not in ("idw3_pepita", "idw1", "idw3")}
            cvs[v] = validacion_cruzada(res[v], v, fams)
            print("validación cruzada", v, flush=True)
        pd.to_pickle(cvs, CACHE_CV)
    todo = todo or A.cargar_todo()

    figura_pesos(res)
    figura_error({v: cvs[v][0] for v in VARS})

    out = ["# Tablas del análisis de peso según la distancia (peso_distancia.py)\n",
           "Error medio en validación cruzada dejando una estación afuera (octubre–abril). Cada columna es un tramo "
           "de distancia a la estación más cercana disponible; 'promedio de tramos' da el mismo peso a cada tramo "
           "(es lo que se minimizó para elegir parámetros). Los parámetros mostrados son los elegidos con todos los "
           "datos; el error es el de validación cruzada (parámetro elegido sin la estación evaluada)."]
    filas_conv = [("estacion", "om"), ("grilla", "om"), ("grilla", "om_qm"), ("fija50", "om"), ("fija50", "om_qm"),
                  ("fija_opt", "om"), ("fija_opt", "om_qm"), ("exp", "om"), ("exp", "om_qm"), ("idw1", "om"),
                  ("idw1", "om_qm"), ("idw1_p1", "om"), ("idw1_p1", "om_qm"), ("idw2_p1", "om"), ("idw2_p1", "om_qm"),
                  ("idw3", "om"), ("idw3", "om_qm"), ("idw3_p1", "om"), ("idw3_p1", "om_qm"), ("idw3_p2", "om"),
                  ("idw3_p2", "om_qm"), ("idw3_pepita", "om"), ("idw3_pepita", "om_qm"), ("idw3_sin_grilla_p2", "om")]
    filas_pp = [("estacion", "om"), ("grilla", "om"), ("grilla", "om_nasa"), ("grilla", "ens"),
                ("idw3_sin_grilla_p2", "om"), ("fija50", "om"), ("fija_opt", "om"), ("exp", "om"),
                ("idw1_p1", "om"), ("idw3_p1", "om"), ("idw3_p1.5", "om"), ("idw3_p2", "om"),
                ("idw3_p2", "om_nasa"), ("idw3_p2", "ens")]
    for v in VARS:
        cv, el = cvs[v]
        mets = ["mae_D", "mae_M"] if v != "pp" else ["rel_X", "rel_M", "csi_D"]
        for met in mets:
            out.append(f"\n## {NOMBRE_VAR[v].split(':')[0]} — {met}\n")
            out.append(a_md(tabla_cv(cv, el, v, met, filas_pp if v == "pp" else filas_conv),
                            3 if v in ("hr80", "pp") else 2))
        f = FORMULA[v]
        fam_f = (f"idw3_p{f['p']}", f["grilla"])
        out.append(f"\nFórmula elegida: {fam_f}. {estabilidad(el, *fam_f)}.")
        filas_b = []
        for met in mets:
            for ref in [REFERENCIA[v], ("estacion", "om"), ("grilla", "om")]:
                m, lo, hi, gana, n = bootstrap(cv, v, fam_f, ref, met)
                filas_b.append({"métrica": met, "contra": f"{ETQ_FAM[ref[0]]} ({ETQ_GRILLA[ref[1]]})",
                                "diferencia (fórmula − otro)": m, "IC 95 % inferior": lo, "IC 95 % superior": hi,
                                "% configuraciones en que gana la fórmula": 100 * gana, "n": n})
        tb = pd.DataFrame(filas_b).set_index("métrica")
        out.append("\nBootstrap por estación objetivo (2000 réplicas):\n\n" + a_md(tb, 3))
        print(v, "\n", tb.round(3).to_string(), flush=True)

    for var, u, sg, txt in (("tx", 30, 1, "TX ≥ 30 °C"), ("tx", 32, 1, "TX ≥ 32 °C"), ("tn", 5, -1, "TN ≤ 5 °C"),
                            ("hr", 80, 1, "HR media diurna ≥ 80 %")):
        c = conteos(var, todo, u, sg)
        t = c.groupby(["metodo", pd.cut(c.d1, [0, 60, 120])], observed=True)[["sesgo", "mae"]].median().unstack()
        t.columns = [f"{'sesgo' if a == 'sesgo' else 'error abs.'} {int(i.left)}–{int(i.right)} km" for a, i in t.columns]
        out.append(f"\n## Días por campaña (oct–abr) con {txt} — media observada {c.dias_obs.mean():.1f} días\n\n"
                   + a_md(t, 1))
        print(txt, "\n", t.round(1).to_string(), flush=True)

    tabla_w = pd.DataFrame({v: [1 / (1 + (d / FORMULA[v]["L"]) ** FORMULA[v]["p"]) for d in (5, 10, 25, 50, 75, 100, 150)]
                            for v in VARS}, index=[f"{d} km" for d in (5, 10, 25, 50, 75, 100, 150)])
    out.append("\n## Peso de la estación cuando hay una sola (1 − peso de Open-Meteo)\n\n" + a_md(tabla_w.T, 2))
    (A.AQUI / "tablas_peso_distancia.md").write_text("\n".join(out), encoding="utf-8")
    print("listo")
