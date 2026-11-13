# Tablas del análisis de peso según la distancia (peso_distancia.py)

Error medio en validación cruzada dejando una estación afuera (octubre–abril). Cada columna es un tramo de distancia a la estación más cercana disponible; 'promedio de tramos' da el mismo peso a cada tramo (es lo que se minimizó para elegir parámetros). Los parámetros mostrados son los elegidos con todos los datos; el error es el de validación cruzada (parámetro elegido sin la estación evaluada).

## Temperatura máxima (°C) — mae_D

| | parámetros (con todos los datos) | 0–30 | 30–60 | 60–90 | 90–120 | 120–150 | promedio de tramos |
|---|---:|---:|---:|---:|---:|---:|---:|
| Estación más cercana sola (Open-Meteo) | w = 1.00 | 1.30 | 1.19 | 1.86 | 1.55 | 2.08 | 1.60 |
| Grilla sola (Open-Meteo) | w = 0.00 | 1.27 | 1.65 | 1.55 | 1.58 | 1.55 | 1.52 |
| Grilla sola (Open-Meteo corregido por cuantiles) | w = 0.00 | 1.18 | 1.27 | 1.21 | 1.26 | 1.24 | 1.23 |
| 50 % estación + 50 % grilla (Open-Meteo) | w = 0.50 | 1.05 | 1.16 | 1.39 | 1.28 | 1.49 | 1.27 |
| 50 % estación + 50 % grilla (Open-Meteo corregido por cuantiles) | w = 0.50 | 1.02 | 1.08 | 1.34 | 1.20 | 1.43 | 1.21 |
| Peso fijo óptimo (Open-Meteo) | w = 0.45 | 1.06 | 1.19 | 1.40 | 1.29 | 1.50 | 1.29 |
| Peso fijo óptimo (Open-Meteo corregido por cuantiles) | w = 0.25 | 1.07 | 1.14 | 1.21 | 1.17 | 1.28 | 1.17 |
| Peso exp(−d/L) (Open-Meteo) | L = 100 km | 1.19 | 1.11 | 1.41 | 1.32 | 1.45 | 1.29 |
| Peso exp(−d/L) (Open-Meteo corregido por cuantiles) | L = 50 km | 1.10 | 1.10 | 1.21 | 1.20 | 1.23 | 1.17 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo) | p = 0.5, L = 50 km | 1.13 | 1.17 | 1.39 | 1.30 | 1.46 | 1.29 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo corregido por cuantiles) | p = 1, L = 20 km | 1.07 | 1.12 | 1.22 | 1.19 | 1.25 | 1.17 |
| 1 estación + grilla, p = 1 (Open-Meteo) | p = 1, L = 60 km | 1.16 | 1.13 | 1.40 | 1.31 | 1.45 | 1.29 |
| 1 estación + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 20 km | 1.04 | 1.12 | 1.20 | 1.19 | 1.23 | 1.16 |
| 2 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 50 km | 1.09 | 1.10 | 1.32 | 1.30 | 1.40 | 1.24 |
| 2 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 20 km | 1.03 | 1.08 | 1.19 | 1.14 | 1.22 | 1.13 |
| 3 estaciones + grilla, p libre (Open-Meteo) | p = 0.5, L = 20 km | 1.08 | 1.12 | 1.28 | 1.26 | 1.40 | 1.23 |
| 3 estaciones + grilla, p libre (Open-Meteo corregido por cuantiles) | p = 1, L = 20 km | 1.11 | 1.06 | 1.15 | 1.13 | 1.21 | 1.13 |
| 3 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 50 km | 1.06 | 1.11 | 1.28 | 1.27 | 1.39 | 1.22 |
| 3 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 20 km | 1.03 | 1.06 | 1.14 | 1.13 | 1.20 | 1.11 |
| 3 estaciones + grilla, p = 2 (Open-Meteo) | p = 2, L = 70 km | 1.20 | 1.07 | 1.29 | 1.27 | 1.40 | 1.25 |
| 3 estaciones + grilla, p = 2 (Open-Meteo corregido por cuantiles) | p = 2, L = 40 km | 1.15 | 1.05 | 1.18 | 1.16 | 1.20 | 1.15 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo) | p = 1, L = 70 km, d0 = 50 km | 1.09 | 1.13 | 1.28 | 1.27 | 1.41 | 1.23 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo corregido por cuantiles) | p = 1, L = 20 km, d0 = 5 km | 1.10 | 1.07 | 1.15 | 1.14 | 1.20 | 1.13 |
| IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | p = 2, L = ∞ | 1.23 | 1.11 | 1.44 | 1.38 | 1.68 | 1.37 |

## Temperatura máxima (°C) — mae_M

