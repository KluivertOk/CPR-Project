import geopandas as gpd
import pandas as pd
import streamlit as st
import plotly.express as px


# Read the GeoJSON file for Ireland
ireland_geojson = gpd.read_file("ireland-counties.geojson")

# Read the DataFrame containing the crime index data for Ireland
crime_data = pd.read_csv("CrimeIndex.csv")

# Merge the GeoDataFrame with the crime data
ireland_geojson = ireland_geojson.merge(crime_data, left_on="name", right_on="Country", how="left")


# Create a GeoDataFrame for Dublin
dublin_data = pd.DataFrame({
    'City': ['Dublin'],
    'Latitude': [53.349805],
    'Longitude': [-6.26031]
})
dublin_gdf = gpd.GeoDataFrame(
    dublin_data,
    geometry=gpd.points_from_xy(dublin_data.Longitude, dublin_data.Latitude)
)

# Create the choropleth map
fig = px.choropleth_mapbox(
    ireland_geojson,
    geojson=ireland_geojson.geometry,
    locations=ireland_geojson.index,
    color='Crime_index_2023',
    color_continuous_scale="RdBu_r",
    mapbox_style="carto-positron",
    zoom=5,
    center={"lat": 53.349805, "lon": -6.26031},
    opacity=0.5,
    labels={'Crime_index_2023': 'Crime Index 2023'}

)


# Add Dublin marker to the map
fig.add_trace(
    px.scatter_mapbox(
        dublin_gdf,
        lat='Latitude',
        lon='Longitude',
        text='City',
        color_discrete_sequence=["yellow"],
        size_max=15
    ).data[0]
)

# Display the map
st.plotly_chart(fig)
