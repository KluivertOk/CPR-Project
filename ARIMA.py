import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from itertools import product
from sklearn.metrics import mean_absolute_error


def grid_search_arima(selected_data, p_range, d_range, q_range):
    best_aic = np.inf
    best_order = None

    for p in p_range:
        for d in d_range:
            for q in q_range:
                order = (p, d, q)
                try:
                    arima_model = ARIMA(selected_data, order=order)
                    model = arima_model.fit()
                    aic = model.aic

                    if aic < best_aic:
                        best_aic = aic
                        best_order = order
                except Exception as e:
                    print(f"Error for order {order}: {e}")   # handling errors
                    continue

    return best_order


def predict_crime_rate(selected_country, population_data, file_path='Prediction.csv',
                       p_range=range(1), d_range=range(1), q_range=range(4, 5), forecast_steps=5):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Filter data for the selected country
    selected_data = df[df['Country'] == selected_country]

    # Check if there is data for the selected country
    if selected_data.empty:
        print(f"There is no data for {selected_country}")
        return None, None  # Return None for both forecast DataFrame and crime_index

    # Convert the 'crime_per_100k' column to numeric
    selected_data['crime_per_100k'] = pd.to_numeric(selected_data['crime_per_100k'], errors='coerce')

    # Check stationarity
    results = adfuller(selected_data['crime_per_100k'].dropna())
    print('p-value:', results[1])

    results = adfuller(selected_data['crime_per_100k'].diff().dropna())
    print('p-value:', results[1])

    results = adfuller(selected_data['crime_per_100k'].diff().diff().dropna())
    print('p-value:', results[1])

    # Perform grid search for ARIMA hyperparameters
    best_order = grid_search_arima(selected_data['crime_per_100k'], p_range, d_range, q_range)

    # ARIMA Model with best order
    arima_model = ARIMA(selected_data['crime_per_100k'], order=best_order)
    model = arima_model.fit()

    # Forecasting
    forecast = model.forecast(steps=forecast_steps)

    # Plot actual vs predicted values
    plt.figure(figsize=(10, 6))
    plt.plot(selected_data.index, selected_data['crime_per_100k'], label='Actual')
    plt.plot(np.arange(len(selected_data), len(selected_data) + forecast_steps), forecast, label='Predicted')
    plt.xlabel('Time')
    plt.ylabel('Crime Rate per 100k')
    plt.title('Actual vs Predicted Crime Rate')
    plt.legend()
    plt.show()

    # Format predicted values into a DataFrame
    result_df = pd.DataFrame(
        {'Date': pd.date_range(start=selected_data['date'].iloc[-1], periods=forecast_steps + 1, freq='Y')[1:],
         'Predicted': forecast})

    # Calculate the crime index
    crime_index = (forecast / 100000) * \
                  population_data.loc[population_data['Country'] == selected_country, 'Population'].iloc[-1]

    # Cap the crime index values at 100
    crime_index = np.minimum(crime_index, 100)

    return result_df, crime_index  # Return both forecast DataFrame and crime_index
