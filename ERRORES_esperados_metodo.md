# Errores esperados del método recomendado

Validación cruzada estación–estación (octubre–abril, 2017–2019 y 2024–2025). La “verdad” es una estación INUMET/INMET; se la estima con el método como si fuera una chacra.

**Método:** 3 estaciones (o pluviómetros) más cercanas con dato + Open-Meteo como estación virtual a \(L\) km:

\[
\hat y = \frac{\sum_{i=1}^{3} x_i/d_i^{p} + G/L^{p}}{\sum_{i=1}^{3} 1/d_i^{p} + 1/L^{p}}
\]

| Variable | \(G\) | \(p\) | \(L\) |
|---|---|---:|---:|
| Temperatura máxima | Open-Meteo corregido por cuantiles | 1 | 20 km |
| Temperatura mínima | Open-Meteo | 1 | 30 km |
| HR media diurna (07–19 h) | Open-Meteo | 1 | 30 km |
| Fracción de horas diurnas con HR ≥ 80 % | Open-Meteo | 1 | 50 km |
| Lluvia | Open-Meteo | 2 | 80 km |

Las métricas son **error absoluto medio (MAE)** salvo lluvia (**error relativo** del monto agregado) y **CSI** (acierto de días con lluvia ≥ 1 mm).

---

## 1. Resumen para tus chacras de Uruguay

Distancias típicas de tus 151 muestras al dato INUMET con cobertura en el ciclo: mediana **34 km** (temperatura), **38 km** (humedad), **8 km** (pluviómetro). Todas ≤ 73 km de una estación con temperatura y ≤ 41 km de un pluviómetro.

| Variable | Error típico en tus chacras | Escala mensual / 10 días | Qué significa en la práctica |
|---|---|---|---|
| Temperatura máxima | **±1.0–1.1 °C** diario | **±0.5–0.6 °C** mensual | Un día a 32 °C puede estimarse ~31–33 °C |
| Temperatura mínima | **±1.1–1.2 °C** diario | **±0.7–0.8 °C** mensual | Similar magnitud a la máxima |
| HR media diurna | **±3.0–3.2 %** diario | **±2.0–2.2 %** mensual | Un día a 75 % puede estimarse ~72–78 % |
| Fracción horas HR ≥ 80 % | **±0.08** (fracción del día) | — | ~1 hora de las 13 diurnas |
| Lluvia (monto) | **±12–20 %** del total mensual | **±22–28 %** del total de 10 días | Un mes de 100 mm: error típico ~12–20 mm |
| Días con lluvia ≥ 1 mm | CSI **0.76–0.79** | — | Acierta ~76–79 % de los días lluviosos (unión de observados y estimados) |

Estos valores salen del tramo de distancia que corresponde a tus medianas (T/HR ~30–60 km; lluvia ~0–20 km) en la tabla de abajo.

---

## 2. Error según distancia a la estación / pluviómetro más cercano (Uruguay)

### Temperatura máxima (°C) — fórmula con Open-Meteo corregido por cuantiles

| Distancia | MAE diario | MAE mensual |
|---|---:|---:|
| 0–30 km | 1.03 | 0.58 |
| 30–60 km | 1.06 | 0.50 |
| 60–90 km | 1.14 | 0.63 |
| 90–120 km | 1.13 | 0.59 |
| 120–150 km | 1.20 | 0.63 |

### Temperatura mínima (°C)

| Distancia | MAE diario | MAE mensual |
|---|---:|---:|
| 0–30 km | 1.14 | 0.73 |
| 30–60 km | 1.25 | 0.84 |
| 60–90 km | 1.44 | 1.01 |
| 90–120 km | 1.26 | 0.78 |
| 120–150 km | 1.41 | 0.89 |

### HR media diurna (%)

| Distancia | MAE diario | MAE mensual |
|---|---:|---:|
| 0–30 km | 3.15 | 2.12 |
| 30–60 km | 3.00 | — |
| 60–90 km | 3.42 | 2.38 |
| 90–120 km | 4.07 | 2.71 |
| 120–150 km | 4.37 | 2.87 |

### Lluvia

| Distancia al pluviómetro más cercano | Error rel. 10 días | Error rel. mensual | CSI (días ≥ 1 mm) |
|---|---:|---:|---:|
| 0–10 km | 22 % | 12 % | 0.79 |
| 10–20 km | 28 % | 19 % | 0.76 |
| 20–30 km | 30 % | 20 % | 0.73 |
| 30–45 km | 34 % | 22 % | 0.70 |
| 45–60 km | 36 % | 24 % | 0.68 |
| 60–80 km | 39 % | 26 % | 0.65 |
| 80–120 km | 42 % | 28 % | 0.62 |

**Nota:** a menos de ~30 km la grilla casi no pesa; el error es el del promedio IDW de 3 pluviómetros. Los montos **diarios** siguen siendo imprecisos (±1–2 mm/día cerca); conviene agregar a 10 días, mes o floración.

