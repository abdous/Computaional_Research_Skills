# Econometric part of the project 
# Step 1: Exploratory Data Analysis
# MRI Scan Case - ScanRecords.csv


# Install 
# install.packages(c("tidyverse", "lubridate"))
library(tidyverse)
library(lubridate)

#Load data

df <- read_csv("C:/Users/User/Downloads/ScanRecords.csv")

# Check structure
glimpse(df)

df <- df %>%
  mutate(
    Date = as.Date(Date),
    Time = as.numeric(Time),
    Duration = as.numeric(Duration),
    # Clean PatientType labels: trim spaces, fix capitalization
    PatientType = str_trim(PatientType),          # removes leading/trailing spaces
    PatientType = str_to_title(PatientType),      # ensures "Type 1", "Type 2" format
    PatientType = factor(PatientType)
  )

# Check unique values and counts
df %>% count(PatientType)

# Confirm total number of rows still matches expectation
nrow(df)

# 3. Summary statistics 

summary(df)
table(df$PatientType)

# Summary per patient type 

duration_summary <- df %>%
  group_by(PatientType) %>%
  summarise(
    n = n(),
    mean_duration = mean(Duration),
    sd_duration = sd(Duration),
    min_duration = min(Duration),
    q25_duration = quantile(Duration, 0.25),
    median_duration = median(Duration),
    q75_duration = quantile(Duration, 0.75),
    max_duration = max(Duration)
  )

duration_summary

# 3. Distribution of scan durations 

# Histogram + density for each type
ggplot(df, aes(x = Duration, fill = PatientType)) +
  geom_histogram(aes(y = ..density..), bins = 30, alpha = 0.4, position = "identity") +
  geom_density(alpha = 0.7) +
  facet_wrap(~ PatientType, scales = "free_y") +
  labs(
    title = "Distribution of Scan Durations by Patient Type",
    x = "Duration (hours)",
    y = "Density"
  ) +
  theme_minimal()

# 4. Arrival times during the day (call times)
ggplot(df, aes(x = Time, fill = PatientType)) +
  geom_histogram(bins = 30, alpha = 0.5, position = "identity") +
  facet_wrap(~ PatientType, ncol = 1) +
  labs(
    title = "Distribution of Call Times by Patient Type",
    x = "Time of Day (hours)",
    y = "Number of calls"
  ) +
  theme_minimal()

# 5. Daily number of patients (per type) 


daily_counts <- df %>%
  group_by(Date, PatientType) %>%
  summarise(
    n_patients = n(),
    .groups = "drop"
  )

# Look at basic stats of daily counts
daily_counts %>%
  group_by(PatientType) %>%
  summarise(
    mean_per_day = mean(n_patients),
    sd_per_day = sd(n_patients),
    min_per_day = min(n_patients),
    max_per_day = max(n_patients)
  )

# Plot daily counts over time
ggplot(daily_counts, aes(x = Date, y = n_patients, color = PatientType)) +
  geom_line() +
  geom_point() +
  facet_wrap(~ PatientType, ncol = 1, scales = "free_y") +
  labs(
    title = "Daily Number of Patients by Type",
    x = "Date",
    y = "Number of patients"
  ) +
  theme_minimal()

# Histogram of daily counts (useful for Poisson check later)
ggplot(daily_counts, aes(x = n_patients)) +
  geom_histogram(binwidth = 1, fill = "grey80", color = "black") +
  facet_wrap(~ PatientType, scales = "free_y") +
  labs(
    title = "Distribution of Daily Patient Counts",
    x = "Number of patients per day",
    y = "Frequency"
  ) +
  theme_minimal()


# BOOTSTRAP: Type 1 duration

set.seed(123)  # for reproducibility
B <- 1000       # number of bootstrap replications

# Extract Type 1 durations
X <- df$Duration[df$PatientType == "Type 1"]
n <- length(X)

# True sample estimates (from real data)
mean_X <- mean(X)
q90_X  <- quantile(X, 0.90)

mean_X
q90_X

# Storage for bootstrap statistics
mean_star <- rep(NA, times = B)
q90_star  <- rep(NA, times = B)

for (b in 1:B) {
  # draw indices with replacement (slides style)
  J <- sample.int(n, size = n, replace = TRUE)
  
  # bootstrap sample
  X_star <- X[J]
  
  # compute bootstrap stats
  mean_star[b] <- mean(X_star)
  q90_star[b]  <- quantile(X_star, 0.90)
}

# Bootstrap standard errors
se_mean_boot <- sd(mean_star)
se_q90_boot  <- sd(q90_star)

se_mean_boot
se_q90_boot

# 95% bootstrap percentile CIs
CI_mean <- quantile(mean_star, probs = c(0.025, 0.975))
CI_q90  <- quantile(q90_star,  probs = c(0.025, 0.975))

CI_mean
CI_q90


# BOOTSTRAP: Type 2 duration


set.seed(123)       # for reproducibility
B <- 1000           # number of bootstrap replications

# 1. Extract Type 2 durations

X2 <- df$Duration[df$PatientType == "Type 2"]
n2 <- length(X2)

# 2. Sample estimates from the real data

mean_X2   <- mean(X2)
median_X2 <- median(X2)
q90_X2    <- quantile(X2, 0.90)
p_gt1_X2  <- mean(X2 > 1)   # probability duration > 1 hour

mean_X2
median_X2
q90_X2
p_gt1_X2

# 3. Storage for bootstrap statistics
mean_star_2   <- rep(NA, B)
median_star_2 <- rep(NA, B)
q90_star_2    <- rep(NA, B)
p_gt1_star_2  <- rep(NA, B)

# 4. Bootstrap loop
for (b in 1:B) {
  # draw indices with replacement
  J <- sample.int(n2, size = n2, replace = TRUE)
  
  # bootstrap sample
  X2_star <- X2[J]
  
  # compute bootstrap statistics
  mean_star_2[b]   <- mean(X2_star)
  median_star_2[b] <- median(X2_star)
  q90_star_2[b]    <- quantile(X2_star, 0.90)
  p_gt1_star_2[b]  <- mean(X2_star > 1)
}

# 5. Bootstrap standard errors
se_mean_2   <- sd(mean_star_2)
se_median_2 <- sd(median_star_2)
se_q90_2    <- sd(q90_star_2)
se_pgt1_2   <- sd(p_gt1_star_2)

se_mean_2
se_median_2
se_q90_2
se_pgt1_2

# 6. 95% bootstrap percentile CIs
CI_mean_2   <- quantile(mean_star_2,   probs = c(0.025, 0.975))
CI_median_2 <- quantile(median_star_2, probs = c(0.025, 0.975))
CI_q90_2    <- quantile(q90_star_2,    probs = c(0.025, 0.975))
CI_pgt1_2   <- quantile(p_gt1_star_2,  probs = c(0.025, 0.975))

CI_mean_2
CI_median_2
CI_q90_2
CI_pgt1_2

# 7. Optional: put everything in a small summary table 

type2_boot_summary <- tibble::tibble(
  Quantity      = c("Mean", "Median", "90th percentile", "Prob(Duration > 1h)"),
  Estimate      = c(mean_X2, median_X2, q90_X2, p_gt1_X2),
  Boot_SE       = c(se_mean_2, se_median_2, se_q90_2, se_pgt1_2),
  CI_lower_2.5  = c(CI_mean_2[1], CI_median_2[1], CI_q90_2[1], CI_pgt1_2[1]),
  CI_upper_97.5 = c(CI_mean_2[2], CI_median_2[2], CI_q90_2[2], CI_pgt1_2[2])
)

type2_boot_summary


