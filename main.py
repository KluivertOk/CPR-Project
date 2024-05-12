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
import os

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

        # Collaborative Features
        st.sidebar.title("Collaborative Features")

        # Check if the user is logged in
        if st.sidebar.checkbox("Logged in"):
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")

            if st.sidebar.button("Login"):
                # Your login logic here
                st.sidebar.success(f"Welcome back, {username}!")

                # Load comments from file if it exists
                if os.path.exists(f"{username}_comments.txt"):
                    with open(f"{username}_comments.txt", "r") as file:
                        comment_list = file.readlines()
                    comment_list = [comment.strip() for comment in comment_list]
                else:
                    comment_list = []  # Initialize the comment_list here

            # Commenting
            st.sidebar.subheader("Commenting")
            comment_input = st.text_area("Add a comment", height=100)

            if st.button("Submit Comment"):
                if 'comment_list' not in locals():
                    comment_list = []
                comment_list.append(comment_input)
                st.success("Comment submitted successfully!")

                # Save comments to file
                with open(f"{username}_comments.txt", "w") as file:
                    for comment in comment_list:
                        file.write(comment + "\n")

            # Display comments
            if 'comment_list' in locals() and comment_list:
                st.sidebar.subheader("Comments")
                for idx, comment in enumerate(comment_list, 1):
                    st.sidebar.write(f"Comment {idx}: {comment}")
        else:
            st.sidebar.warning("Please log in to access collaborative features.")

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

            # Calculate percentage difference between the first and last predicted values for ARIMA
            percentage_difference_arima = ((forecast_df['Predicted'].iloc[-1] - forecast_df['Predicted'].iloc[0]) /
                                           forecast_df['Predicted'].iloc[-1]) * 100

            # Calculate percentage difference between the first and last predicted values for Prophet
            percentage_difference_prophet = ((prophet_df['Predicted'].iloc[-1] - prophet_df['Predicted'].iloc[0]) /
                                             prophet_df['Predicted'].iloc[-1]) * 100

            # Display percentage difference for ARIMA forecast
            st.subheader("Percentage Difference in Predicted Crime Index (ARIMA)")
            st.write(f"Percentage Difference (ARIMA): {percentage_difference_arima:.2f}%")

            # Display percentage difference for Prophet forecast
            st.subheader("Percentage Difference in Predicted Crime Index (Prophet)")
            st.write(f"Percentage Difference (Prophet): {percentage_difference_prophet:.2f}%")

            # Generate a range of dates for the prediction period
            prediction_dates = pd.date_range(start='2022-01-01', end='2026-12-31', freq='Y')

            # Check if the length of prediction_dates matches the length of forecast_df index
            if len(prediction_dates) == len(forecast_df):
                # Set the prediction dates as the index for the forecast dataframes
                forecast_df.index = prediction_dates
                prophet_df.index = prediction_dates

                # Create a line plot for ARIMA forecast
                st.subheader("ARIMA Forecasted Crime Index")
                plt.figure(figsize=(10, 6))
                plt.plot(forecast_df.index, forecast_df['Predicted'], marker='o', linestyle='-')
                plt.title("ARIMA Forecasted Crime Index (2022-2026)")
                plt.xlabel("Year")
                plt.ylabel("Crime Index")
                plt.xticks(forecast_df.index, [str(year)[:4] for year in forecast_df.index], rotation=45)
                plt.grid(True)
                st.pyplot(plt)

                # Create a line plot for Prophet forecast
                st.subheader("Prophet Forecasted Crime Index")
                plt.figure(figsize=(10, 6))
                plt.plot(prophet_df.index, prophet_df['Predicted'], marker='o', linestyle='-')
                plt.title("Prophet Forecasted Crime Index (2022-2026)")
                plt.xlabel("Year")
                plt.ylabel("Crime Index")
                plt.xticks(prophet_df.index, [str(year)[:4] for year in prophet_df.index], rotation=45)
                plt.grid(True)
                st.pyplot(plt)
            else:
                st.error("Length mismatch: Prediction dates do not match the length of the forecast dataframe.")

        else:
            st.warning("No data available for the selected country.")
    elif page == 'Ireland':
        Ireland_Map.show_map()
        st.title('Crime Statistics by Region')

        # Display population size and facts about Ireland in the side menu
        st.sidebar.title("Ireland Population and Facts")
        st.sidebar.subheader("Population Size")
        st.sidebar.write("The population of Ireland is approximately 4.9 million.")

        st.sidebar.subheader("Facts about Ireland")
        st.sidebar.write("1. Ireland is known as the Emerald Isle due to its lush greenery.")
        st.sidebar.write("2. The country has a rich history and cultural heritage, with many ancient landmarks and traditions.")
        st.sidebar.write("3. Dublin is the capital city of Ireland and is famous for its vibrant nightlife and historic landmarks like Trinity College and the Guinness Storehouse.")
        st.sidebar.write("4. Ireland is renowned for its literature, music, and folklore, with famous literary figures such as James Joyce, W.B. Yeats, and Samuel Beckett.")
        st.sidebar.write("5. The Irish economy has undergone significant growth in recent decades, with industries such as technology, pharmaceuticals, and finance driving economic development.")

        # Add a selection dropdown for regions
        selected_region = st.selectbox("Select a region", ["EASTERN REGION", "SOUTHERN REGION", "NORTHERN REGION", "WESTERN REGION"])
        if selected_region == "EASTERN REGION":
            # Display the histogram of offence frequencies for the EASTERN REGION
            st.title('Frequency of Offences in the EASTERN REGION')
            df_offences = pd.read_csv("Ireland Data.csv")
            eastern_region_data = df_offences[df_offences['REGION'] == 'EASTERN REGION']
            quarter_columns = eastern_region_data.columns[5:]
            eastern_region_data[quarter_columns] = eastern_region_data[quarter_columns].apply(pd.to_numeric,errors='coerce')
            offence_counts = eastern_region_data.groupby('TYPE OF OFFENCE')[quarter_columns].sum().sum(axis=1)
            offence_counts = offence_counts.sort_values(ascending=True)
            plt.figure(figsize=(16, 10))  # Adjust the width here
            offence_counts.plot(kind='barh', color='skyblue')
            plt.title('Frequency of Offences in the EASTERN REGION from 2003Q1 to 2019Q3', fontsize=18)
            plt.xlabel('Frequency', fontsize=18)
            plt.ylabel('Type of Offence', fontsize=18)
            plt.yticks(fontsize=12)
            plt.tight_layout()
            st.pyplot(plt)
            st.write("The EASTERN REGION's predominant crimes are THEFT AND RELATED OFFENCES, PUBLIC ORDER AND OTHER SOCIAL CODE OFFENCES and DAMAGE TO PROPERTY AND ENVIRONMENT")
            st.write("The reasons this may be could be because the Eastern Region, particularly Dublin, has a higher population density and is more urbanized compared to other regions in Ireland.")
            st.write("Higher population density often correlates with increased opportunities for theft, public order offenses, and property damage.")

        elif selected_region == "SOUTHERN REGION":
            # Display the histogram of offence frequencies for the SOUTHERN REGION
            st.title('Frequency of Offences in the SOUTHERN REGION')
            df_offences = pd.read_csv("Ireland Data.csv")
            southern_region_data = df_offences[df_offences['REGION'] == 'SOUTHERN REGION']
            quarter_columns_southern = southern_region_data.columns[5:]
            southern_region_data[quarter_columns_southern] = southern_region_data[quarter_columns_southern].apply(pd.to_numeric, errors='coerce')
            offence_counts_southern = southern_region_data.groupby('TYPE OF OFFENCE')[quarter_columns_southern].sum().sum(axis=1)
            offence_counts_southern = offence_counts_southern.sort_values(ascending=True)
            plt.figure(figsize=(16, 10))  # Adjust the width here
            offence_counts_southern.plot(kind='barh', color='skyblue')
            plt.title('Frequency of Offences in the SOUTHERN REGION from 2003Q1 to 2019Q3', fontsize=18)
            plt.xlabel('Frequency', fontsize=18)
            plt.ylabel('Type of Offence', fontsize=18)
            plt.yticks(fontsize=12)
            plt.tight_layout()
            st.pyplot(plt)
            st.write("The SOUTHERN REGION's predominant crimes are THEFT AND RELATED OFFENCES, PUBLIC ORDER AND OTHER SOCIAL CODE OFFENCES and DAMAGE TO PROPERTY AND ENVIRONMENT")
            st.write("Urban areas within the Southern Region, such as Cork and Limerick, may have higher population densities and more significant commercial activities, making them attractive targets for theft-related crimes")
            st.write("Major transportation networks, ports, and routes in the Southern Region can facilitate easier movement for criminals, making it a focal point for theft-related crimes.")

        elif selected_region == "NORTHERN REGION":
            # Display the histogram of offence frequencies for the NORTHERN REGION
            st.title('Frequency of Offences in the NORTHERN REGION')
            df_offences = pd.read_csv("Ireland Data.csv")
            northern_region_data = df_offences[df_offences['REGION'] == 'NORTHERN REGION']
            quarter_columns_northern = northern_region_data.columns[5:]
            northern_region_data[quarter_columns_northern] = northern_region_data[quarter_columns_northern].apply(pd.to_numeric, errors='coerce')
            offence_counts_northern = northern_region_data.groupby('TYPE OF OFFENCE')[quarter_columns_northern].sum().sum(axis=1)
            offence_counts_northern = offence_counts_northern.sort_values(ascending=True)
            # Plotting
            plt.figure(figsize=(16, 10))  # Adjust the width here
            offence_counts_northern.plot(kind='barh', color='skyblue')
            plt.title('Frequency of Offences in the NORTHERN REGION from 2003Q1 to 2019Q3', fontsize=18)
            plt.xlabel('Frequency', fontsize=18)
            plt.ylabel('Type of Offence', fontsize=18)
            plt.yticks(fontsize=12)
            plt.tight_layout()
            st.pyplot(plt)
            st.write("The NORTHERN REGION's predominant crimes are THEFT AND RELATED OFFENCES, PUBLIC ORDER AND OTHER SOCIAL CODE OFFENCES and DAMAGE TO PROPERTY AND ENVIRONMENT")
            st.write("The Northern Region comprises predominantly rural and border areas with limited resources, remote communities, and challenges related to cross-border activities.")
            st.write("These areas might be more susceptible to theft-related crimes, public order offenses, and property damage due to reduced police presence, limited infrastructure, and geographical vulnerabilities.")

        elif selected_region == "WESTERN REGION":
            # Display the histogram of offence frequencies for the WESTERN REGION
            st.title('Frequency of Offences in the WESTERN REGION')
            df_offences = pd.read_csv("Ireland Data.csv")
            western_region_data = df_offences[df_offences['REGION'] == 'WESTERN REGION']
            quarter_columns_western = western_region_data.columns[5:]
            western_region_data[quarter_columns_western] = western_region_data[quarter_columns_western].apply(pd.to_numeric,errors='coerce')
            offence_counts_western = western_region_data.groupby('TYPE OF OFFENCE')[quarter_columns_western].sum().sum(axis=1)
            offence_counts_western = offence_counts_western.sort_values(ascending=True)
            plt.figure(figsize=(16, 14))  # Adjust the width here
            offence_counts_western.plot(kind='barh', color='skyblue')

            plt.title('Frequency of Offences in the WESTERN REGION from 2003Q1 to 2019Q3', fontsize=18)
            plt.xlabel('Frequency', fontsize=18)
            plt.ylabel('Type of Offence', fontsize=18)
            plt.yticks(fontsize=12)
            plt.tight_layout()
            st.pyplot(plt)
            st.write("The WESTERN REGION's predominant crimes are THEFT AND RELATED OFFENCES, PUBLIC ORDER AND OTHER SOCIAL CODE OFFENCES and DAMAGE TO PROPERTY AND ENVIRONMENT")
            st.write( "The Western Region consists of predominantly rural, coastal, and remote areas with dispersed populations, limited infrastructure, and reduced police presence.")
            st.write("These geographical factors can contribute to increased opportunities for theft-related crimes, public order offenses, and property damage due to limited surveillance and access to resources.")

        # to run code type "streamlit run main.py" in terminal
