import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from prophet.plot import plot_plotly
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Read the CSV file
df = pd.read_csv('Prediction.csv')

# Filter data for Ireland
ireland_data = df[df['Country'] == 'Ireland'].copy()

# Select the relevant columns and rename them
ireland_data = ireland_data[['date', 'crime_per_100k']]
ireland_data.columns = ['ds', 'y']

# Convert 'y' column to numeric data, handling errors by setting invalid values to NaN
ireland_data['y'] = pd.to_numeric(ireland_data['y'], errors='coerce')

# Drop rows with NaN values in 'y' column
# ireland_data = ireland_data.dropna(subset=['y'])

# Convert 'ds' column to datetime format
ireland_data['ds'] = pd.to_datetime(ireland_data['ds'], format='%d/%m/%Y', errors='coerce')

# Plot the data
plt.figure(figsize=(18, 6))
plt.plot(ireland_data['ds'], ireland_data['y'], label='Actual', color='blue')
plt.xlabel('Date')
plt.ylabel('Crime Rate per 100k')
plt.title('Actual Crime Rate in Ireland')
plt.legend()
plt.grid(True)
plt.show()


print(len(df))

train = df.iloc[:len(df) - 365]
test = df.iloc[:len(df) - 365]

m = Prophet()
m.fit(ireland_data)

future = m.make_future_dataframe(periods=365)
forecast = m.predict(future)

forecast.tail()

print(plot_plotly(m, forecast).show())