| | parámetros (con todos los datos) | 0–30 | 30–60 | 60–90 | 90–120 | 120–150 | promedio de tramos |
|---|---:|---:|---:|---:|---:|---:|---:|
| Estación más cercana sola (Open-Meteo) | w = 1.00 | 0.79 | 0.58 | 1.22 | 0.89 | 1.39 | 0.97 |
| Grilla sola (Open-Meteo) | w = 0.00 | 0.86 | 1.08 | 1.14 | 1.10 | 1.05 | 1.04 |
| Grilla sola (Open-Meteo corregido por cuantiles) | w = 0.00 | 0.71 | 0.58 | 0.59 | 0.64 | 0.57 | 0.62 |
| 50 % estación + 50 % grilla (Open-Meteo) | w = 0.50 | 0.63 | 0.63 | 0.88 | 0.75 | 0.95 | 0.77 |
| 50 % estación + 50 % grilla (Open-Meteo corregido por cuantiles) | w = 0.50 | 0.55 | 0.50 | 0.82 | 0.64 | 0.87 | 0.68 |
| Peso fijo óptimo (Open-Meteo) | w = 0.45 | 0.65 | 0.65 | 0.89 | 0.77 | 0.98 | 0.79 |
| Peso fijo óptimo (Open-Meteo corregido por cuantiles) | w = 0.25 | 0.62 | 0.52 | 0.68 | 0.61 | 0.71 | 0.63 |
| Peso exp(−d/L) (Open-Meteo) | L = 100 km | 0.70 | 0.58 | 0.90 | 0.81 | 0.96 | 0.79 |
| Peso exp(−d/L) (Open-Meteo corregido por cuantiles) | L = 50 km | 0.62 | 0.51 | 0.67 | 0.62 | 0.61 | 0.60 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo) | p = 0.5, L = 50 km | 0.68 | 0.63 | 0.89 | 0.80 | 0.96 | 0.79 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo corregido por cuantiles) | p = 1, L = 20 km | 0.61 | 0.52 | 0.68 | 0.61 | 0.66 | 0.62 |
| 1 estación + grilla, p = 1 (Open-Meteo) | p = 1, L = 60 km | 0.68 | 0.60 | 0.89 | 0.81 | 0.95 | 0.79 |
| 1 estación + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 20 km | 0.57 | 0.52 | 0.66 | 0.61 | 0.63 | 0.60 |
| 2 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 50 km | 0.59 | 0.59 | 0.82 | 0.82 | 0.90 | 0.74 |
| 2 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 20 km | 0.57 | 0.49 | 0.68 | 0.57 | 0.65 | 0.59 |
| 3 estaciones + grilla, p libre (Open-Meteo) | p = 0.5, L = 20 km | 0.59 | 0.62 | 0.79 | 0.77 | 0.88 | 0.73 |
| 3 estaciones + grilla, p libre (Open-Meteo corregido por cuantiles) | p = 1, L = 20 km | 0.68 | 0.51 | 0.64 | 0.58 | 0.64 | 0.61 |
| 3 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 50 km | 0.56 | 0.61 | 0.77 | 0.78 | 0.88 | 0.72 |
| 3 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 20 km | 0.58 | 0.50 | 0.63 | 0.59 | 0.63 | 0.59 |
| 3 estaciones + grilla, p = 2 (Open-Meteo) | p = 2, L = 70 km | 0.69 | 0.58 | 0.78 | 0.78 | 0.89 | 0.75 |
| 3 estaciones + grilla, p = 2 (Open-Meteo corregido por cuantiles) | p = 2, L = 40 km | 0.66 | 0.51 | 0.67 | 0.60 | 0.59 | 0.60 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo) | p = 1, L = 70 km, d0 = 50 km | 0.57 | 0.64 | 0.78 | 0.78 | 0.89 | 0.73 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo corregido por cuantiles) | p = 1, L = 20 km, d0 = 5 km | 0.66 | 0.51 | 0.63 | 0.59 | 0.63 | 0.61 |
| IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | p = 2, L = ∞ | 0.72 | 0.60 | 0.83 | 0.81 | 1.07 | 0.81 |

Fórmula elegida: ('idw3_p1', 'om_qm'). L elegido en los 21 pliegues: mediana 20 km, rango 20–30 km.

Bootstrap por estación objetivo (2000 réplicas):

| | contra | diferencia (fórmula − otro) | IC 95 % inferior | IC 95 % superior | % configuraciones en que gana la fórmula | n |
|---|---:|---:|---:|---:|---:|---:|
| mae_D | 50 % estación + 50 % grilla (Open-Meteo corregido por cuantiles) | -0.094 | -0.130 | -0.058 | 77.083 | 96.000 |
| mae_D | Estación más cercana sola (Open-Meteo) | -0.472 | -0.538 | -0.410 | 97.917 | 96.000 |
| mae_D | Grilla sola (Open-Meteo) | -0.406 | -0.529 | -0.251 | 88.542 | 96.000 |
| mae_M | 50 % estación + 50 % grilla (Open-Meteo corregido por cuantiles) | -0.079 | -0.130 | -0.028 | 60.417 | 96.000 |
| mae_M | Estación más cercana sola (Open-Meteo) | -0.369 | -0.441 | -0.302 | 82.292 | 96.000 |
| mae_M | Grilla sola (Open-Meteo) | -0.457 | -0.658 | -0.201 | 87.500 | 96.000 |

## Temperatura mínima (°C) — mae_D

| | parámetros (con todos los datos) | 0–30 | 30–60 | 60–90 | 90–120 | 120–150 | promedio de tramos |
|---|---:|---:|---:|---:|---:|---:|---:|
| Estación más cercana sola (Open-Meteo) | w = 1.00 | 1.35 | 1.33 | 2.18 | 1.59 | 2.10 | 1.71 |
| Grilla sola (Open-Meteo) | w = 0.00 | 1.10 | 1.67 | 1.55 | 1.44 | 1.52 | 1.46 |
| Grilla sola (Open-Meteo corregido por cuantiles) | w = 0.00 | 1.36 | 1.34 | 1.61 | 1.40 | 1.50 | 1.44 |
| 50 % estación + 50 % grilla (Open-Meteo) | w = 0.50 | 1.09 | 1.21 | 1.62 | 1.28 | 1.55 | 1.35 |
| 50 % estación + 50 % grilla (Open-Meteo corregido por cuantiles) | w = 0.50 | 1.22 | 1.17 | 1.76 | 1.32 | 1.62 | 1.42 |
| Peso fijo óptimo (Open-Meteo) | w = 0.35 | 1.09 | 1.32 | 1.54 | 1.28 | 1.48 | 1.34 |
| Peso fijo óptimo (Open-Meteo corregido por cuantiles) | w = 0.30 | 1.27 | 1.21 | 1.65 | 1.31 | 1.52 | 1.39 |
| Peso exp(−d/L) (Open-Meteo) | L = 80 km | 1.23 | 1.21 | 1.56 | 1.31 | 1.46 | 1.35 |
| Peso exp(−d/L) (Open-Meteo corregido por cuantiles) | L = 60 km | 1.26 | 1.17 | 1.65 | 1.34 | 1.49 | 1.38 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo) | p = 0.5, L = 20 km | 1.12 | 1.29 | 1.54 | 1.29 | 1.46 | 1.34 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo corregido por cuantiles) | p = 1, L = 30 km | 1.25 | 1.19 | 1.65 | 1.33 | 1.50 | 1.38 |
| 1 estación + grilla, p = 1 (Open-Meteo) | p = 1, L = 40 km | 1.19 | 1.25 | 1.54 | 1.30 | 1.45 | 1.35 |
| 1 estación + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 30 km | 1.25 | 1.19 | 1.65 | 1.33 | 1.49 | 1.38 |
| 2 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 40 km | 1.13 | 1.28 | 1.49 | 1.27 | 1.46 | 1.33 |
| 2 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 30 km | 1.20 | 1.15 | 1.60 | 1.25 | 1.49 | 1.34 |
| 3 estaciones + grilla, p libre (Open-Meteo) | p = 0.5, L = 10 km | 1.19 | 1.28 | 1.43 | 1.25 | 1.40 | 1.31 |
| 3 estaciones + grilla, p libre (Open-Meteo corregido por cuantiles) | p = 1, L = 30 km | 1.27 | 1.13 | 1.51 | 1.22 | 1.41 | 1.31 |
| 3 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 30 km | 1.14 | 1.25 | 1.44 | 1.26 | 1.41 | 1.30 |
| 3 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 30 km | 1.20 | 1.13 | 1.51 | 1.22 | 1.40 | 1.29 |
| 3 estaciones + grilla, p = 2 (Open-Meteo) | p = 2, L = 60 km | 1.24 | 1.20 | 1.47 | 1.26 | 1.41 | 1.32 |
| 3 estaciones + grilla, p = 2 (Open-Meteo corregido por cuantiles) | p = 2, L = 50 km | 1.25 | 1.12 | 1.54 | 1.24 | 1.41 | 1.31 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo) | p = 1, L = 40 km, d0 = 20 km | 1.20 | 1.27 | 1.44 | 1.25 | 1.41 | 1.32 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo corregido por cuantiles) | p = 1, L = 30 km, d0 = 5 km | 1.26 | 1.13 | 1.51 | 1.22 | 1.41 | 1.31 |
| IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | p = 2, L = ∞ | 1.28 | 1.20 | 1.68 | 1.38 | 1.75 | 1.46 |

