import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv("Ireland Data.csv")

# Filter data for the WESTERN REGION
western_region_data = df[df['REGION'] == 'EASTERN REGION']

# Select only the columns containing quarter data
quarter_columns = df.columns[5:]

# Convert quarter data to integer type and sum occurrences across all quarters
western_region_data[quarter_columns] = western_region_data[quarter_columns].apply(pd.to_numeric, errors='coerce')
offence_counts = western_region_data.groupby('TYPE OF OFFENCE')[quarter_columns].sum().sum(axis=1)

# Sort offences by frequency in descending order
offence_counts = offence_counts.sort_values(ascending=False)

# Plotting
offence_counts.plot(kind='bar', figsize=(16, 8), color='skyblue')
plt.title('Frequency of Offences in the EASTERN REGION from 2003Q1 to 2019Q3')
plt.xlabel('Type of Offence')
plt.ylabel('Frequency')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
