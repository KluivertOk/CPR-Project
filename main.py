import geopandas as gpd
import pickle
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as ex
from plotly import graph_objs as go
from ARIMA import predict_crime_rate
from shapely.geometry import Point
import yaml
from yaml.loader import SafeLoader
from LoginPage import login  # Importing the login function from login.py

# Load YAML configuration
with open('../CPR Project/login.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Perform login
login_success = login("login.yaml")

if login_success:
    # Load data
    data = pd.read_csv('CrimeIndex.csv')
    data['PercentageChange'] = ((data['Crime_index_2023'] - data['Crime_Index_2020']) / data['Crime_Index_2020']) * 100

    page = st.sidebar.radio("Select Page", ["Map", "Histogram"])

    if page == "Map":
        st.title('Crime Index Map')
        selected_country = st.selectbox("Select a country", data["Country"].unique())
        selected_data = data[data["Country"] == selected_country]

        if not selected_data.empty:
            fig = ex.choropleth(
                data,
                locations="Country",
                locationmode="country names",
                color="Crime_index_2023",
                color_continuous_scale="RdBu_r",
                title="Crime Index 2023 per 100,000",
                labels={"Crime_index_2023": "Crime_index_2023", "PercentageChange": "Percentage Change"},
            )

            st.plotly_chart(fig)

            selected_lat = selected_data["Country"].values[0]
            selected_lon = selected_data["Country"].values[0]

            custom_marker = go.Scattergeo(
                lon=[selected_lon],
                lat=[selected_lat],
                mode="markers",
                marker=dict(size=10, color="yellow", symbol="star"),
                text=selected_country,
                name="Country",
            )

            fig.add_trace(custom_marker)

            st.sidebar.title(f"Details for {selected_country}")
            st.subheader(f"Statistics for {selected_country}")
            st.sidebar.write(f"Crime Index 2020: {selected_data['Crime_Index_2020'].values[0]}")
            st.sidebar.write(f"Crime Index 2023: {selected_data['Crime_index_2023'].values[0]}")

            # Check if the column exists before accessing it
            if 'PercentageChange' in selected_data:
                st.sidebar.write(f"Percentage Change: {selected_data['PercentageChange'].values[0]}%")
                st.write(f"Percentage Change (2020-2023): {selected_data['PercentageChange'].values[0]:.2f}%")
            else:
                st.sidebar.warning("PercentageChange column not found.")

            st.subheader("Crime Rate Forecasting (2024-2026)")
            st.write(selected_data)
            forecast_df = predict_crime_rate(selected_country)
            st.write(forecast_df)

            # if st.sidebar.button('Logout'):
            #     login_success = False
            #     st.experimental_rerun()


        else:
            st.warning("No data available for the selected country.")

    elif page == 'Histogram':
        st.title('Crime Index Scatter Plot')

        # Corrected line to read from an Excel file
        df = pd.read_excel('Histogram_Stats.xlsx')

        geometry = [Point(xy) if pd.notna(xy) and len(xy) == 2 else Point(0, 0) for xy in
                    zip(df['Crime Index 2020 - 2023'], df['Year'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry)
        # Scatter Plot
        st.write("### Scatter Plot of Crime Index for Selected Country")
        scatter_fig = ex.scatter(
            gdf,
            x='Year',
            y='Crime Index 2020 - 2023',
            color='Country',
            title=f'Crime Index Scatter Plot for',
            labels={'Crime Index 2020 - 2023': 'Crime Rate'},
        )

        st.plotly_chart(scatter_fig)

# to run code type "streamlit run main.py" in terminal