## Temperatura mínima (°C) — mae_M

| | parámetros (con todos los datos) | 0–30 | 30–60 | 60–90 | 90–120 | 120–150 | promedio de tramos |
|---|---:|---:|---:|---:|---:|---:|---:|
| Estación más cercana sola (Open-Meteo) | w = 1.00 | 0.88 | 0.77 | 1.69 | 0.89 | 1.44 | 1.14 |
| Grilla sola (Open-Meteo) | w = 0.00 | 0.54 | 1.29 | 1.11 | 0.97 | 1.06 | 0.99 |
| Grilla sola (Open-Meteo corregido por cuantiles) | w = 0.00 | 0.93 | 0.65 | 1.05 | 0.85 | 0.91 | 0.88 |
| 50 % estación + 50 % grilla (Open-Meteo) | w = 0.50 | 0.65 | 0.73 | 1.18 | 0.76 | 1.01 | 0.86 |
| 50 % estación + 50 % grilla (Open-Meteo corregido por cuantiles) | w = 0.50 | 0.84 | 0.65 | 1.32 | 0.79 | 1.06 | 0.93 |
| Peso fijo óptimo (Open-Meteo) | w = 0.35 | 0.62 | 0.89 | 1.09 | 0.80 | 0.96 | 0.87 |
| Peso fijo óptimo (Open-Meteo corregido por cuantiles) | w = 0.30 | 0.88 | 0.63 | 1.19 | 0.81 | 0.98 | 0.90 |
| Peso exp(−d/L) (Open-Meteo) | L = 80 km | 0.79 | 0.71 | 1.11 | 0.83 | 0.98 | 0.89 |
| Peso exp(−d/L) (Open-Meteo corregido por cuantiles) | L = 60 km | 0.85 | 0.64 | 1.18 | 0.83 | 0.93 | 0.88 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo) | p = 0.5, L = 20 km | 0.66 | 0.84 | 1.08 | 0.81 | 0.95 | 0.87 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo corregido por cuantiles) | p = 1, L = 30 km | 0.84 | 0.63 | 1.18 | 0.82 | 0.95 | 0.88 |
| 1 estación + grilla, p = 1 (Open-Meteo) | p = 1, L = 40 km | 0.75 | 0.78 | 1.09 | 0.82 | 0.96 | 0.88 |
| 1 estación + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 30 km | 0.86 | 0.64 | 1.18 | 0.82 | 0.95 | 0.89 |
| 2 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 40 km | 0.69 | 0.87 | 1.07 | 0.78 | 0.96 | 0.87 |
| 2 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 30 km | 0.80 | 0.61 | 1.16 | 0.73 | 0.98 | 0.86 |
| 3 estaciones + grilla, p libre (Open-Meteo) | p = 0.5, L = 10 km | 0.77 | 0.87 | 1.00 | 0.76 | 0.88 | 0.86 |
| 3 estaciones + grilla, p libre (Open-Meteo corregido por cuantiles) | p = 1, L = 30 km | 0.90 | 0.60 | 1.08 | 0.68 | 0.90 | 0.83 |
| 3 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 30 km | 0.73 | 0.84 | 1.01 | 0.78 | 0.89 | 0.85 |
| 3 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 30 km | 0.84 | 0.59 | 1.08 | 0.68 | 0.89 | 0.82 |
| 3 estaciones + grilla, p = 2 (Open-Meteo) | p = 2, L = 60 km | 0.80 | 0.75 | 1.04 | 0.78 | 0.90 | 0.85 |
| 3 estaciones + grilla, p = 2 (Open-Meteo corregido por cuantiles) | p = 2, L = 50 km | 0.82 | 0.60 | 1.12 | 0.70 | 0.88 | 0.83 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo) | p = 1, L = 40 km, d0 = 20 km | 0.78 | 0.87 | 1.00 | 0.77 | 0.90 | 0.86 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo corregido por cuantiles) | p = 1, L = 30 km, d0 = 5 km | 0.90 | 0.59 | 1.08 | 0.68 | 0.89 | 0.83 |
| IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | p = 2, L = ∞ | 0.83 | 0.71 | 1.23 | 0.80 | 1.25 | 0.96 |

Fórmula elegida: ('idw3_p1', 'om'). L elegido en los 21 pliegues: mediana 30 km, rango 30–50 km.

Bootstrap por estación objetivo (2000 réplicas):

| | contra | diferencia (fórmula − otro) | IC 95 % inferior | IC 95 % superior | % configuraciones en que gana la fórmula | n |
|---|---:|---:|---:|---:|---:|---:|
| mae_D | 50 % estación + 50 % grilla (Open-Meteo) | -0.046 | -0.099 | 0.013 | 68.750 | 96.000 |
| mae_D | Estación más cercana sola (Open-Meteo) | -0.397 | -0.501 | -0.299 | 87.500 | 96.000 |
| mae_D | Grilla sola (Open-Meteo) | -0.163 | -0.270 | -0.030 | 80.208 | 96.000 |
| mae_M | 50 % estación + 50 % grilla (Open-Meteo) | -0.006 | -0.085 | 0.079 | 56.250 | 96.000 |
| mae_M | Estación más cercana sola (Open-Meteo) | -0.266 | -0.437 | -0.115 | 67.708 | 96.000 |
| mae_M | Grilla sola (Open-Meteo) | -0.155 | -0.318 | 0.015 | 70.833 | 96.000 |

