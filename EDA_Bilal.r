# Econometrics part of project:

# Read the given data file
df <- read.csv("ScanRecords.csv")


# Lets work on the scan duration first
dfI <- df[df$PatientType == "Type 1", ]
scansTypeI <- dfI$Duration

dfII <- df[df$PatientType == "Type 2",]
scansTypeII <- dfII$Duration

# Histogram for Type I patients' scan duration
hist(scansTypeI, 
     main = "Scan duration for patient type I",
     xlab =  "Scan duration in fractions of hours",
     col = "blue")


# Histogram for Type II patients' scan duration
hist(scansTypeII, 
     main = "Scan duration for patient type II",
     xlab =  "Scan duration in fractions of hours",
     col = "blue")

# Boxplot for Type I & II patients' scan duration
boxplot(scansTypeI, scansTypeII,
        main = "Boxplots for patient type I & II",
        names = c("Type I", "Type II"),
        col = c("orange", "red"),
        border = "brown",
        horizontal = TRUE,
        las = 1
        )

#Basic summary of scan duration data
summary(scansTypeI)
summary(scansTypeII)

scanMeanI <- mean(scansTypeI)
scanMeanII <- mean(scansTypeII)
scanSDI <- sd(scansTypeI)
scanSDII <- sd(scansTypeII)

# Set plotting area for side-by-side QQ plots
par(mfrow = c(1, 2))

# QQ plot for Type I patients
qqnorm(scansTypeI,
       main = "QQ Plot: Type I Scan Duration")
qqline(scansTypeI, col = "red", lwd = 2)

# QQ plot for Type II patients
qqnorm(scansTypeII,
       main = "QQ Plot: Type II Scan Duration")
qqline(scansTypeII, col = "red", lwd = 2)

# Reset plotting layout
par(mfrow = c(1, 1))



# Empirical CDFs
ecdfTypeI <- ecdf(scansTypeI)
ecdfTypeII <- ecdf(scansTypeII)

# Define ranges for smooth normal CDF curves
xI <- seq(min(scansTypeI), max(scansTypeI), length.out = 200)
xII <- seq(min(scansTypeII), max(scansTypeII), length.out = 200)

# Set plotting area
par(mfrow = c(1, 2))

# CDF comparison for Type I
plot(ecdfTypeI,
     main = "CDF Comparison: Type I",
     xlab = "Scan Duration",
     ylab = "CDF",
     col = "blue",
     lwd = 2)
lines(xI, pnorm(xI, mean = scanMeanI, sd = scanSDI),
      col = "red", lwd = 2, lty = 2)
legend("bottomright",
       legend = c("Empirical CDF", "Normal CDF"),
       col = c("blue", "red"),
       lty = c(1, 2),
       lwd = 2)

# CDF comparison for Type II
plot(ecdfTypeII,
     main = "CDF Comparison: Type II",
     xlab = "Scan Duration",
     ylab = "CDF",
     col = "blue",
     lwd = 2)
lines(xII, pnorm(xII, mean = scanMeanII, sd = scanSDII),
      col = "red", lwd = 2, lty = 2)
legend("bottomright",
       legend = c("Empirical CDF", "Normal CDF"),
       col = c("blue", "red"),
       lty = c(1, 2),
       lwd = 2)

# Reset layout
par(mfrow = c(1, 1))


# -----------------------------
# Arrival rate analysis
# -----------------------------

# Ensure Date is treated as a date
df$Date <- as.Date(df$Date)

# Split by patient type (already done, but we reuse)
dfI  <- df[df$PatientType == "Type 1", ]
dfII <- df[df$PatientType == "Type 2", ]

# -----------------------------
# Daily arrival counts
# -----------------------------

# Type I: number of arrivals per day
arrivalsI <- table(dfI$Date)
arrivalsI <- as.numeric(arrivalsI)

# Type II: number of arrivals per day
arrivalsII <- table(dfII$Date)
arrivalsII <- as.numeric(arrivalsII)

# -----------------------------
# Histograms of daily arrivals
# -----------------------------

hist(arrivalsI,
     main = "Daily arrivals for patient type I",
     xlab = "Number of arrivals per day",
     col = "lightblue",
     breaks = "Sturges")

hist(arrivalsII,
     main = "Daily arrivals for patient type II",
     xlab = "Number of arrivals per day",
     col = "lightgreen",
     breaks = "Sturges")

