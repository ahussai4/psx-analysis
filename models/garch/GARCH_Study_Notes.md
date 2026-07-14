# GARCH Models: A Practical Introduction Through PSX Data

## Purpose of These Notes

These notes introduce GARCH models as a response to a specific empirical problem:

> Financial-market volatility is not constant through time.

In our earlier analysis of HBL, a geometric Brownian motion model was fitted to historical PSX prices. That model provided a useful first approximation, but the diagnostics revealed two important limitations:

1. The distribution of standardized returns was more sharply peaked and had heavier tails than a normal distribution.
2. The 60-day rolling volatility changed substantially over time.

The second finding is especially important. Geometric Brownian motion assumes a constant volatility parameter, whereas the HBL data showed alternating periods of calm and turbulence.

GARCH models are designed to describe this changing volatility.

---

## 1. Begin With the Empirical Question

Suppose $S_t$ denotes the closing price of a stock on trading day $t$. Rather than modelling the price directly, GARCH models are usually fitted to returns.

The continuously compounded, or log, return is

```math
r_t
=
\log\left(\frac{S_t}{S_{t-1}}\right).
```

A return series often looks quite different from a price series.

Prices may exhibit long upward or downward trends. Returns, by contrast, typically fluctuate around a relatively stable mean. However, the size of those fluctuations is often not stable.

A financial return series commonly displays periods such as:

- many consecutive days of small movements;
- several consecutive days of large movements;
- sudden volatility spikes;
- a gradual return from turbulent conditions to calmer conditions.

This empirical pattern is called **volatility clustering**.

Volatility clustering does not mean that positive returns are necessarily followed by positive returns. It means that large movements, whether positive or negative, tend to occur near other large movements.

---

## 2. Conditional Variance

To understand GARCH, it is essential to distinguish between **unconditional variance** and **conditional variance**.

The unconditional variance describes the overall variability of the return series across the full sample.

The conditional variance asks a more local question:

> Given the information available up to yesterday, how uncertain is today’s return?

Let $\mathcal{F}_{t-1}$ represent all information available before observing the return at time $t$. The conditional variance of the return is then

```math
\operatorname{Var}(r_t \mid \mathcal{F}_{t-1}).
```

In a GARCH model, this conditional variance changes over time.

We write it as

```math
\sigma_t^2
=
\operatorname{Var}(r_t \mid \mathcal{F}_{t-1}).
```

Thus, $\sigma_t$ is not one fixed number. It is a time series of conditional volatilities.

---

## 3. The Return Equation

A basic return equation can be written as

```math
r_t = \mu + \varepsilon_t,
```

where:

- $r_t$ is the return at time $t$;
- $\mu$ is the conditional mean return;
- $\varepsilon_t$ is the unexpected part of the return.

The shock $\varepsilon_t$ is written as

```math
\varepsilon_t = \sigma_t z_t,
```

where:

- $\sigma_t$ is the conditional volatility;
- $z_t$ is a standardized innovation.

Therefore,

```math
r_t = \mu + \sigma_t z_t.
```

The standardized innovations are usually assumed to satisfy

```math
E[z_t]=0,
\qquad
\operatorname{Var}(z_t)=1.
```

A first model may assume

```math
z_t \sim N(0,1).
```

For financial returns, a Student-$t$ distribution is often considered because it allows heavier tails than the normal distribution.

The key point is that the innovation $z_t$ has constant unit variance, while the scale $\sigma_t$ changes through time.

---

## 4. From ARCH to GARCH

### 4.1 The ARCH idea

An ARCH model allows today’s variance to depend on previous squared shocks.

An ARCH(1) model is

```math
\sigma_t^2
=
\omega
+
\alpha \varepsilon_{t-1}^2.
```

A large value of $\varepsilon_{t-1}^2$ means that yesterday contained a large unexpected movement. The model responds by increasing today’s conditional variance.

This captures the immediate effect of recent news or market turbulence.

