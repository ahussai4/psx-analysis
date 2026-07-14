# Heston-Style Stochastic Volatility Simulation for HBL

## 1. Purpose of This Simulation

The purpose of this simulation is to understand stochastic volatility SDEs using real PSX data.

Earlier models showed the following progression:

```text
GBM:
constant volatility

GARCH:
time-varying volatility in discrete time

Student-t GARCH:
time-varying volatility with heavy-tailed shocks
```

The next natural step is a continuous-time stochastic volatility model.

The goal here is not to produce a full professional Heston calibration. Instead, the goal is to use HBL data to build a data-informed stochastic volatility simulation and understand how it differs from GBM.

---

## 2. Model Used

The simulation uses a Heston-style stochastic volatility system:

```math
dS_t
=
\mu S_t\,dt
+
\sqrt{v_t}S_t\,dW_t^{(1)}.
```

The variance process is modeled as

```math
dv_t
=
\kappa(\theta-v_t)\,dt
+
\xi\sqrt{v_t}\,dW_t^{(2)}.
```

Here:

- $S_t$ is the stock price;
- $v_t$ is the instantaneous variance;
- $\sqrt{v_t}$ is the instantaneous volatility;
- $\mu$ is the stock-price drift;
- $\theta$ is the long-run variance level;
- $\kappa$ is the speed of mean reversion;
- $\xi$ is the volatility of volatility;
- $W_t^{(1)}$ drives price shocks;
- $W_t^{(2)}$ drives volatility shocks.

---

## 3. Data-Informed Inputs

The inputs estimated from HBL historical data were:

```text
S0, latest close price: 298.0400
mu, annual drift estimate: 0.0861
GBM annual sigma estimate: 0.3173
v0, initial variance from recent volatility: 0.1005
theta, long-run variance estimate: 0.1007
```

The latest close price was used as the starting value for simulated price paths.

The annual drift estimate was obtained from historical log returns.

The long-run variance estimate was based on the historical GBM volatility estimate:

```math
\theta
\approx
\sigma_{\text{GBM}}^2.
```

Since

```text
GBM annual sigma estimate = 0.3173
```

the corresponding variance is approximately

```math
0.3173^2 \approx 0.1007.
```

The initial variance $v_0$ was estimated from recent 60-day volatility.

---

## 4. Chosen Simulation Parameters

The following Heston-style parameters were chosen for learning purposes:

```text
kappa = 2.0000
xi    = 0.5000
rho   = 0.0000
```

The parameter $\kappa=2$ means that variance is pulled back toward its long-run level at a moderate speed.

The parameter $\xi=0.5$ controls the randomness of variance itself. This allows volatility to fluctuate and occasionally spike.

The parameter $\rho=0$ means that price shocks and variance shocks are assumed uncorrelated in this first simulation.

This is a simplification. In many equity-market models, $\rho$ is often negative, reflecting the tendency for volatility to rise when prices fall.

---

## 5. Important Calibration Note

This is a data-informed simulation, not a full Heston calibration.

A full Heston calibration usually requires option-price data, because option prices contain information about expected future volatility and the market price of volatility risk.

With only historical closing prices, we can estimate useful historical quantities such as:

- current price;
- historical drift;
- historical volatility;
- recent volatility;
- approximate long-run variance.

However, parameters such as $\kappa$, $\xi$, and $\rho$ are difficult to estimate reliably from closing prices alone.

Therefore, this simulation should be interpreted as a learning experiment rather than a final empirical model.

---

## 6. Interpretation of Price Paths

The simulated price paths show possible future HBL price scenarios under stochastic volatility.

Unlike GBM, the randomness in the stock price does not have a fixed scale.

In GBM, the price model is

```math
dS_t
=
\mu S_t\,dt
+
\sigma S_t\,dW_t,
```

where $\sigma$ is constant.

In the Heston-style model, the price equation is

```math
dS_t
=
\mu S_t\,dt
+
\sqrt{v_t}S_t\,dW_t^{(1)}.
```

The volatility term $\sqrt{v_t}$ changes over time.

This means that some simulated paths become calm, while others become highly volatile. This behavior is closer to what was observed in the real HBL data.

---

## 7. Interpretation of Volatility Paths

The volatility-path plot is the most important output.

It shows that volatility is no longer a fixed parameter. It is now a state variable with its own stochastic dynamics.

Some volatility paths rise sharply. Others decline. Some remain near the long-run level.

