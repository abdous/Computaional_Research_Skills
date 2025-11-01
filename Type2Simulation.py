import simpy
import numpy as np
from scipy.stats import gamma
import statistics

# # Make use of the fitted gamma parameters but one can also use lognormal from the EDA
A, LOC, SCALE = (
    4.573,
    -0.109,
    0.150,
)
LAMBDA = 10.0  # mean arrivals per day, i choose small value because the waiting time was long
WORK_START, WORK_END = 8.0, 17.0
DAY_LEN = WORK_END - WORK_START


# Sampling functions
def sample_service_time(rng):
    s = gamma.rvs(A, loc=LOC, scale=SCALE, random_state=rng)
    return max(s, 1e-4)  # ensure positive


def arrival_times_poisson(rng, lam=LAMBDA):
    n = rng.poisson(lam)
    times = WORK_START + rng.random(n) * DAY_LEN
    times.sort()
    return times


# Determine the patient process
def patient_process(env, name, mri, arrival, stats, rng):
    yield env.timeout(max(0, arrival - env.now))
    arrive = env.now
    with mri.request() as req:
        yield req
        start = env.now
        wait = start - arrive
        stats["waits"].append(wait)
        dur = sample_service_time(rng)
        yield env.timeout(dur)
        end = env.now
        stats["starts"].append(start)
        stats["ends"].append(end)
        stats["overtime"].append(max(0.0, (end - WORK_END) * 60))


# Consider a single day run/simulation
def run_one_day(seed=None):
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    mri = simpy.Resource(env, capacity=1)
    stats = {"waits": [], "starts": [], "ends": [], "overtime": []}

    arrivals = arrival_times_poisson(rng)
    for i, at in enumerate(arrivals):  # at: stand for arrival time
        env.process(patient_process(env, f"T2_{i}", mri, at, stats, rng))

    env.run(until=WORK_END + 8.0)  # allow overtime

    busy = sum(e - s for s, e in zip(stats["starts"], stats["ends"]))
    util = busy / DAY_LEN
    return {
        "n": len(stats["waits"]),
        "wait_min": np.mean(stats["waits"]) * 60 if stats["waits"] else 0,
        "total_ot": sum(stats["overtime"]),
        "util": util,
    }


# Replicate the one-day simulation multiple times
def run_reps(n_rep=200):
    seeds = range(2000, 2000 + n_rep)
    outs = [run_one_day(s) for s in seeds]
    return outs


if __name__ == "__main__":
    results = run_reps(200)
    n_arr = [r["n"] for r in results]
    wait = [r["wait_min"] for r in results]
    ot = [r["total_ot"] for r in results]
    util = [r["util"] for r in results]

    print(
        "Daily arrivals: mean {:.2f}, sd {:.2f}".format(
            np.mean(n_arr), np.std(n_arr, ddof=1)
        )
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
        "Utilization: mean {:.3f}, sd {:.3f}".format(
            np.mean(util), np.std(util, ddof=1)
        )
    )