However, an ARCH model may require many lagged squared shocks to reproduce persistent volatility.

---

### 4.2 The GARCH extension

GARCH stands for

> Generalized Autoregressive Conditional Heteroskedasticity.

The most widely used specification is GARCH(1,1):

```math
\sigma_t^2
=
\omega
+
\alpha \varepsilon_{t-1}^2
+
\beta \sigma_{t-1}^2.
```

The notation GARCH(1,1) refers to:

- one lag of the squared shock;
- one lag of the conditional variance.

This compact model is often able to reproduce persistent volatility with only three variance parameters.

---

## 5. Interpreting the GARCH(1,1) Parameters

The variance equation is

```math
\sigma_t^2
=
\omega
+
\alpha \varepsilon_{t-1}^2
+
\beta \sigma_{t-1}^2.
```

Each parameter has a distinct role.

### 5.1 The baseline term: $\omega$

The parameter $\omega$ is a positive constant.

It prevents the conditional variance from collapsing permanently to zero and contributes to the long-run level of variance.

A larger $\omega$ generally corresponds to a higher baseline variance, although it should not be interpreted in isolation from $\alpha$ and $\beta$.

---

### 5.2 The shock-response parameter: $\alpha$

The parameter $\alpha$ measures how strongly volatility reacts to recent unexpected returns.

The term

```math
\alpha \varepsilon_{t-1}^2
```

is large when yesterday’s return differed substantially from its expected value.

A larger $\alpha$ means that volatility reacts more sharply to new shocks.

This is often called the **ARCH effect** or the **news effect**.

---

### 5.3 The persistence parameter: $\beta$

The parameter $\beta$ measures how strongly yesterday’s variance carries into today.

The term

```math
\beta \sigma_{t-1}^2
```

allows a high-volatility period to remain volatile even when the most recent return is not extreme.

A large $\beta$ indicates that volatility decays slowly.

This is the main mechanism through which GARCH reproduces volatility clustering.

---

## 6. Positivity and Stationarity Conditions

For a standard GARCH(1,1) model, the usual parameter restrictions are

```math
\omega > 0,
\qquad
\alpha \geq 0,
\qquad
\beta \geq 0.
```

These restrictions help ensure that the conditional variance remains nonnegative.

A commonly used condition for covariance stationarity is

```math
\alpha + \beta < 1.
```

Under this condition, the unconditional variance of the shocks is

```math
\operatorname{Var}(\varepsilon_t)
=
\frac{\omega}{1-\alpha-\beta}.
```

This formula is important because it connects the changing conditional variance to a stable long-run variance.

When $\alpha+\beta$ is close to one, volatility is highly persistent. A shock to volatility may take a long time to disappear.

When $\alpha+\beta$ is substantially below one, volatility returns more quickly toward its long-run level.

---

## 7. Persistence and Mean Reversion

A GARCH model does not imply that volatility wanders without structure.

When $\alpha+\beta<1$, conditional variance tends to revert toward its long-run mean.

The long-run variance is

```math
\bar{\sigma}^2
=
\frac{\omega}{1-\alpha-\beta}.
```

The corresponding long-run volatility is

```math
\bar{\sigma}
=
\sqrt{\frac{\omega}{1-\alpha-\beta}}.
```

This gives GARCH two important features at the same time:

- volatility changes from day to day;
- volatility remains anchored to a long-run level.

This is more realistic than assuming that volatility is either completely constant or completely unrestricted.

---

## 8. Why Squared Shocks Appear

The sign of a return does not determine its contribution to volatility.

A return of $+5\%$ and a return of $-5\%$ are equally large in magnitude. Both indicate an unusually large movement.

Squaring the shock removes its sign:

```math
(+0.05)^2 = (-0.05)^2.
```

Therefore, $\varepsilon_{t-1}^2$ measures the size of yesterday’s surprise rather than its direction.

The standard GARCH model treats positive and negative shocks of equal magnitude symmetrically.