---

## 3. Conteos por campaña (útil para Fusarium)

Error en el **número de días** por campaña (oct–abr) que superan un umbral. Media observada en Uruguay: ~50 días con TX ≥ 30 °C, ~28 con TX ≥ 32 °C, ~34 con HR ≥ 80 %, ~2.3 con TN ≤ 5 °C.

Mediana del sesgo / error absoluto, con estación más cercana a **0–60 km**:

| Umbral | Sesgo (días) | Error absoluto (días) |
|---|---:|---:|
| TX ≥ 30 °C | −0.7 | 4.3 |
| TX ≥ 32 °C | −0.7 | 3.0 |
| HR media diurna ≥ 80 % | −3.2 | 4.8 |
| TN ≤ 5 °C | −0.7 | 0.8 |

Con estación a **60–120 km**: error absoluto ~6.6 días (TX ≥ 30 °C), ~6.0 (TX ≥ 32 °C), ~5.0 (HR ≥ 80 %), ~1.0 (TN ≤ 5 °C).

La máxima queda bien calibrada gracias a la corrección por cuantiles. La HR alta **sigue subestimando** ~3 días por campaña: si un índice depende de ese umbral, conviene sensibilizar con `hr_estacion`.

---

## 4. Comparación rápida: método vs alternativas (Uruguay, promedio de tramos)

| Variable | Método | Estación sola | Open-Meteo sola | 50/50 (versión anterior) |
|---|---:|---:|---:|---:|
| TX diaria (°C) | **1.11** | 1.60 | 1.52 | 1.21 |
| TN diaria (°C) | **1.30** | 1.71 | 1.46 | 1.35 |
| HR diaria (%) | **3.60** | 5.12 | 4.22 | 3.84 |
| Lluvia 10 días (error rel.) | **33 %** | 41 % | 52 % | 34 % (IDW 3 pluv.) |

---

## 5. Brasil (referencia): Gurupi, Itumbiara, Planaltina, Toledo

Misma fórmula, aplicada a estimar cada estación INMET con sus vecinos + Open-Meteo. **No** es el error en el punto del cultivo cuando la estación está en el pueblo (ahí el error real es mucho menor).

| Sitio | Estación | Dist. sitio | Vecino más cercano | TX (°C) | TN (°C) | HR (%) | Lluvia 10 d |
|---|---|---:|---:|---:|---:|---:|---:|
| Gurupi (TO) | A019 | 2.6 km | 63 km | 0.95 | 0.71 | 3.29 | 43 % |
| Itumbiara (GO) | A035 | 3.2 km | 70 km | 0.83 | 0.64 | 3.41 | 43 % |
| Planaltina (DF) | A045 | 16.4 km | 39 km | 1.25 | 1.22 | 3.45 | 38 % |
| Toledo (PR) | A820 | 34.4 km | 106 km | 1.09 | 0.99 | 4.34 | 46 % |

**Uso práctico en Brasil:**

| Sitio | Recomendación | Error esperado en la chacra |
|---|---|---|
| Gurupi, Itumbiara | **Estación INMET sola** (está en la localidad) | Del orden del error de medición de la estación; la tabla de arriba **no** aplica |
| Planaltina | Estación sola (A045 a 16 km); en mínima preferir no diluir (altitud ~1030 m) | Similar: estación local |
| Toledo | **Fórmula** (A820 a 34 km y en Pane; chequear huecos / sumar A825) | ~ tabla Uruguay a 30–45 km, o fila A820 si hay que interpolar desde lejos |

---

## 6. Cómo leer estas tablas

1. **El error crece con la distancia**, sobre todo en lluvia y HR. En temperatura la fórmula se mantiene ~1.0–1.2 °C hasta 150 km.
2. **No hay medición en la chacra:** estos números son el error al estimar una estación con otras. Es la mejor cota disponible; el error real en chacra puede ser algo mayor o menor según microclima.
3. **Pocos pares &lt; 60 km en Uruguay** (7 pares convencionales). La parte cercana de la curva es la menos segura; a &lt; 10 km la estación sola puede ser tan buena como la mezcla.
4. **Lluvia diaria** no se recomienda como cantidad; sí como ocurrencia (CSI) o montos de 10 días / mes.
5. **Brasil tropical/cerrado** tiene más relieve y red más rala que Uruguay; la fórmula generaliza en orden de magnitud, pero en sitio con estación local conviene estación sola.

---

## 7. Archivos relacionados

- Criterio completo: `analisis_distancia_estaciones/CRITERIO_distancia_estaciones.md`
- Tablas de validación Uruguay: `analisis_distancia_estaciones/tablas_peso_distancia.md`
- Series diarias Uruguay: `analisis_distancia_estaciones/series_diarias_muestras.csv`
- Validación Brasil: `analisis_inmet_brasil/RESULTADOS_validacion_brasil.md`
