import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA


def predict_crime_rate(selected_country, file_path='Prediction.csv', order=(1, 2, 2), forecast_steps=5):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Filter data for the selected country
    selected_data = df[df['Country'] == selected_country]

    # Check if there is data for the selected country
    if selected_data.empty:
        print(f"There is no data for {selected_country}")
        return None

    # Convert the 'crime_per_100k' column to numeric
    selected_data['crime_per_100k'] = pd.to_numeric(selected_data['crime_per_100k'], errors='coerce')

    # Check stationarity
    results = adfuller(selected_data['crime_per_100k'].dropna())
    print('p-value:', results[1])

    results = adfuller(selected_data['crime_per_100k'].diff().dropna())
    print('p-value:', results[1])

    results = adfuller(selected_data['crime_per_100k'].diff().diff().dropna())
    print('p-value:', results[1])

    # ARIMA Model
    arima_model = ARIMA(selected_data['crime_per_100k'], order=order)
    model = arima_model.fit()

    # Forecasting
    forecast = model.forecast(steps=forecast_steps)

    # Format predicted values into a DataFrame
    result_df = pd.DataFrame(
        {'Date': pd.date_range(start=selected_data['date'].iloc[-1], periods=forecast_steps + 1, freq='Y')[1:],
         'Predicted': forecast})

    return result_df