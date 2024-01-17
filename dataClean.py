import pandas as pd

# Sample data loading (replace it with your actual dataset)
df = pd.read_csv("CrimeIndex.csv")

# Clean and convert the 'Crime_indicator_from_2020_2023' column to floats
df['Crime_indicator_from_2020_2023'] = df['Crime_indicator_from_2020_2023'].str.replace('↑', ' +').str.replace('↓', ' -').str.replace('%', ' ').astype(float)



# Display the updated DataFrame
print(df)
