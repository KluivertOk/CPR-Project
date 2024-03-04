import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv("Ireland Data.csv")

# Filter data for the NORTHERN REGION and "THEFT AND RELATED OFFENCES"
theft_northern_region = df[(df['REGION'] == 'NORTHERN REGION') & (df['TYPE OF OFFENCE'] == 'THEFT AND RELATED OFFENCES')]

# Select columns from 2003Q1 to 2019Q3
theft_data = theft_northern_region.loc[:, '2003Q1':'2019Q3']

# Sum the occurrences across all quarters
theft_counts = theft_data.sum()

# Plotting
theft_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, figsize=(10, 8))
plt.title('Frequency of "THEFT AND RELATED OFFENCES" in the Northern Region from 2003Q1 to 2019Q3')
plt.xlabel('Quarter')
plt.ylabel('Frequency')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
