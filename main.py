import geopandas as gpd
import pickle
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as ex
from matplotlib import pyplot as plt
from plotly import graph_objs as go
from ARIMA import predict_crime_rate
from Prophet import predict_crime_rate_prophet
import Ireland_Map
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

    page = st.sidebar.radio("Select Page", ["Map", "Ireland"])

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

            # Read population data from Prediction.csv
            population_data = pd.read_csv('Prediction.csv')

            # Remove commas from the population column and convert it to numeric
            population_data['Population'] = population_data['Population'].str.replace(',', '')
            population_data['Population'] = pd.to_numeric(population_data['Population'], errors='coerce')

            population = population_data.loc[population_data['Country'] == selected_country, 'Population'].iloc[-1]

            # Replace NaN values with a default population value or any other strategy
            population_data['Population'].fillna(0, inplace=True)

            # Convert the 'Population' column to float
            population_data['Population'] = population_data['Population'].astype(float)

            # Call predict_crime_rate function and store the results
            forecast_df, crime_index = predict_crime_rate(selected_country, population_data, file_path='Prediction.csv')

            # Calculate crime index for ARIMA forecast results
            forecast_df['Crime_Index'] = crime_index

            st.write(forecast_df)

            prophet_df = predict_crime_rate_prophet(selected_country, population_data, file_path='Prediction.csv')

            prophet_df['Crime_Index'] = (prophet_df['Predicted'] / 100000) * population

            st.write(prophet_df)

        else:
            st.warning("No data available for the selected country.")

    elif page == 'Ireland':
        Ireland_Map.show_map()
        st.title('Ireland Data')

        # Display the histogram of offence frequencies for the EASTERN REGION
        st.title('Frequency of Offences in the EASTERN REGION')
        # Read the CSV file
        df_offences = pd.read_csv("Ireland Data.csv")
        # Filter data for the EASTERN REGION
        eastern_region_data = df_offences[df_offences['REGION'] == 'EASTERN REGION']
        # Select only the columns containing quarter data
        quarter_columns = eastern_region_data.columns[5:]
        # Convert quarter data to integer type and sum occurrences across all quarters
        eastern_region_data[quarter_columns] = eastern_region_data[quarter_columns].apply(pd.to_numeric,
                                                                                          errors='coerce')
        offence_counts = eastern_region_data.groupby('TYPE OF OFFENCE')[quarter_columns].sum().sum(axis=1)
        # Sort offences by frequency in descending order
        offence_counts = offence_counts.sort_values(ascending=False)
        # Plotting
        offence_counts.plot(kind='bar', figsize=(16, 8), color='skyblue')
        plt.title('Frequency of Offences in the EASTERN REGION from 2003Q1 to 2019Q3')
        plt.xlabel('Type of Offence')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(plt)  # Display the histogram using Streamlit's pyplot function

        ("The EASTERN REGION's prodominant crimes are THEFT AND RELATED OFFENCES, PUBLIC ORDER AND OTHER SOCIAL CODE OFFENCES and DAMAGE TO PROPERTY AND ENVIRONMENT")
        ("The reasons this maybe coould be because the Eastern Region, particularly Dublin, has a higher population density and is more urbanized compared to other regions in Ireland.")
        ("Higher population density often correlates with increased opportunities for theft, public order offenses, and property damage.")


        # Display the histogram of offence frequencies for the SOUTHERN REGION
        st.title('Frequency of Offences in the SOUTHERN REGION')
        # Read the CSV file
        df_offences = pd.read_csv("Ireland Data.csv")
        # Filter data for the SOUTHERN REGION
        southern_region_data = df_offences[df_offences['REGION'] == 'SOUTHERN REGION']
        # Select only the columns containing quarter data
        quarter_columns_southern = southern_region_data.columns[5:]
        # Convert quarter data to integer type and sum occurrences across all quarters
        southern_region_data[quarter_columns_southern] = southern_region_data[quarter_columns_southern].apply(
            pd.to_numeric, errors='coerce')
        offence_counts_southern = southern_region_data.groupby('TYPE OF OFFENCE')[quarter_columns_southern].sum().sum(
            axis=1)
        # Sort offences by frequency in descending order
        offence_counts_southern = offence_counts_southern.sort_values(ascending=False)
        # Plotting
        offence_counts_southern.plot(kind='bar', figsize=(16, 8), color='skyblue')
        plt.title('Frequency of Offences in the SOUTHERN REGION from 2003Q1 to 2019Q3')
        plt.xlabel('Type of Offence')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(plt)  # Display the histogram using Streamlit's pyplot function

        ("The SOUTHERN REGION's prodominant crimes are THEFT AND RELATED OFFENCES, PUBLIC ORDER AND OTHER SOCIAL CODE OFFENCES and DAMAGE TO PROPERTY AND ENVIRONMENT")
        ("Urban areas within the Southern Region, such as Cork and Limerick, may have higher population densities and more significant commercial activities, making them attractive targets for theft-related crimes")
        ("Major transportation networks, ports, and routes in the Southern Region can facilitate easier movement for criminals, making it a focal point for theft-related crimes.")

        # Display the histogram of offence frequencies for the NORTHERN REGION
        st.title('Frequency of Offences in the NORTHERN REGION')
        # Read the CSV file
        df_offences = pd.read_csv("Ireland Data.csv")
        # Filter data for the NORTHERN REGION
        northern_region_data = df_offences[df_offences['REGION'] == 'NORTHERN REGION']
        # Select only the columns containing quarter data
        quarter_columns_northern = northern_region_data.columns[5:]
        # Convert quarter data to integer type and sum occurrences across all quarters
        northern_region_data[quarter_columns_northern] = northern_region_data[quarter_columns_northern].apply(
            pd.to_numeric, errors='coerce')
        offence_counts_northern = northern_region_data.groupby('TYPE OF OFFENCE')[quarter_columns_northern].sum().sum(
            axis=1)
        # Sort offences by frequency in descending order
        offence_counts_northern = offence_counts_northern.sort_values(ascending=False)
        # Plotting
        offence_counts_northern.plot(kind='bar', figsize=(16, 8), color='skyblue')
        plt.title('Frequency of Offences in the NORTHERN REGION from 2003Q1 to 2019Q3')
        plt.xlabel('Type of Offence')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(plt)  # Display the histogram using Streamlit's pyplot function

        ("The NORTHERN REGION's prodominant crimes are THEFT AND RELATED OFFENCES, PUBLIC ORDER AND OTHER SOCIAL CODE OFFENCES and DAMAGE TO PROPERTY AND ENVIRONMENT")
        ("The Northern Region comprises predominantly rural and border areas with limited resources, remote communities, and challenges related to cross-border activities.")
        ("These areas might be more susceptible to theft-related crimes, public order offenses, and property damage due to reduced police presence, limited infrastructure, and geographical vulnerabilities.")

        # Display the histogram of offence frequencies for the WESTERN REGION
        st.title('Frequency of Offences in the WESTERN REGION')
        # Read the CSV file
        df_offences = pd.read_csv("Ireland Data.csv")
        # Filter data for the WESTERN REGION
        western_region_data = df_offences[df_offences['REGION'] == 'WESTERN REGION']
        # Select only the columns containing quarter data
        quarter_columns_western = western_region_data.columns[5:]
        # Convert quarter data to integer type and sum occurrences across all quarters
        western_region_data[quarter_columns_western] = western_region_data[quarter_columns_western].apply(pd.to_numeric,
                                                                                                          errors='coerce')
        offence_counts_western = western_region_data.groupby('TYPE OF OFFENCE')[quarter_columns_western].sum().sum(
            axis=1)
        # Sort offences by frequency in descending order
        offence_counts_western = offence_counts_western.sort_values(ascending=False)
        # Plotting
        offence_counts_western.plot(kind='bar', figsize=(16, 8), color='skyblue')
        plt.title('Frequency of Offences in the WESTERN REGION from 2003Q1 to 2019Q3')
        plt.xlabel('Type of Offence')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(plt)  # Display the histogram using Streamlit's pyplot function

        ("The WESTEN REGION's prodominant crimes are THEFT AND RELATED OFFENCES, PUBLIC ORDER AND OTHER SOCIAL CODE OFFENCES and DAMAGE TO PROPERTY AND ENVIRONMENT")
        ("The Western Region consists of predominantly rural, coastal, and remote areas with dispersed populations, limited infrastructure, and reduced police presence.")
        ("These geographical factors can contribute to increased opportunities for theft-related crimes, public order offenses, and property damage due to limited surveillance and access to resources.")

    # to run code type "streamlit run main.py" in terminal
