"""Descarga ERA5-Land (serie temporal horaria de un punto) desde el Climate Data Store de Copernicus.

Requisitos previos (una sola vez):
  1. Cuenta en https://cds.climate.copernicus.eu
  2. Aceptar la licencia en la pestaña "Download" de
     https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries
  3. Archivo ~/.cdsapirc con:
        url: https://cds.climate.copernicus.eu/api
        key: <tu token personal, sale en tu perfil del CDS>
  4. pip install cdsapi

Uso: python descargar_era5_land.py
"""
from pathlib import Path

import cdsapi

OUT = Path(__file__).resolve().parent / "datos_era5_land"
OUT.mkdir(exist_ok=True)

# ERA5-Land solo tiene datos sobre tierra. El punto de grilla más cercano a la estación Colonia
# (-34.4519, -57.7678) es -34.5/-57.8, que cae en el Río de la Plata y viene vacío; se usa el punto
# de tierra más cercano, -34.4/-57.8 (~6.5 km al NNO de la estación).
LAT, LON = -34.40, -57.80

VARIABLES = [
    "2m_temperature",
    "2m_dewpoint_temperature",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "total_precipitation",
]
PERIODOS = {"2017_2019": "2017-01-01/2019-12-31", "2024_2025": "2024-01-01/2025-12-31"}

cliente = cdsapi.Client()
for nombre, rango in PERIODOS.items():
    destino = OUT / f"era5_land_colonia_{nombre}.zip"
    if destino.exists():
        print("ya existe", destino)
        continue
    cliente.retrieve(
        "reanalysis-era5-land-timeseries",
        {
            "variable": VARIABLES,
            "location": {"latitude": LAT, "longitude": LON},
            "date": [rango],
            "data_format": "csv",
        },
        str(destino),
    )
    print("descargado", destino)
