import numpy as np
import pandas as pd
import scipy.stats as st

""""
The synthetic data generation script creates a synthetic dataset for MRI scan durations
for two patient types over a simulated month (30 days)."""

rng = np.random.default_rng(2025)
n_days = 30  # simulate one month

# Type 1 parameters from EDA
lambda_t1 = 16.95
mu_t1, sigma_t1 = 0.4285, 0.0973

# Type 2 parameters from EDA / bootstrap
lambda_t2 = 10.0  # daily arrivals
df = pd.read_csv(
    r"C:\Users\dourh\OneDrive\Bureau\UM\Computational Research Skills(E&OR)\ScanRecords.csv"
)
type2_durations = df[df["PatientType"] == "Type 2"]["Duration"].values

# Generate Type 1 data
type1_records = []
for day in range(1, n_days + 1):
    n_arrivals = rng.poisson(lambda_t1)
    durations = rng.normal(mu_t1, sigma_t1, n_arrivals)
    type1_records.extend([(day, "Type 1", d) for d in durations])

# Generate Type 2 data (bootstrap resampling)
"""
Here we are not confident about the true distribution, so instead of assuming a possibly wrong model,
we recycle the actual observed durations with replacement, because this preserves their real-world shape,
including skewness and variability.
"""
type2_records = []
for day in range(1, n_days + 1):
    n_arrivals = rng.poisson(lambda_t2)
    durations = rng.choice(type2_durations, n_arrivals, replace=True)
    type2_records.extend([(day, "Type 2", d) for d in durations])

# Combine both types and save to CSV
synthetic_df = pd.DataFrame(
    type1_records + type2_records, columns=["Day", "Type", "Duration"]
)
synthetic_df.to_csv("data/synthetic_month.csv", index=False)
print(synthetic_df.head())
print(synthetic_df.info())
print(synthetic_df.groupby("Type")["Day"].count())