## HR media diurna (%) — mae_D

| | parámetros (con todos los datos) | 0–30 | 30–60 | 60–90 | 90–120 | 120–150 | promedio de tramos |
|---|---:|---:|---:|---:|---:|---:|---:|
| Estación más cercana sola (Open-Meteo) | w = 1.00 | 4.06 | 3.25 | 5.05 | 5.53 | 7.69 | 5.12 |
| Grilla sola (Open-Meteo) | w = 0.00 | 3.88 | 4.18 | 4.08 | 4.41 | 4.56 | 4.22 |
| Grilla sola (Open-Meteo corregido por cuantiles) | w = 0.00 | 4.78 | 4.00 | 4.57 | 4.91 | 5.22 | 4.70 |
| 50 % estación + 50 % grilla (Open-Meteo) | w = 0.50 | 3.25 | 3.02 | 3.67 | 4.12 | 5.14 | 3.84 |
| 50 % estación + 50 % grilla (Open-Meteo corregido por cuantiles) | w = 0.50 | 3.63 | 3.11 | 3.83 | 4.43 | 5.48 | 4.10 |
| Peso fijo óptimo (Open-Meteo) | w = 0.35 | 3.39 | 3.35 | 3.61 | 4.05 | 4.67 | 3.81 |
| Peso fijo óptimo (Open-Meteo corregido por cuantiles) | w = 0.45 | 3.76 | 3.21 | 3.83 | 4.42 | 5.32 | 4.11 |
| Peso exp(−d/L) (Open-Meteo) | L = 80 km | 3.56 | 3.05 | 3.60 | 4.05 | 4.45 | 3.74 |
| Peso exp(−d/L) (Open-Meteo corregido por cuantiles) | L = 90 km | 3.71 | 3.05 | 3.82 | 4.43 | 5.08 | 4.02 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo) | p = 1, L = 40 km | 3.55 | 3.25 | 3.62 | 4.05 | 4.48 | 3.79 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo corregido por cuantiles) | p = 1, L = 50 km | 3.72 | 3.13 | 3.83 | 4.43 | 5.16 | 4.05 |
| 1 estación + grilla, p = 1 (Open-Meteo) | p = 1, L = 40 km | 3.39 | 3.23 | 3.63 | 4.08 | 4.47 | 3.76 |
| 1 estación + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 50 km | 3.62 | 3.12 | 3.83 | 4.42 | 5.10 | 4.02 |
| 2 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 30 km | 3.21 | 3.06 | 3.54 | 4.05 | 4.48 | 3.67 |
| 2 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 50 km | 3.42 | 3.01 | 3.73 | 4.28 | 4.93 | 3.87 |
| 3 estaciones + grilla, p libre (Open-Meteo) | p = 1, L = 30 km | 3.42 | 2.97 | 3.39 | 4.05 | 4.45 | 3.66 |
| 3 estaciones + grilla, p libre (Open-Meteo corregido por cuantiles) | p = 1, L = 40 km | 3.48 | 3.08 | 3.59 | 4.26 | 4.80 | 3.84 |
| 3 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 30 km | 3.15 | 3.00 | 3.42 | 4.07 | 4.37 | 3.60 |
| 3 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 40 km | 3.33 | 3.05 | 3.58 | 4.24 | 4.78 | 3.80 |
| 3 estaciones + grilla, p = 2 (Open-Meteo) | p = 2, L = 50 km | 3.63 | 2.86 | 3.42 | 4.08 | 4.33 | 3.66 |
| 3 estaciones + grilla, p = 2 (Open-Meteo corregido por cuantiles) | p = 2, L = 60 km | 3.74 | 2.98 | 3.60 | 4.28 | 4.78 | 3.88 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo) | p = 2, L = 60 km, d0 = 50 km | 3.31 | 2.98 | 3.42 | 4.06 | 4.36 | 3.63 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo corregido por cuantiles) | p = 1.5, L = 70 km, d0 = 50 km | 3.46 | 3.06 | 3.56 | 4.27 | 4.83 | 3.84 |
| IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | p = 2, L = ∞ | 3.87 | 3.21 | 4.12 | 5.04 | 6.38 | 4.53 |

## HR media diurna (%) — mae_M

| | parámetros (con todos los datos) | 0–30 | 30–60 | 60–90 | 90–120 | 120–150 | promedio de tramos |
|---|---:|---:|---:|---:|---:|---:|---:|
| Estación más cercana sola (Open-Meteo) | w = 1.00 | 2.92 | — | 2.86 | 3.66 | 4.95 | 3.60 |
| Grilla sola (Open-Meteo) | w = 0.00 | 2.12 | — | 3.02 | 2.71 | 2.94 | 2.70 |
| Grilla sola (Open-Meteo corregido por cuantiles) | w = 0.00 | 3.51 | — | 3.78 | 3.52 | 3.72 | 3.63 |
| 50 % estación + 50 % grilla (Open-Meteo) | w = 0.50 | 2.07 | — | 2.38 | 2.67 | 3.38 | 2.63 |
| 50 % estación + 50 % grilla (Open-Meteo corregido por cuantiles) | w = 0.50 | 2.53 | — | 2.89 | 3.22 | 4.10 | 3.19 |
| Peso fijo óptimo (Open-Meteo) | w = 0.35 | 2.07 | — | 2.51 | 2.61 | 2.98 | 2.54 |
| Peso fijo óptimo (Open-Meteo corregido por cuantiles) | w = 0.45 | 2.67 | — | 3.06 | 3.28 | 4.02 | 3.26 |
| Peso exp(−d/L) (Open-Meteo) | L = 80 km | 2.48 | — | 2.49 | 2.56 | 2.86 | 2.60 |
| Peso exp(−d/L) (Open-Meteo corregido por cuantiles) | L = 90 km | 2.60 | — | 3.03 | 3.29 | 3.91 | 3.21 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo) | p = 1, L = 40 km | 2.42 | — | 2.51 | 2.58 | 2.87 | 2.59 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo corregido por cuantiles) | p = 1, L = 50 km | 2.62 | — | 3.07 | 3.29 | 3.97 | 3.24 |
| 1 estación + grilla, p = 1 (Open-Meteo) | p = 1, L = 40 km | 2.29 | — | 2.55 | 2.60 | 2.86 | 2.57 |
| 1 estación + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 50 km | 2.52 | — | 3.06 | 3.27 | 3.93 | 3.19 |
| 2 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 30 km | 2.17 | — | 2.52 | 2.63 | 2.87 | 2.55 |
| 2 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 50 km | 2.44 | — | 2.97 | 3.08 | 3.74 | 3.06 |
| 3 estaciones + grilla, p libre (Open-Meteo) | p = 1, L = 30 km | 2.37 | — | 2.33 | 2.69 | 2.88 | 2.57 |
| 3 estaciones + grilla, p libre (Open-Meteo corregido por cuantiles) | p = 1, L = 40 km | 2.51 | — | 2.79 | 3.10 | 3.51 | 2.98 |
| 3 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 30 km | 2.12 | — | 2.38 | 2.71 | 2.87 | 2.52 |
| 3 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 40 km | 2.37 | — | 2.76 | 3.09 | 3.55 | 2.94 |
| 3 estaciones + grilla, p = 2 (Open-Meteo) | p = 2, L = 50 km | 2.61 | — | 2.38 | 2.72 | 2.84 | 2.64 |
| 3 estaciones + grilla, p = 2 (Open-Meteo corregido por cuantiles) | p = 2, L = 60 km | 2.71 | — | 2.76 | 3.19 | 3.61 | 3.06 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo) | p = 2, L = 60 km, d0 = 50 km | 2.30 | — | 2.39 | 2.71 | 2.84 | 2.56 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo corregido por cuantiles) | p = 1.5, L = 70 km, d0 = 50 km | 2.51 | — | 2.73 | 3.12 | 3.56 | 2.98 |
| IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | p = 2, L = ∞ | 2.83 | — | 2.61 | 3.60 | 3.98 | 3.25 |

