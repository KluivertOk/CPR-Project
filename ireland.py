import geopandas as gpd
import pandas as pd
import plotly.express as px

# Read the GeoJSON file into a GeoDataFrame
ireland_geojson = gpd.read_file("ireland-counties.geojson")

# Read the additional data file containing region names
region_data = pd.read_csv("Ireland Data.csv")

# Check the column names of both DataFrames
print("ireland_geojson columns:", ireland_geojson.columns)
print("region_data columns:", region_data.columns)

# Make sure the 'REGION' column exists in the GeoDataFrame
if 'REGION' not in ireland_geojson.columns:
    raise ValueError("The 'REGION' column does not exist in the ireland_geojson GeoDataFrame.")

# Merge the region data with the GeoDataFrame
ireland_geojson = ireland_geojson.merge(region_data, on="REGION", how="left")

# Optionally, inspect the merged GeoDataFrame
print(ireland_geojson.head())

# Create the choropleth map
fig = px.choropleth_mapbox(
    ireland_geojson,
    geojson=ireland_geojson.geometry,
    locations=ireland_geojson.index,
    color='GARDA DIVISION',  # Change 'region_name' to the column containing region names
    mapbox_style="carto-positron",
    zoom=5,
    center={"lat": 53.349805, "lon": -6.26031},
    opacity=0.5,
    labels={'GARDA DIVISION': 'REGION'}  # Adjust label as needed
)

# Show the map
fig.show()
