import streamlit as st
import pandas as pd
import plotly.express as px
import json


def show_map():
    # Sample data for the provinces and their coordinates
    data = {
        'Province': ['Dublin', 'Galway', 'Cork', 'Belfast'],
        'Latitude': [53.3498, 53.2707, 51.8969, 54.5973],
        'Longitude': [-6.2603, -9.0568, -8.4863, -5.9301],
        'Region': ['Eastern', 'Western', 'Southern', 'Northern'],
        'Description': [
            'Capital city of Ireland and the largest city in the Eastern region.',
            'A vibrant city located in the Western region known for its arts and culture.',
            'A coastal city in the Southern region famous for its food and music.',
            'The capital and largest city of Northern Ireland, rich in history.'
        ]
    }
    df = pd.DataFrame(data)

    # Define the boundaries of Ireland
    ireland_geojson = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"name": "Leinster"}, "geometry": {"type": "Polygon", "coordinates": [
                [[-6.14, 53.51], [-6.14, 52.86], [-5.41, 52.86], [-5.41, 53.51], [-6.14, 53.51]]]}},
            {"type": "Feature", "properties": {"name": "Munster"}, "geometry": {"type": "Polygon", "coordinates": [
                [[-9.83, 52.14], [-9.83, 51.43], [-8.29, 51.43], [-8.29, 52.14], [-9.83, 52.14]]]}},
            {"type": "Feature", "properties": {"name": "Connacht"}, "geometry": {"type": "Polygon", "coordinates": [
                [[-10.5, 54.0], [-10.5, 52.96], [-8.1, 52.96], [-8.1, 54.0], [-10.5, 54.0]]]}},
            {"type": "Feature", "properties": {"name": "Ulster"}, "geometry": {"type": "Polygon", "coordinates": [
                [[-8.25, 55.38], [-8.25, 53.99], [-6.24, 53.99], [-6.24, 55.38], [-8.25, 55.38]]]}}
        ]
    }

    # Convert geojson to string
    ireland_geojson_str = json.dumps(ireland_geojson)

    # Create a new DataFrame for scatter plot
    df_scatter = pd.DataFrame({
        'Latitude': df['Latitude'],
        'Longitude': df['Longitude'],
        'HoverInfo': df['Province'] + ' (' + df['Region'] + ')',
        'Description': df['Description']
    })

    # Create the Streamlit app
    st.title("Ireland Map")

    # Plot the map
    fig = px.choropleth_mapbox(
        data_frame=None,
        geojson=ireland_geojson_str,
        locations=[feature["properties"]["name"] for feature in ireland_geojson["features"]],
        color=[1, 2, 3, 4],  # Dummy color data for demonstration
        color_discrete_map={1: "blue", 2: "green", 3: "yellow", 4: "red"},  # Dummy color map for demonstration
        mapbox_style="carto-positron",
        zoom=5,
        center={"lat": 53.3498, "lon": -7.2603},
        opacity=0.5,
        labels={'color': 'Province'}
    )

    # Highlight provinces using scatter plot
    fig_provinces = px.scatter_mapbox(df_scatter,
                                      lat="Latitude",
                                      lon="Longitude",
                                      hover_name="HoverInfo",
                                      hover_data={"Description": True},  # Include description in hover data
                                      zoom=5)

    # Update the layout of the scatter plot to remove margins
    fig_provinces.update_layout(mapbox_style="open-street-map")
    fig_provinces.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Add the scatter plot to the main map
    fig.add_trace(fig_provinces.data[0])

    # Display the map
    st.plotly_chart(fig)