Fórmula elegida: ('idw3_p1', 'om'). L elegido en los 14 pliegues: mediana 30 km, rango 20–40 km.

Bootstrap por estación objetivo (2000 réplicas):

| | contra | diferencia (fórmula − otro) | IC 95 % inferior | IC 95 % superior | % configuraciones en que gana la fórmula | n |
|---|---:|---:|---:|---:|---:|---:|
| mae_D | 50 % estación + 50 % grilla (Open-Meteo) | -0.246 | -0.371 | -0.096 | 64.062 | 64.000 |
| mae_D | Estación más cercana sola (Open-Meteo) | -1.505 | -1.926 | -1.183 | 96.875 | 64.000 |
| mae_D | Grilla sola (Open-Meteo) | -0.635 | -0.884 | -0.243 | 85.938 | 64.000 |
| mae_M | 50 % estación + 50 % grilla (Open-Meteo) | -0.149 | -0.383 | 0.068 | 40.625 | 64.000 |
| mae_M | Estación más cercana sola (Open-Meteo) | -1.114 | -1.776 | -0.628 | 57.812 | 64.000 |
| mae_M | Grilla sola (Open-Meteo) | -0.224 | -0.605 | 0.349 | 56.250 | 64.000 |

## Fracción de horas diurnas con HR ≥ 80 % — mae_D

| | parámetros (con todos los datos) | 0–30 | 30–60 | 60–90 | 90–120 | 120–150 | promedio de tramos |
|---|---:|---:|---:|---:|---:|---:|---:|
| Estación más cercana sola (Open-Meteo) | w = 1.00 | 0.089 | 0.069 | 0.113 | 0.117 | 0.155 | 0.108 |
| Grilla sola (Open-Meteo) | w = 0.00 | 0.096 | 0.115 | 0.105 | 0.112 | 0.115 | 0.109 |
| Grilla sola (Open-Meteo corregido por cuantiles) | w = 0.00 | 0.123 | 0.091 | 0.118 | 0.119 | 0.141 | 0.118 |
| 50 % estación + 50 % grilla (Open-Meteo) | w = 0.50 | 0.081 | 0.077 | 0.095 | 0.098 | 0.118 | 0.094 |
| 50 % estación + 50 % grilla (Open-Meteo corregido por cuantiles) | w = 0.50 | 0.094 | 0.071 | 0.104 | 0.104 | 0.131 | 0.101 |
| Peso fijo óptimo (Open-Meteo) | w = 0.50 | 0.081 | 0.082 | 0.096 | 0.099 | 0.117 | 0.095 |
| Peso fijo óptimo (Open-Meteo corregido por cuantiles) | w = 0.60 | 0.092 | 0.070 | 0.104 | 0.105 | 0.134 | 0.101 |
| Peso exp(−d/L) (Open-Meteo) | L = 120 km | 0.084 | 0.074 | 0.096 | 0.099 | 0.112 | 0.093 |
| Peso exp(−d/L) (Open-Meteo corregido por cuantiles) | L = 170 km | 0.088 | 0.068 | 0.103 | 0.105 | 0.132 | 0.099 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo) | p = 1.5, L = 80 km | 0.087 | 0.078 | 0.097 | 0.100 | 0.114 | 0.095 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo corregido por cuantiles) | p = 1, L = 120 km | 0.088 | 0.068 | 0.103 | 0.105 | 0.132 | 0.099 |
| 1 estación + grilla, p = 1 (Open-Meteo) | p = 1, L = 70 km | 0.083 | 0.078 | 0.096 | 0.100 | 0.113 | 0.094 |
| 1 estación + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 120 km | 0.088 | 0.068 | 0.103 | 0.104 | 0.131 | 0.099 |
| 2 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 60 km | 0.080 | 0.078 | 0.093 | 0.099 | 0.111 | 0.092 |
| 2 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 100 km | 0.084 | 0.068 | 0.097 | 0.101 | 0.128 | 0.096 |
| 3 estaciones + grilla, p libre (Open-Meteo) | p = 1, L = 50 km | 0.087 | 0.078 | 0.091 | 0.099 | 0.107 | 0.093 |
| 3 estaciones + grilla, p libre (Open-Meteo corregido por cuantiles) | p = 1, L = 80 km | 0.086 | 0.070 | 0.095 | 0.103 | 0.119 | 0.095 |
| 3 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 50 km | 0.078 | 0.077 | 0.090 | 0.098 | 0.107 | 0.090 |
| 3 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 80 km | 0.082 | 0.069 | 0.095 | 0.102 | 0.119 | 0.094 |
| 3 estaciones + grilla, p = 2 (Open-Meteo) | p = 2, L = 70 km | 0.084 | 0.072 | 0.090 | 0.098 | 0.106 | 0.090 |
| 3 estaciones + grilla, p = 2 (Open-Meteo corregido por cuantiles) | p = 2, L = 90 km | 0.086 | 0.068 | 0.095 | 0.102 | 0.120 | 0.094 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo) | p = 3, L = 80 km, d0 = 50 km | 0.085 | 0.075 | 0.090 | 0.098 | 0.107 | 0.091 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo corregido por cuantiles) | p = 1.5, L = 100 km, d0 = 30 km | 0.086 | 0.069 | 0.094 | 0.103 | 0.119 | 0.094 |
| IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | p = 2, L = ∞ | 0.086 | 0.069 | 0.098 | 0.110 | 0.133 | 0.099 |