This symmetry can be unrealistic because bad news sometimes increases volatility more strongly than good news. Models such as EGARCH and GJR-GARCH are designed to capture this asymmetry.

For the first analysis, GARCH(1,1) remains the appropriate starting point.

---

## 9. GARCH Is a Model for Returns, Not Prices

A common conceptual mistake is to interpret GARCH as a direct stock-price model.

GARCH primarily describes the conditional variance of returns.

The model is

```math
r_t = \mu + \sigma_t z_t,
```

together with

```math
\sigma_t^2
=
\omega
+
\alpha \varepsilon_{t-1}^2
+
\beta \sigma_{t-1}^2.
```

Prices can be reconstructed from returns through

```math
S_t = S_{t-1}e^{r_t},
```

but the GARCH mechanism itself operates through the return variance.

This differs from geometric Brownian motion, which specifies the stock-price dynamics directly in continuous time.

---

## 10. GBM and GARCH Answer Different Questions

The geometric Brownian motion model is

```math
dS_t
=
\mu S_t\,dt
+
\sigma S_t\,dW_t.
```

Here, $\sigma$ is constant.

GARCH instead uses a changing conditional volatility $\sigma_t$.

| Feature | Geometric Brownian motion | GARCH |
|---|---|---|
| Time framework | Continuous time | Discrete time |
| Main object | Stock price | Return variance |
| Volatility | Constant | Time-varying |
| Volatility clustering | Not captured | Captured |
| Brownian motion | Explicitly present | Not explicit |
| Estimation from daily returns | Straightforward | Straightforward |
| Common use | Pricing and simulation | Volatility forecasting and risk |

It is therefore misleading to think of GARCH simply as a “better GBM.”

They are different types of models.

GBM gives a continuous-time stochastic process for prices. GARCH gives a discrete-time dynamic model for conditional return variance.

---

## 11. Connection With Stochastic Volatility Models

GARCH provides a natural conceptual bridge toward stochastic volatility SDEs.

A continuous-time stochastic volatility model may be written as

```math
dS_t
=
\mu S_t\,dt
+
\sqrt{v_t}S_t\,dW_t^{(1)},
```

together with a second stochastic differential equation for variance:

```math
dv_t
=
\kappa(\theta-v_t)\,dt
+
\xi\sqrt{v_t}\,dW_t^{(2)}.
```

This is the structure of the Heston model.

Here:

- $v_t$ is the instantaneous variance;
- $\theta$ is the long-run variance level;
- $\kappa$ controls the speed of mean reversion;
- $\xi$ is the volatility of variance;
- $W_t^{(1)}$ and $W_t^{(2)}$ may be correlated.

The progression is therefore:

```text
GBM
    constant volatility in continuous time

GARCH
    predictable time-varying conditional volatility in discrete time

Stochastic volatility
    random volatility governed by its own continuous-time SDE
```

GARCH is not itself a stochastic volatility SDE, but it teaches the central empirical lesson that motivates such models: volatility is dynamic.

---

## 12. Estimating a GARCH Model

GARCH parameters are generally estimated by maximum likelihood.

The procedure can be summarized conceptually as follows:

1. Choose tentative values of $\mu$, $\omega$, $\alpha$, and $\beta$.
2. Use the variance recursion to calculate each $\sigma_t^2$.
3. Compute the likelihood of the observed returns under the assumed innovation distribution.
4. Adjust the parameters to maximize the likelihood.

The fitted model produces:

- estimates of $\mu$, $\omega$, $\alpha$, and $\beta$;
- a conditional variance series $\sigma_t^2$;
- a conditional volatility series $\sigma_t$;
- residuals $\varepsilon_t$;
- standardized residuals

```math
z_t = \frac{\varepsilon_t}{\sigma_t}.
```

If the model is adequate, the standardized residuals should contain little remaining volatility structure.

---

## 13. Diagnostics After Fitting

Fitting a GARCH model is not the end of the analysis.

A fitted model should be checked.

### 13.1 Standardized residuals

