import ee
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from libpysal import weights
from esda import Moran
import matplotlib.colors as mcolors

# 1. Initialize Earth Engine
ee.Initialize(project='atiq-project-july2025')

# 2a. ERA5-Land monthly aggregated 2m air temperature dataset
era5 = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR") \
            .filterDate("2016-01-01", "2025-12-31") \
            .select("temperature_2m")
avg_temp = era5.mean()

# 2b. CHIRPS rainfall dataset
chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
            .filterDate("2016-01-01", "2025-12-31")
total_rainfall = chirps.sum()

# 3. Load polygons (Thailand Admin1 asset)
provinces = ee.FeatureCollection("projects/atiq-project-july2025/assets/THA_Admin1")

# 4a. Aggregate temperature
province_temp = avg_temp.reduceRegions(
    collection=provinces,
    reducer=ee.Reducer.mean(),
    scale=5000
)
temp_dict = province_temp.getInfo()
temp_df = pd.DataFrame([f["properties"] for f in temp_dict["features"]])
temp_df["temp_celsius"] = (temp_df["mean"] - 273.15).round(1)

# 4b. Aggregate rainfall
province_rain = total_rainfall.reduceRegions(
    collection=provinces,
    reducer=ee.Reducer.mean(),
    scale=5000
)
rain_dict = province_rain.getInfo()
rain_df = pd.DataFrame([f["properties"] for f in rain_dict["features"]])
rain_df["rainfall_cm"] = (rain_df["mean"] / 10).round(0)

# 5. Load shapefile (Thailand Admin1)
shp_path = "/Users/atiq/Pyvs_2026/gadm41_THA_shp.zip"
provinces_gdf = gpd.read_file(shp_path, layer="gadm41_THA_1")

# 6. Merge both datasets (Admin1 uses NAME_1)
provinces_gdf = provinces_gdf.merge(temp_df, on="NAME_1")
provinces_gdf = provinces_gdf.merge(rain_df, on="NAME_1")

# 7. Moran’s I (optional diagnostics)
w = weights.Queen.from_dataframe(provinces_gdf)
w.transform = "r"
moran_temp = Moran(provinces_gdf["temp_celsius"], w)
moran_rain = Moran(provinces_gdf["rainfall_cm"], w)
print(f"Temperature Moran's I: {moran_temp.I:.3f}, p={moran_temp.p_sim:.4f}")
print(f"Rainfall Moran's I: {moran_rain.I:.3f}, p={moran_rain.p_sim:.4f}")

# 8. Reproject
provinces_gdf = provinces_gdf.to_crs(epsg=3857)

# 9. Plot side-by-side maps
fig, axes = plt.subplots(1, 2, figsize=(20, 10))

# --- Temperature map ---
values_temp = provinces_gdf["temp_celsius"].fillna(0).values
norm_temp = mcolors.Normalize(vmin=values_temp.min(), vmax=values_temp.max())
cmap_temp = plt.get_cmap("inferno_r")
provinces_gdf.plot(ax=axes[0],
                   color=[cmap_temp(norm_temp(v)) for v in values_temp],
                   edgecolor="lightgray", linewidth=0.3)
axes[0].set_title("Thailand Avg Annual Temperature (2016–2025)",
                  fontsize=14, weight="bold", pad=20)
axes[0].axis("off")
sm_temp = plt.cm.ScalarMappable(cmap=cmap_temp, norm=norm_temp)
sm_temp.set_array([])
cbar_temp = fig.colorbar(sm_temp, ax=axes[0], orientation="horizontal",
                         fraction=0.025, pad=0.05)
cbar_temp.ax.set_title("Temperature (°C)", fontsize=11, weight="bold", pad=10)

# --- Rainfall map ---
values_rain = provinces_gdf["rainfall_cm"].fillna(0).values
norm_rain = mcolors.Normalize(vmin=values_rain.min(), vmax=values_rain.max())
cmap_rain = plt.get_cmap("viridis_r")
provinces_gdf.plot(ax=axes[1],
                   color=[cmap_rain(norm_rain(v)) for v in values_rain],
                   edgecolor="lightgray", linewidth=0.3)
axes[1].set_title("Thailand Avg Annual Rainfall (2016–2025)",
                  fontsize=14, weight="bold", pad=20)
axes[1].axis("off")
sm_rain = plt.cm.ScalarMappable(cmap=cmap_rain, norm=norm_rain)
sm_rain.set_array([])
cbar_rain = fig.colorbar(sm_rain, ax=axes[1], orientation="horizontal",
                         fraction=0.025, pad=0.05)
cbar_rain.ax.set_title("Rainfall (cm)", fontsize=11, weight="bold", pad=10)

# 10. Save and show
plt.tight_layout()
plt.savefig("/Users/atiq/Pyvs_2026/thailand_admin1_temp_rainfall_combined_2016-2025.png",
            dpi=300, bbox_inches="tight")
plt.show()