## Fracción de horas diurnas con HR ≥ 80 % — mae_M

| | parámetros (con todos los datos) | 0–30 | 30–60 | 60–90 | 90–120 | 120–150 | promedio de tramos |
|---|---:|---:|---:|---:|---:|---:|---:|
| Estación más cercana sola (Open-Meteo) | w = 1.00 | 0.053 | — | 0.057 | 0.064 | 0.079 | 0.063 |
| Grilla sola (Open-Meteo) | w = 0.00 | 0.045 | — | 0.065 | 0.070 | 0.079 | 0.065 |
| Grilla sola (Open-Meteo corregido por cuantiles) | w = 0.00 | 0.071 | — | 0.075 | 0.068 | 0.087 | 0.075 |
| 50 % estación + 50 % grilla (Open-Meteo) | w = 0.50 | 0.041 | — | 0.051 | 0.054 | 0.062 | 0.052 |
| 50 % estación + 50 % grilla (Open-Meteo corregido por cuantiles) | w = 0.50 | 0.055 | — | 0.063 | 0.057 | 0.076 | 0.063 |
| Peso fijo óptimo (Open-Meteo) | w = 0.50 | 0.042 | — | 0.053 | 0.056 | 0.062 | 0.053 |
| Peso fijo óptimo (Open-Meteo corregido por cuantiles) | w = 0.60 | 0.054 | — | 0.061 | 0.058 | 0.075 | 0.062 |
| Peso exp(−d/L) (Open-Meteo) | L = 120 km | 0.049 | — | 0.052 | 0.056 | 0.063 | 0.055 |
| Peso exp(−d/L) (Open-Meteo corregido por cuantiles) | L = 170 km | 0.052 | — | 0.061 | 0.058 | 0.078 | 0.062 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo) | p = 1.5, L = 80 km | 0.050 | — | 0.052 | 0.057 | 0.065 | 0.056 |
| 1 estación + grilla, 1/(1+(d/L)^p) (Open-Meteo corregido por cuantiles) | p = 1, L = 120 km | 0.052 | — | 0.061 | 0.058 | 0.078 | 0.062 |
| 1 estación + grilla, p = 1 (Open-Meteo) | p = 1, L = 70 km | 0.047 | — | 0.052 | 0.057 | 0.062 | 0.055 |
| 1 estación + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 120 km | 0.052 | — | 0.061 | 0.058 | 0.077 | 0.062 |
| 2 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 60 km | 0.044 | — | 0.053 | 0.056 | 0.059 | 0.053 |
| 2 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 100 km | 0.049 | — | 0.058 | 0.057 | 0.072 | 0.059 |
| 3 estaciones + grilla, p libre (Open-Meteo) | p = 1, L = 50 km | 0.049 | — | 0.050 | 0.058 | 0.058 | 0.054 |
| 3 estaciones + grilla, p libre (Open-Meteo corregido por cuantiles) | p = 1, L = 80 km | 0.051 | — | 0.053 | 0.057 | 0.066 | 0.057 |
| 3 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 50 km | 0.042 | — | 0.051 | 0.057 | 0.057 | 0.052 |
| 3 estaciones + grilla, p = 1 (Open-Meteo corregido por cuantiles) | p = 1, L = 80 km | 0.047 | — | 0.053 | 0.056 | 0.067 | 0.056 |
| 3 estaciones + grilla, p = 2 (Open-Meteo) | p = 2, L = 70 km | 0.049 | — | 0.050 | 0.056 | 0.059 | 0.053 |
| 3 estaciones + grilla, p = 2 (Open-Meteo corregido por cuantiles) | p = 2, L = 90 km | 0.050 | — | 0.053 | 0.057 | 0.070 | 0.058 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo) | p = 3, L = 80 km, d0 = 50 km | 0.047 | — | 0.050 | 0.057 | 0.060 | 0.054 |
| 3 estaciones + grilla, p y pepita d0 libres (Open-Meteo corregido por cuantiles) | p = 1.5, L = 100 km, d0 = 30 km | 0.050 | — | 0.053 | 0.057 | 0.067 | 0.057 |
| IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | p = 2, L = ∞ | 0.050 | — | 0.053 | 0.061 | 0.068 | 0.058 |

Fórmula elegida: ('idw3_p1', 'om'). L elegido en los 14 pliegues: mediana 50 km, rango 30–70 km.

Bootstrap por estación objetivo (2000 réplicas):

| | contra | diferencia (fórmula − otro) | IC 95 % inferior | IC 95 % superior | % configuraciones en que gana la fórmula | n |
|---|---:|---:|---:|---:|---:|---:|
| mae_D | 50 % estación + 50 % grilla (Open-Meteo) | -0.003 | -0.006 | -0.001 | 53.125 | 64.000 |
| mae_D | Estación más cercana sola (Open-Meteo) | -0.018 | -0.024 | -0.013 | 84.375 | 64.000 |
| mae_D | Grilla sola (Open-Meteo) | -0.018 | -0.023 | -0.014 | 82.812 | 64.000 |
| mae_M | 50 % estación + 50 % grilla (Open-Meteo) | -0.001 | -0.005 | 0.002 | 37.500 | 64.000 |
| mae_M | Estación más cercana sola (Open-Meteo) | -0.012 | -0.026 | -0.001 | 48.438 | 64.000 |
| mae_M | Grilla sola (Open-Meteo) | -0.013 | -0.025 | -0.003 | 56.250 | 64.000 |

## Lluvia — rel_X

