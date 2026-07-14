# GARCH(1,1) Analysis of HBL Using PSX Data

## 1. Purpose of This Analysis

The purpose of this analysis is to study whether HBL stock returns exhibit time-varying volatility.

Earlier, a geometric Brownian motion model was fitted to HBL data. That model assumed a constant volatility parameter. However, the rolling-volatility diagnostics showed that HBL volatility changes substantially through time.

This motivates the use of a GARCH model.

The central question is:

> Does a GARCH(1,1) model provide a more realistic description of HBL return volatility than the constant-volatility GBM benchmark?

The data is obtained from the PSX REST API:

```text
https://psx-rest-api.onrender.com
```

---

## 2. Data and Returns

The analysis uses daily historical closing prices for HBL.

The sample period is:

```text
2016-07-15 to 2026-07-14
```

The number of return observations is:

```text
2475
```

The daily log return is computed as

```math
r_t
=
\log\left(\frac{S_t}{S_{t-1}}\right),
```

where $S_t$ is the closing price on day $t$.

GARCH models are fitted to returns rather than directly to prices, because the main object of interest is the changing conditional variance of returns.

---

## 3. Model Specification

The fitted model is a constant-mean GARCH(1,1) model.

The return equation is

```math
r_t = \mu + \varepsilon_t,
```

where $\varepsilon_t$ is the unexpected return shock.

The shock is written as

```math
\varepsilon_t = \sigma_t z_t,
```

where $\sigma_t$ is the conditional volatility and $z_t$ is a standardized innovation.

The GARCH(1,1) variance equation is

```math
\sigma_t^2
=
\omega
+
\alpha \varepsilon_{t-1}^2
+
\beta \sigma_{t-1}^2.
```

This equation says that today’s conditional variance depends on:

1. a baseline variance level, $\omega$;
2. yesterday’s squared shock, $\varepsilon_{t-1}^2$;
3. yesterday’s conditional variance, $\sigma_{t-1}^2$.

---

## 4. Estimated Parameters

The fitted GARCH(1,1) model produced the following estimates:

```text
mu:       -0.030924
omega:     0.571127
alpha[1]:  0.193074
beta[1]:   0.668141
alpha[1] + beta[1]: 0.861214
```

The estimated variance equation is therefore approximately

```math
\sigma_t^2
=
0.5711
+
0.1931\varepsilon_{t-1}^2
+
0.6681\sigma_{t-1}^2.
```

Returns were expressed in percentage units for the GARCH estimation. This is common in applied GARCH work because it improves numerical stability.

---

## 5. Interpretation of the Mean Parameter

The estimated mean parameter is

```text
mu = -0.030924
```

Its p-value is approximately

```text
0.471
```

This means the mean return parameter is not statistically significant in this fitted model.

This is not surprising. In daily financial-return models, the conditional mean is often difficult to estimate precisely. The main object of interest in a GARCH model is usually not the mean return, but the conditional variance.

Therefore, the important conclusions should come primarily from the volatility equation rather than from the mean equation.

---

## 6. Interpretation of the Volatility Parameters

### 6.1 Shock response: alpha

The estimate of $\alpha$ is

```text
alpha[1] = 0.193074
```

The p-value for $\alpha$ is approximately

```text
0.007168
```

This is statistically significant.

The parameter $\alpha$ measures how strongly volatility reacts to recent shocks. A large unexpected return yesterday increases today’s conditional volatility.

The estimate suggests that HBL volatility responds meaningfully to new market shocks.

In practical terms:

> When HBL experiences a large unexpected daily movement, the model expects volatility to rise afterward.

---

### 6.2 Volatility persistence: beta

The estimate of $\beta$ is

```text
beta[1] = 0.668141
```

The p-value for $\beta$ is approximately

```text
0.000006353
```

This is highly statistically significant.

The parameter $\beta$ measures persistence in volatility. It tells us how much yesterday’s conditional variance carries into today.

The estimate suggests that HBL volatility is persistent. Once volatility becomes high, it tends to remain elevated for some time.

In practical terms:

> HBL has volatility clustering: turbulent periods tend to be followed by turbulent periods, and calm periods tend to be followed by calm periods.

---

### 6.3 Overall persistence: alpha plus beta

The sum of the GARCH persistence parameters is

```text
alpha[1] + beta[1] = 0.861214
```

This is below one:

```math
\alpha + \beta < 1.
```

This is important because, in a standard GARCH(1,1) model, $\alpha+\beta<1$ is associated with covariance stationarity.

The estimate implies that volatility shocks are persistent but not permanent.

In other words:

> HBL volatility is mean-reverting, but it returns to its long-run level gradually rather than immediately.

This is a realistic result for financial-market data.

---

## 7. Comparison With GBM Volatility

The earlier GBM model estimated one constant annual volatility:

```text
GBM constant annual volatility: 31.73%
```

The GARCH model produced a time-varying conditional volatility series. Its summary values were:

```text
Average GARCH annual volatility: 30.52%
Latest GARCH annual volatility: 28.97%
```

The average GARCH volatility is close to the GBM constant volatility. This is reassuring because both models are using the same underlying return data.

However, the interpretation is different.

GBM compresses the whole volatility history into one number:

```math
\sigma = 31.73\%.
```

GARCH instead gives a sequence of conditional volatilities:

```math
\sigma_1,\sigma_2,\ldots,\sigma_t.
```

This allows the model to identify periods when HBL was more or less risky than usual.

Therefore, the GBM volatility estimate is useful as a broad benchmark, while the GARCH volatility estimate is more informative for studying changing risk.

