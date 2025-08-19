import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create sample data with intentional issues
np.random.seed(42)
n_samples = 100

# Generate data with various issues
data = {
    'Name': ['John Smith', 'Jane Doe', np.nan, 'Bob Wilson', 'Alice Brown'] * 20,
    'Age': np.random.randint(18, 80, n_samples),
    'City': ['New York', None, 'London', 'Paris', 'Tokyo'] * 20,
    'Salary': np.random.randint(30000, 120000, n_samples).astype(str),  # Salary as string
    'Date': [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(n_samples)]
}

# Introduce more missing values
data['Age'][10:20] = np.nan
data['Salary'][5:15] = np.nan

# Create DataFrame and save to CSV
df = pd.DataFrame(data)
df.to_csv('dirty_data.csv', index=False)
print("Sample dirty dataset has been created!")
