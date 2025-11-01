# ==========================================================
# Monte Carlo Simulations for Type 2 Duration Estimators
# ==========================================================

import numpy as np
import pandas as pd
import scipy.stats as st
from tqdm import trange

# Make sure to adjust the data path as needed
DATA_PATH = r"C:\Users\dourh\OneDrive\Bureau\UM\Computational Research Skills(E&OR)\ScanRecords.csv"
df = pd.read_csv(DATA_PATH)
type2 = df[df["PatientType"] == "Type 2"]["Duration"].dropna().values
n = len(type2)

# These are the parameters defined for the simulation
mc_reps = 500  # Monte Carlo replications
B_boot = 500  # Bootstrap resamples per replication
alpha = 0.05
rng_master = np.random.default_rng(2025)  # random generator for  reproducibility

# These are the fitted distribution parameters we already computed from the EDA
ln_shape, ln_loc, ln_scale = st.lognorm.fit(type2, floc=0)
gamma_a, gamma_loc, gamma_scale = st.gamma.fit(type2)


# Some basic statistic functions like mean, median, 90th percentile, probability > threshold t
def stat_mean(x):
    return np.mean(x)


def stat_median(x):
    return np.median(x)


def stat_p90(x):
    return np.percentile(x, 90)


def stat_prob_gt(x, t=1.0):
    # probability that a scan duration is greater than some threshold t = 1.0 hour
    # since in the EDA we noticed that a scan can take from 40 minutes and up so 1 hour is a reasonable threshold
    return np.mean(x > t)


# Bootstrap Helpers

""" In the nonparametric bootstrap, we resample with replacement from the observed data.
For each bootstrap sample, it recomputes the statistic.
The distribution of these bootstrap statistics gives an empirical estimate of sampling uncertainty.
The confidence interval is then just the percentiles of that bootstrap distribution
So no assumptions about the underlying distribution of the data are made.
"""


def nonparam_boot_ci(data, statfunc, B=B_boot, alpha=alpha, rng=None):
    rng = np.random.default_rng() if rng is None else rng
    boots = np.array(
        [statfunc(rng.choice(data, len(data), replace=True)) for _ in range(B)]
    )
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return (lo, hi)


""" In the parametric bootstrap, instead of resampling from the observed data,
we generate new samples from a parametric distribution(sample_func)."""


def param_boot_ci(sample_func, statfunc, n, B=B_boot, alpha=alpha, rng=None):
    rng = np.random.default_rng() if rng is None else rng
    boots = np.array([statfunc(sample_func(rng, n)) for _ in range(B)])
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return (lo, hi)


# Make use of sampler functions defined earlier
def sample_lognorm(rng, n):
    return st.lognorm.rvs(
        ln_shape, loc=ln_loc, scale=ln_scale, size=n, random_state=rng
    )


def sample_gamma(rng, n):
    return st.gamma.rvs(
        gamma_a, loc=gamma_loc, scale=gamma_scale, size=n, random_state=rng
    )


def sample_empirical(rng, n):
    return rng.choice(type2, size=n, replace=True)


# Defined Scenarios and Quantities
scenarios = {
    "Empirical": sample_empirical,
    "Lognormal": sample_lognorm,
    "Gamma": sample_gamma,
}

quantities = {
    "Mean": stat_mean,
    "Median": stat_median,
    "P90": stat_p90,
    "Prob>1h": lambda x: stat_prob_gt(x, 1.0),
}

results = {}

# Monte Carlo Simulations
for sc_name, sampler in scenarios.items():
    print(f"\nThe Running scenario is the : {sc_name} simulation")
    rng0 = np.random.default_rng(42)
    large_sample = sampler(rng0, 100000)
    # q stand for quantity and f for function
    true_vals = {q: f(large_sample) for q, f in quantities.items()}

    res = {q: {"Bias": [], "RMSE": [], "Coverage": []} for q in quantities}

    for rep in trange(mc_reps, desc=f"{sc_name} MC"):
        rng = np.random.default_rng(rng_master.integers(1e9))
        sample = sampler(rng, n)

        # Empirical (nonparametric bootstrap)
        for qname, statf in quantities.items():
            est = statf(sample)
            lo, hi = nonparam_boot_ci(sample, statf, rng=rng)
            bias = est - true_vals[qname]
            res[qname]["Bias"].append(bias)
            res[qname]["RMSE"].append(bias**2)
            res[qname]["Coverage"].append(1 if (lo <= true_vals[qname] <= hi) else 0)

    # summary of the results
    summary = {}
    for q in quantities:
        Bias = np.mean(res[q]["Bias"])
        RMSE = np.sqrt(np.mean(res[q]["RMSE"]))
        Coverage = np.mean(res[q]["Coverage"])
        summary[q] = {
            "True": true_vals[q],
            "Bias": Bias,
            "RMSE": RMSE,
            "Coverage": Coverage,
        }

    results[sc_name] = summary

# Display the results
pd.set_option("display.precision", 4)
for sc_name, res in results.items():
    print(f"\n***** Scenario: {sc_name} *****")
    print(pd.DataFrame(res).T)