| | parámetros (con todos los datos) | 0–10 | 10–20 | 20–30 | 30–45 | 45–60 | 60–80 | 80–120 | promedio de tramos |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Estación más cercana sola (Open-Meteo) | w = 1.00 | 0.244 | 0.337 | 0.353 | 0.406 | 0.453 | 0.495 | 0.548 | 0.405 |
| Grilla sola (Open-Meteo) | w = 0.00 | 0.482 | 0.561 | 0.514 | 0.521 | 0.511 | 0.512 | 0.514 | 0.516 |
| Grilla sola (promedio Open-Meteo + NASA) | w = 0.00 | 0.466 | 0.485 | 0.446 | 0.440 | 0.441 | 0.439 | 0.439 | 0.451 |
| Grilla sola (promedio 3 grillas) | w = 0.00 | 0.436 | 0.477 | 0.441 | 0.438 | 0.438 | 0.436 | 0.437 | 0.443 |
| IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | p = 2, L = ∞ | 0.218 | 0.282 | 0.303 | 0.342 | 0.373 | 0.403 | 0.441 | 0.337 |
| 50 % estación + 50 % grilla (Open-Meteo) | w = 0.50 | 0.301 | 0.373 | 0.364 | 0.391 | 0.411 | 0.432 | 0.458 | 0.390 |
| Peso fijo óptimo (Open-Meteo) | w = 0.70 | 0.267 | 0.335 | 0.337 | 0.376 | 0.409 | 0.441 | 0.478 | 0.378 |
| Peso exp(−d/L) (Open-Meteo) | L = 120 km | 0.237 | 0.324 | 0.333 | 0.376 | 0.407 | 0.432 | 0.457 | 0.367 |
| 1 estación + grilla, p = 1 (Open-Meteo) | p = 1, L = 80 km | 0.236 | 0.324 | 0.334 | 0.376 | 0.407 | 0.432 | 0.457 | 0.366 |
| 3 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 100 km | 0.206 | 0.284 | 0.303 | 0.339 | 0.365 | 0.390 | 0.420 | 0.330 |
| 3 estaciones + grilla, p = 1.5 (Open-Meteo) | p = 1.5, L = 80 km | 0.210 | 0.279 | 0.300 | 0.338 | 0.365 | 0.390 | 0.419 | 0.329 |
| 3 estaciones + grilla, p = 2 (Open-Meteo) | p = 2, L = 80 km | 0.217 | 0.281 | 0.300 | 0.338 | 0.364 | 0.390 | 0.420 | 0.330 |
| 3 estaciones + grilla, p = 2 (promedio Open-Meteo + NASA) | p = 2, L = 50 km | 0.216 | 0.280 | 0.299 | 0.333 | 0.358 | 0.380 | 0.400 | 0.324 |
| 3 estaciones + grilla, p = 2 (promedio 3 grillas) | p = 2, L = 50 km | 0.215 | 0.279 | 0.299 | 0.333 | 0.358 | 0.379 | 0.400 | 0.323 |

## Lluvia — rel_M

| | parámetros (con todos los datos) | 0–10 | 10–20 | 20–30 | 30–45 | 45–60 | 60–80 | 80–120 | promedio de tramos |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Estación más cercana sola (Open-Meteo) | w = 1.00 | 0.135 | 0.229 | 0.239 | 0.270 | 0.296 | 0.337 | 0.368 | 0.268 |
| Grilla sola (Open-Meteo) | w = 0.00 | 0.324 | 0.378 | 0.337 | 0.342 | 0.339 | 0.339 | 0.341 | 0.343 |
| Grilla sola (promedio Open-Meteo + NASA) | w = 0.00 | 0.314 | 0.342 | 0.304 | 0.300 | 0.304 | 0.303 | 0.304 | 0.310 |
| Grilla sola (promedio 3 grillas) | w = 0.00 | 0.292 | 0.331 | 0.302 | 0.299 | 0.301 | 0.299 | 0.300 | 0.303 |
| IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | p = 2, L = ∞ | 0.119 | 0.191 | 0.202 | 0.226 | 0.243 | 0.272 | 0.295 | 0.221 |
| 50 % estación + 50 % grilla (Open-Meteo) | w = 0.50 | 0.189 | 0.255 | 0.240 | 0.257 | 0.268 | 0.289 | 0.304 | 0.257 |
| Peso fijo óptimo (Open-Meteo) | w = 0.70 | 0.154 | 0.232 | 0.226 | 0.248 | 0.266 | 0.298 | 0.319 | 0.249 |
| Peso exp(−d/L) (Open-Meteo) | L = 120 km | 0.132 | 0.222 | 0.224 | 0.248 | 0.264 | 0.290 | 0.303 | 0.240 |
| 1 estación + grilla, p = 1 (Open-Meteo) | p = 1, L = 80 km | 0.131 | 0.223 | 0.224 | 0.248 | 0.265 | 0.290 | 0.303 | 0.240 |
| 3 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 100 km | 0.112 | 0.197 | 0.199 | 0.222 | 0.239 | 0.261 | 0.280 | 0.216 |
| 3 estaciones + grilla, p = 1.5 (Open-Meteo) | p = 1.5, L = 80 km | 0.114 | 0.192 | 0.198 | 0.222 | 0.238 | 0.261 | 0.279 | 0.215 |
| 3 estaciones + grilla, p = 2 (Open-Meteo) | p = 2, L = 80 km | 0.119 | 0.191 | 0.199 | 0.222 | 0.238 | 0.261 | 0.279 | 0.216 |
| 3 estaciones + grilla, p = 2 (promedio Open-Meteo + NASA) | p = 2, L = 50 km | 0.118 | 0.190 | 0.198 | 0.219 | 0.235 | 0.256 | 0.270 | 0.212 |
| 3 estaciones + grilla, p = 2 (promedio 3 grillas) | p = 2, L = 50 km | 0.118 | 0.189 | 0.197 | 0.219 | 0.234 | 0.254 | 0.267 | 0.211 |

## Lluvia — csi_D

