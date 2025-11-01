import simpy
import numpy as np
from scipy.stats import gamma
import statistics

# Parameters
# Type 1 from the EDA
MU1, SIG1, LAMBDA1 = 0.4285, 0.0973, 16.95
# Type 2 from the EDA
A2, LOC2, SCALE2, LAMBDA2 = (
    4.573,
    -0.109,
    0.150,
    10.0,
)  # i consider a slightly higher arrival rate for Type 2 10.0 beacause of the longer observation period
# Workday
WORK_START, WORK_END = 8.0, 17.0
DAY_LEN = WORK_END - WORK_START


# Sampling functions
def service_time(type_id, rng):
    """Draw service time depending on patient type."""
    if type_id == "Type 1":
        s = rng.normal(MU1, SIG1)
        return abs(s) + 1e-4
    else:  # Type 2
        s = gamma.rvs(A2, loc=LOC2, scale=SCALE2, random_state=rng)
        return max(s, 1e-4)


def arrival_times_poisson(rng, lam):
    """Generate Poisson number of arrivals uniformly over the day."""
    n = rng.poisson(lam)
    times = WORK_START + rng.random(n) * DAY_LEN
    times.sort()
    return times


# Determine the patient process
def patient_process(env, name, mri_pool, arrival, type_id, stats, rng):
    yield env.timeout(max(0, arrival - env.now))
    arrive = env.now
    with mri_pool.request() as req:
        yield req
        start = env.now
        wait = start - arrive
        stats["waits"].append(wait)
        dur = service_time(type_id, rng)
        yield env.timeout(dur)
        end = env.now
        stats["starts"].append(start)
        stats["ends"].append(end)
        stats["types"].append(type_id)
        stats["overtime"].append(max(0.0, (end - WORK_END) * 60))


# Consider a single day run/simulation
def run_one_day(seed=None):
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    mri_pool = simpy.Resource(env, capacity=2)
    stats = {"waits": [], "starts": [], "ends": [], "types": [], "overtime": []}

    # arrivals for both types
    arr1 = [(t, "Type 1") for t in arrival_times_poisson(rng, LAMBDA1)]
    arr2 = [(t, "Type 2") for t in arrival_times_poisson(rng, LAMBDA2)]
    all_arr = sorted(arr1 + arr2, key=lambda x: x[0])

    for i, (at, tp) in enumerate(
        all_arr
    ):  # at: stand for arrival time, tp: patient type
        env.process(patient_process(env, f"{tp}_{i}", mri_pool, at, tp, stats, rng))

    env.run(until=WORK_END + 8.0)

    busy = sum(e - s for s, e in zip(stats["starts"], stats["ends"]))
    util = busy / (DAY_LEN * 2)  # we are making use of the 2 machines
    return {
        "n_patients": len(stats["waits"]),
        "avg_wait_min": np.mean(stats["waits"]) * 60 if stats["waits"] else 0,
        "total_overtime_min": sum(stats["overtime"]),
        "utilization": util,
    }


# Replicate the one-day simulation multiple timesC
def run_reps(n_rep=200):
    seeds = range(3000, 3000 + n_rep)
    return [run_one_day(s) for s in seeds]


if __name__ == "__main__":
    results = run_reps(200)
    arr = [r["n_patients"] for r in results]
    wait = [r["avg_wait_min"] for r in results]
    ot = [r["total_overtime_min"] for r in results]
    util = [r["utilization"] for r in results]

    print(
        "Arrivals/day: mean {:.2f}, sd {:.2f}".format(np.mean(arr), np.std(arr, ddof=1))
    )
    print(
        "Avg wait (min): mean {:.2f}, sd {:.2f}".format(
            np.mean(wait), np.std(wait, ddof=1)
        )
    )
    print(
        "Total overtime (min): mean {:.2f}, sd {:.2f}".format(
            np.mean(ot), np.std(ot, ddof=1)
        )
    )
    print(
        "Utilization (2 MRIs): mean {:.3f}, sd {:.3f}".format(
            np.mean(util), np.std(util, ddof=1)
        )
    )