This reflects the variance equation:

```math
dv_t
=
\kappa(\theta-v_t)\,dt
+
\xi\sqrt{v_t}\,dW_t^{(2)}.
```

The first term,

```math
\kappa(\theta-v_t)\,dt,
```

pulls variance toward the long-run level $\theta$.

The second term,

```math
\xi\sqrt{v_t}\,dW_t^{(2)},
```

adds random variation to variance itself.

This is the central idea of stochastic volatility:

```text
volatility changes randomly through time.
```

---

## 8. Comparison With GBM

The comparison plot shows Heston-style paths against GBM paths.

GBM paths have one fixed volatility level.

Heston-style paths have changing volatility because each path has its own variance process.

This is the essential difference:

```text
GBM:
one constant volatility parameter

Heston-style stochastic volatility:
a random volatility process
```

The Heston-style simulation can produce periods of low volatility and periods of high volatility within the same path.

GBM cannot do this because its volatility is fixed.

---

## 9. Numerical Simulation Note

The simulation used a discrete-time approximation to the continuous-time SDE.

For the stock price, the update was based on:

```math
S_{t+\Delta t}
\approx
S_t
\exp\left[
\left(\mu-\frac{1}{2}v_t\right)\Delta t
+
\sqrt{v_t}\sqrt{\Delta t}Z_t^{(1)}
\right].
```

For the variance process, the approximation was:

```math
v_{t+\Delta t}
\approx
v_t
+
\kappa(\theta-v_t)\Delta t
+
\xi\sqrt{v_t}\sqrt{\Delta t}Z_t^{(2)}.
```

A non-negativity correction was used so that variance does not become negative in the simulation.

This is acceptable for a first learning simulation, but more careful numerical schemes may be used in advanced Heston simulation.

---

## 10. What This Simulation Teaches

This simulation shows the conceptual progression from GBM to stochastic volatility.

GBM has one source of randomness:

```text
Brownian motion driving price
```

The Heston-style model has two sources of randomness:

```text
one Brownian motion driving price
one Brownian motion driving variance
```

This makes the model more flexible.

It can produce:

- changing volatility;
- volatility spikes;
- calm periods;
- turbulent periods;
- price paths whose uncertainty changes through time.

These features are more consistent with what was observed in the HBL data than constant-volatility GBM.

---

## 11. Relation to GARCH

The GARCH analysis showed that HBL volatility is dynamic in discrete time.

The Heston-style simulation expresses a similar idea in continuous time.

The relationship is:

```text
GARCH:
conditional variance changes through a discrete recursion

Heston-style stochastic volatility:
instantaneous variance changes through an SDE
```

Thus, GARCH helped motivate the stochastic volatility SDE.

The data first taught us that volatility changes. The Heston-style model then provides a continuous-time mathematical structure for that idea.

---

## 12. Limitations

This simulation has several important limitations.

First, it is not a full calibration.

Second, the parameters $\kappa$, $\xi$, and $\rho$ were chosen for learning purposes rather than statistically estimated.

Third, the simulation used $\rho=0$, although equity models often use negative correlation between price and volatility shocks.

Fourth, the basic variance simulation used a simple non-negativity correction.

Fifth, the model does not include jumps, heavy-tailed innovations, or regime changes.

Therefore, the simulation should be used for understanding stochastic volatility, not for making precise financial forecasts.

---

## 13. Main Conclusion

The Heston-style simulation demonstrates why stochastic volatility models are a natural step beyond GBM.

The HBL data showed that volatility is not constant.

GBM cannot capture this because it uses a fixed volatility parameter.

GARCH captured changing volatility in discrete time.

The Heston-style model captures changing volatility in continuous time by giving variance its own stochastic differential equation.

The main lesson is:

```text
Volatility is not merely a parameter.

Volatility can be modeled as a stochastic state variable.
```

This is the central idea of stochastic volatility SDEs.

---

## 14. Learning Takeaway

The full learning progression is now:

```text
GBM:
first continuous-time SDE model for stock prices

GBM diagnostics:
real data violates constant-volatility assumptions

GARCH:
discrete-time model of changing volatility

Student-t GARCH:
changing volatility plus heavy-tailed shocks

Heston-style stochastic volatility:
continuous-time SDE system with random variance
```

This simulation connects real PSX data back to the theory of stochastic differential equations.

It shows that stochastic calculus is not only a formal mathematical language. It is also a framework for building and testing increasingly realistic models of uncertainty.