---

## 8. Main Empirical Finding

The GARCH results support the conclusion that HBL returns exhibit time-varying volatility.

The strongest evidence is:

1. $\alpha$ is statistically significant;
2. $\beta$ is statistically significant;
3. $\alpha+\beta=0.861214$, indicating persistent but mean-reverting volatility;
4. the fitted conditional volatility varies over time;
5. the GARCH volatility series is more flexible than the constant-volatility GBM benchmark.

The main empirical finding is:

```text
HBL volatility is dynamic, shock-sensitive, persistent, and mean-reverting.
```

---

## 9. What GARCH Adds Beyond GBM

The GBM model is

```math
dS_t
=
\mu S_t\,dt
+
\sigma S_t\,dW_t.
```

In this model, $\sigma$ is constant.

This is mathematically elegant and useful as a first model, but it cannot describe volatility clustering.

The GARCH model replaces the constant-volatility idea with a conditional-volatility process:

```math
r_t = \mu + \sigma_t z_t,
```

```math
\sigma_t^2
=
\omega
+
\alpha \varepsilon_{t-1}^2
+
\beta \sigma_{t-1}^2.
```

This gives the model memory.

It remembers recent shocks and recent volatility levels. That is why GARCH can describe periods of calm and turbulence more realistically than GBM.

---

## 10. Interpretation of the GARCH Volatility Plot

The plot

```text
garch_vs_gbm_volatility.png
```

compares two ideas:

1. GBM constant annual volatility;
2. GARCH annualized conditional volatility.

The horizontal GBM line represents a single fixed volatility estimate.

The GARCH curve moves over time, showing the model’s estimate of changing risk.

When the GARCH curve is above the GBM line, HBL is experiencing higher-than-average conditional volatility.

When the GARCH curve is below the GBM line, HBL is experiencing lower-than-average conditional volatility.

This plot is important because it makes the main limitation of GBM visually clear:

> A single volatility number cannot describe all periods equally well.

---

## 11. Interpretation of Standardized Residuals

After fitting the GARCH model, the standardized residuals are

```math
z_t
=
\frac{\varepsilon_t}{\sigma_t}.
```

These residuals are the shocks after adjusting for time-varying volatility.

The purpose of looking at standardized residuals is to ask:

> After GARCH has explained changing volatility, do the remaining shocks look more stable?

If the GARCH model is successful, the standardized residuals should show less volatility clustering than the original returns.

However, standardized residuals may still have heavy tails. This means a normal innovation distribution may still be too simple.

This is why a natural next step is to fit a GARCH model with Student-$t$ innovations.

---

## 12. Limitations of the Current Model

The fitted GARCH(1,1) model is useful, but it remains a simplified model.

Important limitations include:

1. It assumes symmetric volatility response.
2. Positive and negative shocks of the same size affect volatility equally.
3. It uses normal innovations.
4. It is a discrete-time model, not a continuous-time SDE.
5. It models conditional variance, not the full stock-price process directly.

The normal innovation assumption may be too restrictive because financial returns often have heavier tails than the normal distribution.

A better next version may use Student-$t$ innovations:

```text
GARCH(1,1) with Student-t errors
```

This would allow more probability for extreme returns.

---

## 13. Connection to Stochastic Volatility SDEs

This GARCH analysis prepares the ground for stochastic volatility models.

In GBM, volatility is constant:

```math
dS_t
=
\mu S_t\,dt
+
\sigma S_t\,dW_t.
```

In GARCH, volatility changes in discrete time:

```math
\sigma_t^2
=
\omega
+
\alpha \varepsilon_{t-1}^2
+
\beta \sigma_{t-1}^2.
```

In stochastic volatility models, volatility changes in continuous time and follows its own stochastic differential equation.

For example, the Heston model has the structure

```math
dS_t
=
\mu S_t\,dt
+
\sqrt{v_t}S_t\,dW_t^{(1)},
```

```math
dv_t
=
\kappa(\theta-v_t)\,dt
+
\xi\sqrt{v_t}\,dW_t^{(2)}.
```

The conceptual progression is therefore:

```text
GBM:
constant volatility

GARCH:
time-varying conditional volatility in discrete time

Stochastic volatility SDE:
random volatility in continuous time
```

The GARCH analysis shows why the stochastic volatility idea is natural.

The data itself suggests that volatility should not be treated as a constant.

---

## 14. Professional Summary

The GARCH(1,1) analysis of HBL indicates that return volatility is both shock-sensitive and persistent. The estimate of $\alpha$ suggests that new market shocks have a statistically significant immediate effect on volatility, while the estimate of $\beta$ indicates that volatility remains elevated after turbulent periods. Since $\alpha+\beta=0.861214<1$, the conditional variance process appears mean-reverting, although volatility shocks decay gradually.

Compared with the constant-volatility GBM benchmark, the GARCH model provides a more realistic description of HBL by allowing volatility to vary through time. The GBM volatility estimate remains useful as an average benchmark, but the GARCH conditional-volatility series better captures the changing risk visible in the historical data.

The results therefore support the use of GARCH as a natural intermediate step between GBM and continuous-time stochastic volatility models.

---

## 15. Main Takeaway

The main lesson is:

```text
GBM gives a first stochastic model of prices.

Diagnostics show that volatility is not constant.

GARCH gives a statistical model for changing volatility.

This motivates stochastic volatility SDEs.
```

For HBL, the fitted GARCH model suggests that volatility is not random noise with a fixed scale. It has structure, persistence, and mean reversion.

This is the essential empirical reason to move beyond constant-volatility GBM.