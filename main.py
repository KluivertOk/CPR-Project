import geopandas as gpd
import pickle
from pathlib import Path
import pandas as pd
import stauth
import streamlit as st
import plotly.express as ex
import streamlit_authenticator as stauch
from plotly import graph_objs as go
from prediction import predict_crime_rate
from statsmodels.tsa.arima.model import ARIMA
from shapely.geometry import Point

data = pd.read_csv('CrimeIndex.csv')
data['PercentageChange'] = ((data['Crime_index_2023'] - data['Crime_Index_2020']) / data['Crime_Index_2020']) * 100

page = st.sidebar.radio("Select Page", ["Map", "Histogram"])

# names = ["Kluivert Okobi", "Kluvz Lean"]
# usernames = ["kokobi", "klean"]
#
# file_path = Path(__file__).parent / "hashed_pw.pk1"
# with file_path.open("rb") as file:
#     hashed_passwords = pickle.load(file)
#
# authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
#                                     "sales_dashboard", "abcedef", cookie_expiry_days=30)
#
# name, authentication_status, usernames = authenticator.login("Login", "main")
#
# if authentication_status == False:
#     st.error("Username/Password is incorrect")
#
# if authentication_status == None:
#     st.warning("Please enter a username and password")
#
# if authentication_status:

selected_country = None

# Page 1: Display the choropleth map and select a country
if page == 'Map':
    st.title('Crime Index Map')
    selected_country = st.selectbox("Select a country", data["Country"].unique())

    selected_data = data[data["Country"] == selected_country]

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

    if selected_country and not selected_data.empty:  # Check if selected_data is not empty
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

        if selected_country:
            st.sidebar.title(f"Details for {selected_country}")
        selected_data = data[data["Country"] == selected_country]

        st.subheader(f"Statistics for {selected_country}")
        st.sidebar.write(f"Crime Index 2020: {selected_data['Crime_Index_2020'].values[0]}")
        st.sidebar.write(f"Crime Index 2023: {selected_data['Crime_index_2023'].values[0]}")
        st.sidebar.write(f"Percentage Change: {selected_data['PercentageChange'].values[0]}%")
        st.write(f"Percentage Change (2020-2023): {selected_data['PercentageChange'].values[0]:.2f}%")

        st.subheader("Crime Rate Forecasting (2024-2026)")

        st.write(selected_data)

        forecast_df = predict_crime_rate(selected_country)

        st.write(forecast_df)

# Page 2: Display the histogram for the selected country
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

#     to run code type "streamlit run main.py" in terminal
