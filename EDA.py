import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from datetime import datetime, timedelta

# Make some constants for easy adjustment
DATA_PATH = r"C:\Users\dourh\OneDrive\Bureau\UM\Computational Research Skills(E&OR)\ScanRecords.csv"  # <-- replace with your dataset filename
DATE_COL = "Date"
TIME_COL = "Time"
DUR_COL = "Duration"
TYPE_COL = "PatientType"

# Data loading and initial exploration
df = pd.read_csv(DATA_PATH)
print("Rows,cols:", df.shape)
print(df.head())
print(df.info())
