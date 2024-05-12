import pandas as pd
from prophet import Prophet
import warnings

def predict_crime_rate_prophet(selected_country, population_data, file_path='Prediction.csv', forecast_years=5):
    # Suppress warnings
    warnings.filterwarnings("ignore")

    # Read the CSV file
    df = pd.read_csv(file_path)

    # Filter data for the selected country
    selected_data = df[df['Country'] == selected_country]

    # Check if there is data for the selected country
    if selected_data.empty:
        print(f"There is no data for {selected_country}")
        return None

    # Prepare the data for Prophet
    ireland_data = selected_data[['date', 'crime_per_100k']].copy()
    ireland_data.columns = ['ds', 'y']
    ireland_data['ds'] = pd.to_datetime(ireland_data['ds'], format='%d/%m/%Y', errors='coerce')

    # Instantiate and fit Prophet model
    m = Prophet()
    m.fit(ireland_data)

    # Calculate the number of days in the forecast_years
    forecast_days = forecast_years * 1

    # Generate future dates for forecasting
    future = m.make_future_dataframe(periods=forecast_days, freq='Y')  # Forecast for forecast_years

    # Predict future crime rates
    forecast = m.predict(future)

    # Filter forecast for only the future dates
    try:
        forecast_future = forecast[forecast['ds'] > selected_data['ds'].max()]
    except KeyError:
        forecast_future = forecast[forecast['ds'] > ireland_data['ds'].max()]

    # Calculate the crime index
    forecast_future['Crime_Index'] = (forecast_future['yhat'] / 100000) * population_data.loc[
        population_data['Country'] == selected_country, 'Population'].iloc[-1]

    # Format predicted values into a DataFrame
    result_df = forecast_future[['ds', 'yhat', 'Crime_Index']].rename(columns={'yhat': 'Predicted'})

    return result_df