# -----------------------------
# Boxplot comparison
# -----------------------------

boxplot(arrivalsI, arrivalsII,
        names = c("Type I", "Type II"),
        main = "Daily arrival counts by patient type",
        col = c("lightblue", "lightgreen"),
        horizontal = TRUE,
        las = 1)

# -----------------------------
# Summary statistics
# -----------------------------

summary(arrivalsI)
summary(arrivalsII)

# -----------------------------
# Arrival rate estimates
# -----------------------------

# Mean arrivals per day
lambdaHatI  <- mean(arrivalsI)   # Poisson rate estimate for Type I
meanArrII   <- mean(arrivalsII)  # Empirical mean for Type II

# Variance diagnostics
varArrI  <- var(arrivalsI)
varArrII <- var(arrivalsII)

dispersionI  <- varArrI / lambdaHatI
dispersionII <- varArrII / meanArrII

cat("Arrival rate estimates:\n")
cat("Type I: lambda_hat =", round(lambdaHatI, 3),
    ", var/mean =", round(dispersionI, 3), "\n")

cat("Type II: mean arrivals =", round(meanArrII, 3),
    ", var/mean =", round(dispersionII, 3), "\n")


# -----------------------------
# QQ plots vs Poisson
# -----------------------------

# Function to create Poisson QQ plot
poissonQQ <- function(x, lambda, mainTitle) {
  n <- length(x)
  probs <- ppoints(n)
  theoQ <- qpois(probs, lambda = lambda)
  sampQ <- sort(x)
  
  plot(theoQ, sampQ,
       main = mainTitle,
       xlab = "Theoretical Poisson Quantiles",
       ylab = "Sample Quantiles",
       pch = 19, col = "blue")
  abline(0, 1, col = "red", lwd = 2)
}

par(mfrow = c(1, 2))

# Type I QQ plot
poissonQQ(arrivalsI, lambdaHatI,
          "Poisson QQ Plot: Type I Arrivals")

# Type II QQ plot
poissonQQ(arrivalsII, meanArrII,
          "Poisson QQ Plot: Type II Arrivals")

par(mfrow = c(1, 1))



# -----------------------------
# CDF comparison: empirical vs Poisson
# -----------------------------

# Empirical CDFs
ecdfArrI  <- ecdf(arrivalsI)
ecdfArrII <- ecdf(arrivalsII)

# Support for Poisson CDF
xI  <- 0:max(arrivalsI)
xII <- 0:max(arrivalsII)

par(mfrow = c(1, 2))

# Type I CDF comparison
plot(ecdfArrI,
     main = "CDF Comparison: Type I Arrivals",
     xlab = "Arrivals per day",
     ylab = "CDF",
     col = "blue",
     lwd = 2)
points(xI, ppois(xI, lambda = lambdaHatI),
       col = "red", pch = 19)
legend("bottomright",
       legend = c("Empirical CDF", "Poisson CDF"),
       col = c("blue", "red"),
       lty = c(1, NA),
       pch = c(NA, 19),
       lwd = 2)

# Type II CDF comparison
plot(ecdfArrII,
     main = "CDF Comparison: Type II Arrivals",
     xlab = "Arrivals per day",
     ylab = "CDF",
     col = "blue",
     lwd = 2)
points(xII, ppois(xII, lambda = meanArrII),
       col = "red", pch = 19)
legend("bottomright",
       legend = c("Empirical CDF", "Poisson CDF"),
       col = c("blue", "red"),
       lty = c(1, NA),
       pch = c(NA, 19),
       lwd = 2)

par(mfrow = c(1, 1))



# ==========================================
# TYPE I SCAN DURATIONS – PARAMETRIC BOOTSTRAP-t
# ==========================================

set.seed(2025)

x <- scansTypeI
n <- length(x)
B <- 5000

# Observed statistics
xbar <- mean(x)
s    <- sd(x)
se_obs <- s / sqrt(n)

# Bootstrap-t statistics
Tstar <- numeric(B)

for (b in 1:B) {
  # Parametric bootstrap sample
  sim <- rnorm(n, mean = xbar, sd = s)
  
  xbar_star <- mean(sim)
  s_star    <- sd(sim)
  se_star   <- s_star / sqrt(n)
  
  # Studentized statistic
  Tstar[b] <- (xbar_star - xbar) / se_star
}

