### THAILAND'S TEMPERATURE AND RAINFALL BY PROVINCES (2016–2025)

Author: Atiq Kainan Ahmed. Email: atiqka@yahoo.com

This Python script uses Google Earth Engine (GEE) to calculate the average temperature and rainfall for each Thai province (Admin level 1) over 2016–2025. It tests the spatial pattern of both variables with Moran's I and exports a side-by-side map as a PNG.


## What it does

Initializes Earth Engine with your Google Cloud project.
Loads two climate datasets for 2016-01-01 to 2025-12-31:
Temperature: ERA5-Land monthly aggregated 2 m air temperature (ECMWF/ERA5_LAND/MONTHLY_AGGR), averaged over all months.
Rainfall: CHIRPS daily precipitation (UCSB-CHG/CHIRPS/DAILY), summed over the whole period.
Loads Thailand province polygons from a GEE asset and calculates the mean value per province (reduceRegions, 5 km scale).
Converts temperature from Kelvin to °C and rainfall to the plotted unit.
Joins the results to a GADM province shapefile on NAME_1.
Calculates Moran's I (Queen contiguity, row-standardized weights) for temperature and rainfall to check for spatial autocorrelation.
Reprojects to Web Mercator (EPSG:3857) and plots two maps side by side: temperature (inferno_r) and rainfall (viridis_r), each with a horizontal colorbar.
Saves the figure as a 300 dpi PNG.

Output is shown here https://github.com/atiqka/THA_tmp-pr_2016-2025/blob/main/thailand_admin1_temp_rainfall_combined_2016-2025.png


The script also prints Moran's I and the simulated p-value for each variable:

Temperature Moran's I: <value>, p=<value>
Rainfall Moran's I: <value>, p=<value>

A positive I with a small p-value means neighbouring provinces have similar values (spatial clustering).

## Requirements

Python 3.9+
A Google Earth Engine account and a Google Cloud project registered for Earth Engine
Packages: earthengine-api, geopandas, pandas, numpy, matplotlib, libpysal, esda

bash
pip install earthengine-api geopandas pandas numpy matplotlib libpysal esda

## Setup

1. Authenticate with Earth Engine (first time only)
bash
earthengine authenticate

2. Set your project

In the script, replace the project ID with your own:

python
ee.Initialize(project='your-project-id')

3. Upload the province asset to GEE

Upload a Thailand Admin 1 (province) layer to your GEE assets and point the script to it:

python
provinces = ee.FeatureCollection("projects/your-project-id/assets/THA_Admin1")

The asset must contain a NAME_1 property so it matches the shapefile (step 4).

4. Download the GADM shapefile

Download the Thailand shapefile (GADM 4.1, gadm41_THA_shp.zip) from gadm.org. Then set the local path in the script:

python
shp_path = "/path/to/gadm41_THA_shp.zip"
provinces_gdf = gpd.read_file(shp_path, layer="gadm41_THA_1")

Also update the output path in plt.savefig(...) near the end of the script.

Usage

bash
python thailand_temp_rainfall.py

Rename the command to match your script's file name. The Earth Engine calls use getInfo(), so the script waits for the results and can take a minute or two.

## Configuration

Setting	Where	Default
Period	filterDate(...)	2016-01-01 to 2025-12-31
Reduction scale	scale=5000	5 km
Temperature colormap	cmap_temp	inferno_r
Rainfall colormap	cmap_rain	viridis_r
Figure size / resolution	figsize, dpi	20 x 10 in, 300 dpi
Data sources
ERA5-Land Monthly Aggregated: ECMWF / Copernicus Climate Change Service, via the Earth Engine catalog
CHIRPS Daily: Climate Hazards Group (UCSB), via the Earth Engine catalog
Province boundaries: GADM 4.1 (Thailand, level 1)

Please credit the data providers and check each source's terms of use.

## Notes and limitations

Rainfall unit: CHIRPS is in mm/day. The script sums 10 years of daily values and divides by 10, which gives an average of roughly mm per year, but the code and the map label call it cm. To get true cm per year, divide by 100 instead of 10 (rain_df["rainfall_cm"] = (rain_df["mean"] / 100).round(0)). Check this before you publish the map.
Province names in the GEE asset and in the GADM shapefile must match exactly for the merge on NAME_1. Provinces that do not match are dropped by the merge.
The temperature is a mean of monthly means, and the rainfall is a mean over the province polygon at 5 km scale. Small provinces are represented by few pixels.
Moran's I is shown as optional diagnostics. Results depend on the spatial weights (Queen contiguity here).
The Earth Engine project ID and the local file paths in the script are specific to one machine. Change them before running.

## License

MIT License

Copyright (c) 2026 Atiq Kainan Ahmed.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
