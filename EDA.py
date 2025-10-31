import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from datetime import datetime, timedelta

# Make some constants for easy adjustment
DATA_PATH = r"C:\Users\dourh\OneDrive\Bureau\UM\Computational Research Skills(E&OR)\ScanRecords.csv"  # replace with your dataset filename


# Loading data and initial exploration
df = pd.read_csv(DATA_PATH)


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

# Check for missing or invalid datetimes
# print("\nChecking datetime values:")
# print(f"Total rows: {len(df)}")
# print(f"Missing datetime values: {df['Datetime'].isna().sum()}")
# print(f"Percentage missing: {(df['Datetime'].isna().sum() / len(df)) * 100:.2f}%")
# print(f"Missing Duration values: {df['Duration'].isna().sum()}")
# print(f"Percentage missing: {(df['Duration'].isna().sum() / len(df)) * 100:.2f}%")
# i check for invalid datetime/duration entries and there are none in this dataset

#  Separate dataframes by patient scan type in dictionary for easy access
#  Here also check for missing values but there are no missing patient type entries
patienScanType = df["PatientType"].unique()
df["CallDate"] = df["Datetime"].dt.date
splitedData = {tp: df[df["PatientType"] == tp].copy() for tp in patienScanType}

# Daily counts of scans by type
daily_counts = (
    df.groupby(["PatientType", "CallDate"])
    .size()
    .unstack(level=0)
    .fillna(0)
    .astype(int)
)


for patientType, sub in splitedData.items():
    # plot the histogram and Q-Q plot for each patient type
    print(f"\n--- summary for {patientType} ---")
    print(f"Number of patient in {patientType}:", len(sub))

    stats = sub["Duration"].agg(["mean", "std", "median"])
    p90 = np.percentile(sub["Duration"], 90)  # 90th percentile

    print(stats)
    print("90th percentile:", p90)

    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.hist(sub["Duration"], bins=20)
    plt.title(f"Histogram durations - {patientType}")

    plt.subplot(1, 2, 2)
    st.probplot(sub["Duration"], dist="norm", plot=plt)
    plt.suptitle(f"Check for normality - {patientType}")
    plt.show()

# Fit Normal (mu, sigma) and Poisson arrivals per day for Type 1 patients scans
if "Type 1" in splitedData:
    typeI = splitedData["Type 1"]
    mu_hat = typeI["Duration"].mean()
    sigma_hat = typeI["Duration"].std(ddof=1)
    print("\nType 1 duration estimated μ, σ:", mu_hat, sigma_hat)

    # daily arrivals for Type 1
    counts_type1 = typeI.groupby("CallDate").size()
    lambda_hat = counts_type1.mean()
    print("Type 1 daily arrival counts (mean=λ̂):", lambda_hat)
    print("Type 1 daily counts (summary):")
    print(counts_type1.describe())


# For Type 2 as suggested above we can try fitting lognormal or gamma distributions"
if "Type 2" in splitedData:
    typeII = splitedData["Type 2"]
    # Basic quantiles and a kernel density estimate suggestion
    print("\nType 2 duration quantiles:")
    print(typeII["Duration"].quantile([0.1, 0.25, 0.5, 0.75, 0.9, 0.95]))
    # Try fit candidate parametric distributions (lognormal, gamma)
    # Fit lognormal: take log of durations >0
    positive = typeII[typeII["Duration"] > 0]["Duration"]
    if len(positive) > 5:
        ln_params = st.lognorm.fit(positive, floc=0)  # shape, loc, scale
        print("Type 2 lognormal params (shape, loc, scale):", ln_params)
        gamma_params = st.gamma.fit(positive)
        print("Type 2 gamma params (a, loc, scale):", gamma_params)