# Studentized CI
alpha <- 0.05
q_low  <- quantile(Tstar, 1 - alpha/2)
q_high <- quantile(Tstar, alpha/2)

ci_typeI_scan_mean <- c(
  xbar - q_low  * se_obs,
  xbar - q_high * se_obs
)

cat("Type I scan mean – studentized 95% CI:\n")
print(ci_typeI_scan_mean)


# ==========================================
# TYPE I ARRIVALS – PARAMETRIC POISSON BOOTSTRAP
# ==========================================

set.seed(2025)

x <- arrivalsI
n_days <- length(x)
lambda_hat <- mean(x)

B <- 5000
lambda_star <- numeric(B)

for (b in 1:B) {
  sim <- rpois(n_days, lambda = lambda_hat)
  lambda_star[b] <- mean(sim)
}

# Bootstrap CI for lambda
ci_typeI_lambda <- quantile(lambda_star, c(0.025, 0.975))

cat("Type I arrival rate λ – 95% bootstrap CI:\n")
print(ci_typeI_lambda)


# ==========================================
# TYPE II SCAN DURATIONS – NONPARAMETRIC BOOTSTRAP
# ==========================================

set.seed(2025)

x <- scansTypeII
n <- length(x)
B <- 5000

boot_means_II <- numeric(B)

for (b in 1:B) {
  sim <- sample(x, size = n, replace = TRUE)
  boot_means_II[b] <- mean(sim)
}

# Percentile CI
ci_typeII_scan_mean <- quantile(boot_means_II, c(0.025, 0.975))

cat("Type II scan mean – nonparametric 95% CI:\n")
print(ci_typeII_scan_mean)



# ==========================================
# TYPE II ARRIVALS – NONPARAMETRIC BOOTSTRAP
# ==========================================

set.seed(2025)

x <- arrivalsII
n_days <- length(x)
B <- 5000

boot_mean_arrivals_II <- numeric(B)

for (b in 1:B) {
  sim <- sample(x, size = n_days, replace = TRUE)
  boot_mean_arrivals_II[b] <- mean(sim)
}

# Percentile CI
ci_typeII_arrivals <- quantile(boot_mean_arrivals_II, c(0.025, 0.975))

cat("Type II arrivals mean – nonparametric 95% CI:\n")
print(ci_typeII_arrivals)


# ==========================================
# SUMMARY OF ALL BOOTSTRAPS
# ==========================================

bootstrap_summary <- data.frame(
  Quantity = c("Type I scan mean",
               "Type I arrival rate λ",
               "Type II scan mean",
               "Type II arrivals mean"),
  Lower = c(ci_typeI_scan_mean[1],
            ci_typeI_lambda[1],
            ci_typeII_scan_mean[1],
            ci_typeII_arrivals[1]),
  Upper = c(ci_typeI_scan_mean[2],
            ci_typeI_lambda[2],
            ci_typeII_scan_mean[2],
            ci_typeII_arrivals[2])
)

print(bootstrap_summary)




# ===========================================================================
# Clinically interpretable quantities
# ===========================================================================

# ==========================================
# PROBABILITY OF SLOT OVERRUN
# ==========================================

slot_I  <- 0.5   # 30 minutes
slot_II <- 0.75  # 45 minutes

# Plug-in estimates
p_over_I  <- mean(scansTypeI  > slot_I)
p_over_II <- mean(scansTypeII > slot_II)

# ==========================================
# TYPE I: Probability of slot overrun (parametric bootstrap)
# ==========================================

B <- 5000
mu_hat <- mean(scansTypeI)
sd_hat <- sd(scansTypeI)
n_I <- length(scansTypeI)

p_over_I_star <- numeric(B)

for (b in 1:B) {
  sim <- rnorm(n_I, mean = mu_hat, sd = sd_hat)
  p_over_I_star[b] <- mean(sim > slot_I)
}

ci_p_over_I <- quantile(p_over_I_star, c(0.025, 0.975))

cat("Probability Type I scan exceeds 30 min:\n")
cat("Estimate =", round(p_over_I,3),
    ", 95% CI =", round(ci_p_over_I[1],3), "-", round(ci_p_over_I[2],3), "\n\n")


