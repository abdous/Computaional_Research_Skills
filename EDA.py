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

# print(df.head())
