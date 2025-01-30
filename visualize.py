import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the CSV file into a DataFrame
df = pd.read_csv('oda_product_catalogue.csv')

# Display the first few rows of the DataFrame
print(df.head())

# Clean the price column
df['price'] = df['price'].str.replace('\xa0', '').str.replace('kr', '').str.replace(',', '.').astype(float)

# Example Analysis: Count of products per category
category_counts = df['category'].value_counts()
print(category_counts)

# Example Visualization: Bar plot of product counts per category
plt.figure(figsize=(10, 6))
sns.barplot(x=category_counts.index, y=category_counts.values)
plt.title('Number of Products per Category')
plt.xlabel('Category')
plt.ylabel('Number of Products')
plt.xticks(rotation=90)
plt.show()

# Example Visualization: Distribution of product prices
plt.figure(figsize=(10, 6))
sns.histplot(df['price'], bins=30, kde=True)
plt.title('Distribution of Product Prices')
plt.xlabel('Price (kr)')
plt.ylabel('Frequency')
plt.show()