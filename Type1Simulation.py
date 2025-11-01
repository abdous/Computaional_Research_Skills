# simpy_type1_day.py
import simpy
import numpy as np
import statistics

# These parameters are estimated from the EDA for Type 1 patients
MU = 0.4285398304505077  # hours
SIG = 0.09726936834726761  # hours
LAMBDA = 16.952380952380953  # mean daily arrivals
WORK_START = 8.0  # 8:00
WORK_END = 17.0  # 17:00
DAY_LENGTH = WORK_END - WORK_START  # 9.0 hours


# Sampling functions
def generate_arrival_times_poisson_day(rng, lam=LAMBDA):
    """Draw number of arrivals from Poisson(lam) and assign uniform arrival times during working hours."""
    n = rng.poisson(lam)
    # uniform arrival times within work window (in hours since midnight)
    times = WORK_START + rng.random(n) * DAY_LENGTH
    times.sort()
    return times


def sample_service_time(rng):
    """Sample service duration (hours). If negative from normal, resample or floor to small positive."""
    s = rng.normal(MU, SIG)
    # ensure positive: if negative or zero, resample once (rare)
    if s <= 0:
        s = abs(s) + 1e-4
    return s


# determine the patient process
def patient_process(env, name, mri, arrival_time, stats, rng):
    """Process for a single patient arriving at arrival_time."""
    # Wait until arrival_time
    yield env.timeout(max(0, arrival_time - env.now))
    arrive = env.now
    # Request machine
    with mri.request() as req:
        yield req
        start_service = env.now
        wait = start_service - arrive
        stats["waits"].append(wait)
        service = sample_service_time(rng)
        yield env.timeout(service)
        finish = env.now
        stats["service_starts"].append(start_service)
        stats["service_ends"].append(finish)
        # record whether service finished after WORK_END (overtime minutes)
        if finish > WORK_END:
            stats["overtime_minutes"].append((finish - WORK_END) * 60.0)
        else:
            stats["overtime_minutes"].append(0.0)


# Consider a single day run/simulation
def run_one_day(seed=None):
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    mri = simpy.Resource(env, capacity=1)
    stats = {
        "waits": [],
        "service_starts": [],
        "service_ends": [],
        "overtime_minutes": [],
    }

    # Generate arrivals for this day
    arrival_times = generate_arrival_times_poisson_day(rng)
    # Start processes
    for i, at in enumerate(arrival_times):  # at: stand for arrival time
        env.process(patient_process(env, f"p{i+1}", mri, at, stats, rng))

    # Run until a time that allows overtime to finish (work until end + some buffer)
    env.run(
        until=WORK_END + 8.0
    )  # allow up to 8 extra hours of overtime if queue piles up

    # Compute metrics
    total_patients = len(arrival_times)
    avg_wait_min = statistics.mean(stats["waits"]) * 60.0 if stats["waits"] else 0.0
    avg_overtime = statistics.mean(
        stats["overtime_minutes"]
    )  # minutes per patient (includes zeros)
    total_overtime = sum(
        stats["overtime_minutes"]
    )  # total overtime minutes across patients
    # utilization: total busy time / (WORK_END-WORK_START) for the machine
    # approximate busy time as sum of (service ends - service starts)
    busy_time = sum(
        [
            end - start
            for start, end in zip(stats["service_starts"], stats["service_ends"])
        ]
    )
    utilization = busy_time / DAY_LENGTH

    return {
        "n_arrivals": total_patients,
        "avg_wait_min": avg_wait_min,
        "avg_overtime_min_per_patient": avg_overtime,
        "total_overtime_min": total_overtime,
        "utilization": utilization,
    }


# Replicate the one-day simulation multiple times
def run_reps(n_rep=200):
    seeds = list(range(1234, 1234 + n_rep))
    outputs = []
    for s in seeds:
        out = run_one_day(seed=s)
        outputs.append(out)
    return outputs


if __name__ == "__main__":
    results = run_reps(200)
    # summarize
    n_arrivals = [r["n_arrivals"] for r in results]
    avg_waits = [r["avg_wait_min"] for r in results]
    total_overtimes = [r["total_overtime_min"] for r in results]
    utilizations = [r["utilization"] for r in results]

    print(
        "Daily arrivals: mean {:.2f}, sd {:.2f}".format(
            np.mean(n_arrivals), np.std(n_arrivals, ddof=1)
        )
    )
    print(
        "Avg wait (min): mean {:.2f}, sd {:.2f}".format(
            np.mean(avg_waits), np.std(avg_waits, ddof=1)
        )
    )
    print(
        "Total overtime (min): mean {:.2f}, sd {:.2f}".format(
            np.mean(total_overtimes), np.std(total_overtimes, ddof=1)
        )
    )
    print(
        "Utilization: mean {:.3f}, sd {:.3f}".format(
            np.mean(utilizations), np.std(utilizations, ddof=1)
        )
    )