| | parámetros (con todos los datos) | 0–10 | 10–20 | 20–30 | 30–45 | 45–60 | 60–80 | 80–120 | promedio de tramos |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Estación más cercana sola (Open-Meteo) | w = 1.00 | 0.768 | 0.747 | 0.727 | 0.685 | 0.663 | 0.638 | 0.598 | 0.689 |
| Grilla sola (Open-Meteo) | w = 0.00 | 0.538 | 0.549 | 0.560 | 0.552 | 0.563 | 0.563 | 0.567 | 0.556 |
| Grilla sola (promedio Open-Meteo + NASA) | w = 0.00 | 0.550 | 0.570 | 0.580 | 0.579 | 0.587 | 0.586 | 0.590 | 0.577 |
| Grilla sola (promedio 3 grillas) | w = 0.00 | 0.559 | 0.567 | 0.579 | 0.577 | 0.586 | 0.584 | 0.587 | 0.577 |
| IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | p = 2, L = ∞ | 0.791 | 0.758 | 0.734 | 0.702 | 0.683 | 0.662 | 0.633 | 0.709 |
| 50 % estación + 50 % grilla (Open-Meteo) | w = 0.50 | 0.667 | 0.663 | 0.647 | 0.630 | 0.631 | 0.620 | 0.611 | 0.638 |
| Peso fijo óptimo (Open-Meteo) | w = 0.70 | 0.700 | 0.706 | 0.684 | 0.659 | 0.657 | 0.642 | 0.627 | 0.668 |
| Peso exp(−d/L) (Open-Meteo) | L = 120 km | 0.760 | 0.734 | 0.704 | 0.662 | 0.651 | 0.628 | 0.607 | 0.678 |
| 1 estación + grilla, p = 1 (Open-Meteo) | p = 1, L = 80 km | 0.754 | 0.731 | 0.698 | 0.655 | 0.647 | 0.626 | 0.608 | 0.674 |
| 3 estaciones + grilla, p = 1 (Open-Meteo) | p = 1, L = 100 km | 0.774 | 0.742 | 0.717 | 0.687 | 0.672 | 0.651 | 0.627 | 0.696 |
| 3 estaciones + grilla, p = 1.5 (Open-Meteo) | p = 1.5, L = 80 km | 0.782 | 0.749 | 0.726 | 0.690 | 0.671 | 0.648 | 0.622 | 0.698 |
| 3 estaciones + grilla, p = 2 (Open-Meteo) | p = 2, L = 80 km | 0.793 | 0.757 | 0.733 | 0.695 | 0.675 | 0.649 | 0.621 | 0.703 |
| 3 estaciones + grilla, p = 2 (promedio Open-Meteo + NASA) | p = 2, L = 50 km | 0.786 | 0.756 | 0.723 | 0.681 | 0.661 | 0.634 | 0.613 | 0.693 |
| 3 estaciones + grilla, p = 2 (promedio 3 grillas) | p = 2, L = 50 km | 0.790 | 0.753 | 0.726 | 0.682 | 0.663 | 0.635 | 0.613 | 0.694 |

Fórmula elegida: ('idw3_p2', 'om'). L elegido en los 72 pliegues: mediana 80 km, rango 80–80 km.

Bootstrap por estación objetivo (2000 réplicas):

| | contra | diferencia (fórmula − otro) | IC 95 % inferior | IC 95 % superior | % configuraciones en que gana la fórmula | n |
|---|---:|---:|---:|---:|---:|---:|
| rel_X | IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | -0.007 | -0.010 | -0.006 | 72.081 | 788.000 |
| rel_X | Estación más cercana sola (Open-Meteo) | -0.074 | -0.085 | -0.067 | 96.193 | 788.000 |
| rel_X | Grilla sola (Open-Meteo) | -0.186 | -0.197 | -0.168 | 98.223 | 788.000 |
| rel_M | IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | -0.006 | -0.008 | -0.004 | 67.893 | 788.000 |
| rel_M | Estación más cercana sola (Open-Meteo) | -0.051 | -0.060 | -0.046 | 91.751 | 788.000 |
| rel_M | Grilla sola (Open-Meteo) | -0.127 | -0.136 | -0.110 | 94.924 | 788.000 |
| csi_D | IDW 3 estaciones (1/d²) sin grilla (Open-Meteo) | -0.006 | -0.008 | -0.004 | 29.061 | 788.000 |
| csi_D | Estación más cercana sola (Open-Meteo) | 0.013 | 0.007 | 0.019 | 64.340 | 788.000 |
| csi_D | Grilla sola (Open-Meteo) | 0.147 | 0.124 | 0.157 | 99.746 | 788.000 |

## Días por campaña (oct–abr) con TX ≥ 30 °C — media observada 49.6 días

| | sesgo 0–60 km | sesgo 60–120 km | error abs. 0–60 km | error abs. 60–120 km |
|---|---:|---:|---:|---:|
| estacion | 0.0 | 0.0 | 9.7 | 13.0 |
| fija50 om | -7.0 | -11.2 | 7.7 | 11.5 |
| fija50 om_qm | -1.7 | -2.2 | 4.8 | 7.6 |
| formula | -0.7 | -1.5 | 4.3 | 6.6 |

## Días por campaña (oct–abr) con TX ≥ 32 °C — media observada 28.2 días

| | sesgo 0–60 km | sesgo 60–120 km | error abs. 0–60 km | error abs. 60–120 km |
|---|---:|---:|---:|---:|
| estacion | 0.0 | 0.0 | 5.7 | 11.0 |
| fija50 om | -6.2 | -8.0 | 6.5 | 8.0 |
| fija50 om_qm | -1.8 | -1.0 | 3.3 | 6.2 |
| formula | -0.7 | -1.0 | 3.0 | 6.0 |

## Días por campaña (oct–abr) con TN ≤ 5 °C — media observada 2.3 días

| | sesgo 0–60 km | sesgo 60–120 km | error abs. 0–60 km | error abs. 60–120 km |
|---|---:|---:|---:|---:|
| estacion | 0.0 | 0.0 | 0.7 | 1.7 |
| fija50 om | -0.8 | -0.7 | 1.0 | 1.0 |
| fija50 om_qm | -0.3 | -0.2 | 0.8 | 1.3 |
| formula | -0.7 | -1.0 | 0.8 | 1.0 |

## Días por campaña (oct–abr) con HR media diurna ≥ 80 % — media observada 33.9 días

| | sesgo 0–60 km | sesgo 60–120 km | error abs. 0–60 km | error abs. 60–120 km |
|---|---:|---:|---:|---:|
| estacion | 0.0 | 0.7 | 7.7 | 8.0 |
| fija50 om | -4.3 | -3.7 | 6.0 | 6.0 |
| fija50 om_qm | 0.3 | -0.3 | 8.2 | 8.0 |
| formula | -3.2 | -4.3 | 4.8 | 5.0 |

## Peso de la estación cuando hay una sola (1 − peso de Open-Meteo)

| | 5 km | 10 km | 25 km | 50 km | 75 km | 100 km | 150 km |
|---|---:|---:|---:|---:|---:|---:|---:|
| tx | 0.80 | 0.67 | 0.44 | 0.29 | 0.21 | 0.17 | 0.12 |
| tn | 0.86 | 0.75 | 0.55 | 0.37 | 0.29 | 0.23 | 0.17 |
| hr | 0.86 | 0.75 | 0.55 | 0.37 | 0.29 | 0.23 | 0.17 |
| hr80 | 0.91 | 0.83 | 0.67 | 0.50 | 0.40 | 0.33 | 0.25 |
| pp | 1.00 | 0.98 | 0.91 | 0.72 | 0.53 | 0.39 | 0.22 |