# Bootstrap uncertainty (nonparametric)
B <- 5000
p_over_II_star <- numeric(B)

for (b in 1:B) {
  sim <- sample(scansTypeII, replace = TRUE)
  p_over_II_star[b] <- mean(sim > slot_II)
}

ci_p_over_II <- quantile(p_over_II_star, c(0.025, 0.975))

cat("Probability Type II scan exceeds 45 min:\n")
cat("Estimate =", round(p_over_II,3),
    ", 95% CI =", round(ci_p_over_II[1],3), "-", round(ci_p_over_II[2],3), "\n")



# ======================================================
# Upper qunatiles of scan durations
#=======================================================


# ==========================================
# TYPE I: 90th percentile of scan duration (parametric bootstrap)
# ==========================================

q90_I_star <- numeric(B)

for (b in 1:B) {
  sim <- rnorm(n_I, mean = mu_hat, sd = sd_hat)
  q90_I_star[b] <- quantile(sim, 0.9)
}

ci_q90_I <- quantile(q90_I_star, c(0.025, 0.975))

cat("Type I 90th percentile scan duration (hours):\n")
print(ci_q90_I)



# 90th percentile + bootstrap CI (Type II)
q90_hat <- quantile(scansTypeII, 0.9)

q90_star <- numeric(B)
for (b in 1:B) {
  sim <- sample(scansTypeII, replace = TRUE)
  q90_star[b] <- quantile(sim, 0.9)
}

ci_q90 <- quantile(q90_star, c(0.025, 0.975))

cat("Type II 90th percentile scan duration:\n")
print(ci_q90)



# ========================================================
# Justification of non-parametric bootstrap for Type II
# ========================================================

# ==========================================
# MONTE CARLO STUDY – TYPE II SCANS
# ==========================================

set.seed(123)
MC <- 1000
n  <- length(scansTypeII)

true_dist <- function(n) rgamma(n, shape = 4, scale = 0.17)
true_mean <- 4 * 0.17

bias <- numeric(MC)
covered <- logical(MC)

for (m in 1:MC) {
  data <- true_dist(n)
  
  # bootstrap CI
  boot <- replicate(500, mean(sample(data, replace = TRUE)))
  ci <- quantile(boot, c(0.025, 0.975))
  
  bias[m] <- mean(data) - true_mean
  covered[m] <- ci[1] <= true_mean & ci[2] >= true_mean
}

cat("Monte Carlo results:\n")
cat("Bias:", round(mean(bias),4), "\n")
cat("Coverage:", mean(covered), "\n")



# =======================================================
#  Probability daily arrivals exceed capacity
# =======================================================

cap_I <- 16

# Type I (parametric Poisson)
p_over_cap_I <- 1 - ppois(cap_I, lambdaHatI)

# Bootstrap CI
p_over_cap_I_star <- numeric(B)
for (b in 1:B) {
  lambda_star <- mean(rpois(length(arrivalsI), lambdaHatI))
  p_over_cap_I_star[b] <- 1 - ppois(cap_I, lambda_star)
}

quantile(p_over_cap_I_star, c(0.025, 0.975))


# ==========================================
# TYPE II: Probability daily arrivals exceed capacity
# ==========================================

cap_II <- 12   # choose a realistic capacity

# Plug-in estimate
p_over_cap_II <- mean(arrivalsII > cap_II)

# Bootstrap CI (nonparametric)
p_over_cap_II_star <- numeric(B)

for (b in 1:B) {
  sim <- sample(arrivalsII, replace = TRUE)
  p_over_cap_II_star[b] <- mean(sim > cap_II)
}

ci_p_over_cap_II <- quantile(p_over_cap_II_star, c(0.025, 0.975))

cat("Probability Type II arrivals exceed capacity:\n")
cat("Estimate =", round(p_over_cap_II,3),
    ", 95% CI =", round(ci_p_over_cap_II[1],3), "-", round(ci_p_over_cap_II[2],3), "\n\n")



# =======================================================
#  upper quantile of daily arrivals
# =======================================================
# Nonparametric (Type II arrivals)
q95_arr_II <- quantile(arrivalsII, 0.95)

q95_star <- replicate(B, {
  quantile(sample(arrivalsII, replace = TRUE), 0.95)
})

quantile(q95_star, c(0.025, 0.975))