The standardized residuals are

```math
z_t
=
\frac{\varepsilon_t}{\sigma_t}.
```

They should fluctuate around zero and should not display obvious volatility clustering.

---

### 13.2 Squared standardized residuals

If the GARCH model has captured the changing variance successfully, the squared standardized residuals should show little serial dependence.

Persistent structure in $z_t^2$ suggests that the variance model is incomplete.

---

### 13.3 Innovation distribution

A normal innovation distribution may underestimate extreme returns.

A Student-$t$ innovation distribution may provide a better fit when standardized residuals remain heavy-tailed.

---

### 13.4 Parameter persistence

The quantity

```math
\alpha+\beta
```

should be examined carefully.

A value close to one indicates persistent volatility.

A value greater than or equal to one raises questions about stationarity and long-run variance.

---

## 14. What We Will Do With HBL Data

The empirical analysis will use historical HBL prices obtained from the PSX REST API.

The workflow will be:

1. Fetch HBL historical closing prices.
2. Sort observations chronologically.
3. Compute daily log returns.
4. Express returns in percentage units for numerical stability.
5. Fit a GARCH(1,1) model.
6. Record the estimates of $\omega$, $\alpha$, and $\beta$.
7. calculate $\alpha+\beta$.
8. Extract conditional volatility.
9. Compare GARCH volatility with the constant volatility estimated under GBM.
10. Examine standardized residuals.
11. Save plots and a written interpretation.

The main empirical question is:

> Does a time-varying conditional volatility model describe HBL returns more convincingly than a constant-volatility GBM approximation?

---

## 15. Questions to Ask When Reading the Results

The numerical output should not be treated as a collection of coefficients to report mechanically.

The interpretation should address the following questions.

### Does volatility react to new shocks?

This is primarily reflected by $\alpha$.

A larger estimate indicates a stronger immediate response to market surprises.

### Is volatility persistent?

This is reflected by $\beta$ and by $\alpha+\beta$.

A high value means that turbulent periods tend to continue.

### Is the process mean-reverting?

For a standard stationary GARCH(1,1), we expect

```math
\alpha+\beta<1.
```

### Does the fitted conditional volatility resemble the rolling-volatility pattern?

The two measures need not be identical, but they should identify broadly similar calm and turbulent periods.

### Are standardized residuals approximately well behaved?

Remaining clusters or extreme tails may indicate that a normal GARCH(1,1) model is still too simple.

---

## 16. Common Misinterpretations

### “GARCH predicts whether the stock price will rise.”

Not directly.

GARCH primarily predicts conditional variance, not the direction of the return.

### “A high-volatility forecast means the stock will fall.”

Not necessarily.

High volatility means that a large movement is more likely. The movement may be positive or negative.

### “GARCH removes uncertainty.”

It does not.

It models the changing scale of uncertainty.

### “The fitted volatility is the true volatility.”

Volatility is latent. The fitted conditional volatility is a model-based estimate.

### “GARCH is a continuous-time stochastic differential equation.”

Standard GARCH is a discrete-time model.

Its role here is to prepare the conceptual ground for continuous-time stochastic volatility models.

---

## 17. Main Takeaway

The central GARCH(1,1) equation is

```math
\sigma_t^2
=
\omega
+
\alpha \varepsilon_{t-1}^2
+
\beta \sigma_{t-1}^2.
```

Its interpretation is simple but powerful:

> Today’s uncertainty depends on a long-run baseline, yesterday’s surprise, and yesterday’s uncertainty.

This structure allows the model to reproduce volatility clustering and persistent periods of market turbulence.

The progression from GBM to GARCH is therefore not merely a change of technique. It reflects a change in what the data has taught us:

```text
GBM assumes one constant volatility level.

The PSX data shows that volatility changes through time.

GARCH gives that changing volatility a precise statistical structure.
```

The next step is to fit a GARCH(1,1) model to HBL returns and examine whether the estimated conditional volatility explains the changing risk visible in the historical data.