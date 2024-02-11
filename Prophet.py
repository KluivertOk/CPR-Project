import warnings
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet

# Suppress FutureWarnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Step 1: Read the CSV file
data = pd.read_csv("Prediction.csv")

# Step 2: Data Preparation
# Explicitly create a copy of the DataFrame
ireland_data = data[data['Country'] == 'Ireland'].copy()
ireland_data['date'] = pd.to_datetime(ireland_data['date'], format='%d/%m/%Y')

# Rename columns as expected by Prophet
ireland_data.rename(columns={'date': 'ds', 'crime_per_100k': 'y'}, inplace=True)

# Step 3: Prophet Forecasting
# Initialize and fit the Prophet model
model = Prophet()
model.fit(ireland_data)

# Make future predictions
future = model.make_future_dataframe(periods=365)  # Forecast for one year into the future
forecast = model.predict(future)

# Step 4: Visualization
model.plot(forecast, xlabel='Date', ylabel='Crime Rate per 100k', figsize=(10, 6))
plt.title('Prophet Forecast: Crime Rate in Ireland')
plt.show()
