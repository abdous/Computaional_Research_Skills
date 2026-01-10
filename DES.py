import pandas as pd
import numpy as np

# Importing data obtained from part 1
DATA_PATH = "synthetic_month.csv"
df = pd.read_csv(DATA_PATH)

# For easy scheduling, convert durations to minutes
df["Duration_min"] = df["Duration"] * 60

# Simulation parameters
WORKDAY_MIN = 9 * 60  # 8:00-17:00 = 540 minutes
N_MRIS = 2  # Number of MRI machines

slot_policies = [(30, 30), (30, 45), (30, 60), (45, 45), (45, 60), (60, 60)] # Minutes per slot (type 1 slot, type 2 slot)
n_replications = 30

results = []

def generate_calls(data, seed):
    rng = np.random.default_rng(seed)
    calls = data.copy()
    calls["CallTime_min"] = rng.integers(0, WORKDAY_MIN, size=len(calls))
    return calls

def earliest_slot(planned_end, first_day, slot_len):
    d = first_day
    while True:
        end_time = planned_end.get(d, 0)
        if end_time + slot_len <= WORKDAY_MIN:
            return d, end_time
        d += 1

def build_schedule(df, slot_len_t1, slot_len_t2, system, seed):
    rng = np.random.default_rng(seed)
    df = generate_calls(df, seed)

    # Sort by call moment (who calls first gets scheduled first)
    df = df.sort_values(["Day", "CallTime_min"]).reset_index(drop=True)

    schedule = {m: {} for m in range(N_MRIS)}
    planned_end = {m: {} for m in range(N_MRIS)}

    for _, row in df.iterrows():
        call_day = int(row["Day"])
        duration = row["Duration_min"]
        patient_type = row["Type"]
        slot_len = slot_len_t1 if patient_type == "Type 1" else slot_len_t2


        earliest_day = call_day + 1

        if system == "old":
            # Dedicated machines
            m = 0 if patient_type == "Type 1" else 1
            d, start = earliest_slot(planned_end[m], earliest_day, slot_len)

        else:
            # New system: choose earliest slot across both machines
            options = []
            for m_try in range(N_MRIS):
                d_try, s_try = earliest_slot(planned_end[m_try], earliest_day, slot_len)
                options.append((d_try, s_try, m_try))
            d, start, m = min(options)

        planned_end[m][d] = start + slot_len
        schedule[m].setdefault(d, []).append(
            {"PlannedStart": start, "Duration": duration, "CallDay": call_day, "CallTime": row["CallTime_min"]}
        )

    return schedule

def execute_day(appointments):
    current_time = 0
    overtime = 0
    service = 0

    for appt in appointments:
        start = max(appt["PlannedStart"], current_time)
        current_time = start + appt["Duration"]
        service += appt["Duration"]

    overtime = max(0, current_time - WORKDAY_MIN)
    return overtime, service

def run_replication(slot_pair, system, seed):
    slot_len_t1, slot_len_t2 = slot_pair
    schedule = build_schedule(df, slot_len_t1, slot_len_t2, system, seed)

    rows = []
    for day in sorted({d for m in schedule for d in schedule[m]}):
        appt_waits = []
        total_service = 0
        finish_times = []

        for m in schedule:
            todays = schedule[m].get(day, [])
            # collect waiting times (in DAYS, simple & intuitive)
            for appt in todays:
                appt_waits.append(day - appt["CallDay"])

            overtime, service = execute_day(todays)
            total_service += service
            finish_times.append(overtime + WORKDAY_MIN if service > 0 else 0)
        
        avg_wait = float(np.mean(appt_waits)) if appt_waits else 0.0
        overtime_day = max(0, max(finish_times) - WORKDAY_MIN)
        utilization = total_service / (WORKDAY_MIN * N_MRIS)

        rows.append(
            {"AvgWait (days)": avg_wait, "Overtime (min)": overtime_day, "Utilization": utilization}
        )

    return pd.DataFrame(rows)

results = []

for slot_pair in slot_policies:
    for rep in range(n_replications):
        for system in ["old", "new"]:
            out = run_replication(slot_pair, system, rep)
            out["System"] = system
            out["Slot_T1"] = slot_pair[0]
            out["Slot_T2"] = slot_pair[1]            
            results.append(out)

final = pd.concat(results)
summary = final.groupby(["System", "Slot_T1", "Slot_T2"]).agg(["mean", "std"]).round(2)

print(summary)
