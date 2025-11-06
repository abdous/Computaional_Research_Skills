import simpy
import pandas as pd
import numpy as np

DATA_PATH = "data/synthetic_month.csv"
df = pd.read_csv(DATA_PATH)

# For esasy scheduling, convert durations to minutes
df["Duration_min"] = df["Duration"] * 60

# Simulation parameters
WORKDAY_MIN = 8 * 60  # 8 hours = 480 min
N_MRIS = 2  # Number of MRI machines

slot_policies = [30, 45, 60]  # minutes per slot
n_replications = 30

results = []


def simulate_policy(slot_length, seed):
    rng = np.random.default_rng(seed)
    daily_results = []

    for day, group in df.groupby("Day"):
        env = simpy.Environment()
        mri = simpy.Resource(env, capacity=N_MRIS)
        wait_times, overtime = [], []

        # scheduled start times based on slot length
        # expl:  slots every 30, 45, 60 min up to end of workday
        slot_starts = np.arange(0, WORKDAY_MIN, slot_length)
        # assign each patient a random slot start
        assigned_slots = rng.choice(slot_starts, size=len(group), replace=True)

        # patient process
        def patient(env, duration, start_time):
            yield env.timeout(start_time)  # arrive at scheduled time
            arrival = env.now
            with mri.request() as req:
                yield req
                wait = env.now - arrival
                wait_times.append(wait)
                yield env.timeout(duration)
                if env.now > WORKDAY_MIN:
                    overtime.append(env.now - WORKDAY_MIN)

        # launch all patient processes
        for (_, row), slot_start in zip(group.iterrows(), assigned_slots):
            env.process(patient(env, row["Duration_min"], slot_start))

        # run until workday ends + small buffer
        env.run(until=WORKDAY_MIN + 180)

        # daily statistics
        daily_results.append(
            {
                "Day": day,
                "SlotLength": slot_length,
                "AvgWait": np.mean(wait_times) if wait_times else 0,
                "Overtime": np.sum(overtime),
                "Utilization": group["Duration_min"].sum() / (WORKDAY_MIN * N_MRIS),
            }
        )

    return pd.DataFrame(daily_results)


# Run simulation for each slot policy and replication
for slot in slot_policies:
    for rep in range(n_replications):
        res = simulate_policy(slot, seed=rep)
        res["Policy"] = f"{slot}min"
        res["Replication"] = rep
        results.append(res)

# Summary results without capacity control
final_res = pd.concat(results, ignore_index=True)
summary = final_res.groupby("Policy")[["AvgWait", "Overtime", "Utilization"]].agg(
    ["mean", "std"]
)

#  if you want to see the summary uncomment the following lines for the part not taking capacity control policy into account
# print("\n=== Simulation Summary (averaged over replications) ===")
# print(summary.round(2))


"""add capacity control policy simulation"""


def simulate_policy_capacity_control(slot_length, seed):
    rng = np.random.default_rng(seed)
    daily_results = []

    for day, group in df.groupby("Day"):
        env = simpy.Environment()
        mri = simpy.Resource(env, capacity=N_MRIS)
        wait_times, overtime = [], []

        # scheduled start times based on slot length
        slot_starts = np.arange(0, WORKDAY_MIN, slot_length)
        max_slots = len(slot_starts) * N_MRIS  # capacity constraint

        # Limit number of patients to available slots
        if len(group) > max_slots:
            group = group.sample(max_slots, random_state=seed)

        # Assign each patient to one slot
        assigned_slots = rng.choice(slot_starts, size=len(group), replace=True)

        # patient process
        def patient(env, duration, start_time):
            yield env.timeout(start_time)
            arrival = env.now
            with mri.request() as req:
                yield req
                wait_times.append(env.now - arrival)
                yield env.timeout(duration)
                if env.now > WORKDAY_MIN:
                    overtime.append(env.now - WORKDAY_MIN)

        # Launch patients
        for (_, row), slot_start in zip(group.iterrows(), assigned_slots):
            env.process(patient(env, row["Duration_min"], slot_start))

        env.run(until=WORKDAY_MIN + 180)
        daily_results.append(
            {
                "Day": day,
                "SlotLength": slot_length,
                "AvgWait": np.mean(wait_times) if wait_times else 0,
                "Overtime": np.sum(overtime),
                "Utilization": group["Duration_min"].sum() / (WORKDAY_MIN * N_MRIS),
            }
        )

    return pd.DataFrame(daily_results)


# Run simulation for each slot policy and replication

for slot in slot_policies:
    for rep in range(n_replications):
        res = simulate_policy_capacity_control(slot, seed=rep)
        res["Policy"] = f"{slot}min"
        res["Replication"] = rep
        results.append(res)

# summary results with capacity control
final_res = pd.concat(results, ignore_index=True)
summary = final_res.groupby("Policy")[["AvgWait", "Overtime", "Utilization"]].agg(
    ["mean", "std"]
)

print("\n Improved Simulation with Capacity Controlled")
print(summary.round(2))
