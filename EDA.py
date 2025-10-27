import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from datetime import datetime, timedelta

# Make some constants for easy adjustment
DATA_PATH = r"C:\Users\dourh\OneDrive\Bureau\UM\Computational Research Skills(E&OR)\ScanRecords.csv"  # <-- replace with your dataset filename
# DATE_COL = "Date"
# TIME_COL = "Time"
# DUR_COL = "Duration"
# TYPE_COL = "PatientType"

# Data loading and initial exploration
df = pd.read_csv(DATA_PATH)
print("Rows,cols:", df.shape)
# print(df.head())
# print(df.info())


# Parse date and time into single column Datetime
def make_datetime(row):
    # Make sure to change time fraction format from 9.5 to 9:30
    try:
        t = float(row["Time"])
    except:
        # if time is already a string like "09:30" adjust accordingly
        try:
            return pd.to_datetime(row["Date"] + " " + row["Time"])
        except:
            return pd.NaT
    hours = int(np.floor(t))
    minutes = int(round((t - hours) * 60))
    return pd.to_datetime(row["Date"]) + pd.Timedelta(hours=hours, minutes=minutes)


df["Datetime"] = df.apply(make_datetime, axis=1)
# print(df[["Date", TIME_COL, "Datetime"]].head())


# Check for missing or invalid datetimes
# print("\nChecking datetime values:")
# print(f"Total rows: {len(df)}")
# print(f"Missing datetime values: {df['Datetime'].isna().sum()}")
# print(f"Percentage missing: {(df['Datetime'].isna().sum() / len(df)) * 100:.2f}%")
# print(f"Missing Duration values: {df['Duration'].isna().sum()}")
# print(f"Percentage missing: {(df['Duration'].isna().sum() / len(df)) * 100:.2f}%")
# i check for invalid datetime/duration entries and there are none in this dataset

#  Separate dataframes by patient type in dictionary dfs for easy access later
#  print(f"Missing datetime values: {df['PatientType'].isna().sum()}") # there are no missing patient type entries
patientType_values = df["PatientType"].unique()
print("Patient types:", patientType_values)
splitDFs = {tp: df[df["PatientType"] == tp].copy() for tp in patientType_values}
print("splitDFs", splitDFs)

# Daily counts of scans by patient type
df["CallDate"] = df["Datetime"].dt.date
daily_counts = (
    df.groupby(["PatientType", "CallDate"])
    .size()
    .unstack(level=0)
    .fillna(0)
    .astype(int)
)

# print(daily_counts.head(10))

# Histogram for skewness checking
# mean & std sensitive to outliers
# Median & 90th percentile — robust indicators
# Q-Q plot — see whether Normal is a bad assumption
# Helps us choose: gamma/lognormal vs empirical bootstrap
# Here we are triying to extracts the key statistics and visual checks needed
# to decide the correct duration distributions for each patient type, which is
# essential input for the discrete-event simulation and optimization of slot lengths

for patientType, sub in splitDFs.items():
    print(f"\n--- Type {patientType} summary ---")
    print("Number of patient in type I group:", len(sub))

    stats = sub["Duration"].agg(["mean", "std", "median"])
    p90 = np.percentile(sub["Duration"], 90)

    print(stats)
    print("p90:", p90)

    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.hist(sub["Duration"], bins=20)
    plt.title(f"Histogram durations - Type {patientType}")

    plt.subplot(1, 2, 2)
    st.probplot(sub["Duration"], dist="norm", plot=plt)
    plt.suptitle(f"Q-Q plot (normal) - Type {patientType}")
    plt.show()


# print(df.head())
