# Stochastic Volatility SDEs: Study Notes

## 1. Why Move Beyond GBM and GARCH?

We began with geometric Brownian motion:

```math
dS_t
=
\mu S_t\,dt
+
\sigma S_t\,dW_t.
```

In GBM, volatility is constant. The parameter $\sigma$ is one fixed number.

Our HBL analysis showed that this is too simple. Rolling volatility changed substantially through time.

We then studied GARCH models. GARCH allowed volatility to change in discrete time:

```math
r_t
=
\mu
+
\sigma_t z_t,
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

GARCH taught us an important empirical lesson:

> Volatility is dynamic.

Stochastic volatility models take the next step.

They model volatility itself as a continuous-time stochastic process.

---

## 2. The Main Idea

In GBM, the stock price follows one SDE:

```math
dS_t
=
\mu S_t\,dt
+
\sigma S_t\,dW_t.
```

In a stochastic volatility model, the stock price still follows an SDE, but volatility is no longer fixed.

Instead, variance follows its own SDE.

A general stochastic volatility structure is:

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
\text{drift of variance}\,dt
+
\text{volatility of variance}\,dW_t^{(2)}.
```

Here:

- $S_t$ is the stock price;
- $v_t$ is the instantaneous variance;
- $\sqrt{v_t}$ is the instantaneous volatility;
- $W_t^{(1)}$ drives stock-price randomness;
- $W_t^{(2)}$ drives volatility randomness.

This is the key conceptual change:

```text
GBM:
volatility is a constant parameter

Stochastic volatility:
volatility is itself random
```

---

## 3. The Heston Model

The most famous stochastic volatility model is the Heston model.

It is written as:

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

This is a two-dimensional stochastic differential equation system.

One equation describes the stock price.

The other equation describes the variance.

---

## 4. Meaning of the Heston Parameters

### The stock-price equation

```math
dS_t
=
\mu S_t\,dt
+
\sqrt{v_t}S_t\,dW_t^{(1)}.
```

The parameter $\mu$ is the drift of the stock price.

The term $\sqrt{v_t}$ is the instantaneous volatility.

Unlike GBM, this volatility changes through time.

---

### The variance equation

```math
dv_t
=
\kappa(\theta-v_t)\,dt
+
\xi\sqrt{v_t}\,dW_t^{(2)}.
```

The parameter $\theta$ is the long-run variance level.

The parameter $\kappa$ is the speed of mean reversion.

The parameter $\xi$ is the volatility of volatility.

This means:

- if $v_t$ is above $\theta$, the drift pulls it downward;
- if $v_t$ is below $\theta$, the drift pulls it upward;
- the random term makes variance fluctuate unpredictably.

---

## 5. Mean Reversion in Variance

The term

```math
\kappa(\theta-v_t)
```

is the mean-reverting force.

If $v_t > \theta$, then

```math
\theta-v_t < 0.
```

So the drift of variance is negative.

This pulls variance downward.

If $v_t < \theta$, then

```math
\theta-v_t > 0.
```

So the drift of variance is positive.

This pulls variance upward.

Therefore, $v_t$ tends to move around the long-run level $\theta$.

This is similar in spirit to what we saw in GARCH:

```text
volatility changes,
but it does not wander completely without structure.
```

---

## 6. Volatility of Volatility

The term

```math
\xi\sqrt{v_t}\,dW_t^{(2)}
```

makes variance random.

The parameter $\xi$ controls how violently variance itself moves.

If $\xi$ is small, volatility changes smoothly.

If $\xi$ is large, volatility can spike sharply.

This is why $\xi$ is called the volatility of volatility.

---

## 7. Correlation Between Price and Volatility Shocks

In many stochastic volatility models, the two Brownian motions may be correlated:

```math
dW_t^{(1)}dW_t^{(2)}
=
\rho\,dt.
```

The parameter $\rho$ measures the relationship between price shocks and volatility shocks.

In equity markets, $\rho$ is often negative.

A negative $\rho$ means that when prices fall, volatility tends to rise.

This is connected to the leverage effect.

For our first simulation, we can start with $\rho=0$ to keep the model simple. Later we can add correlation.

---

## 8. Why Stochastic Volatility Is More Realistic Than GBM

GBM assumes:

```text
constant volatility
normal log-return shocks
no volatility clustering
```

Our HBL data showed that volatility changes over time and shocks are heavy-tailed.

Stochastic volatility models address one of these weaknesses directly:

```text
volatility changes because variance follows its own stochastic process.
```

This is more realistic than assuming a fixed $\sigma$.

---

## 9. Relationship With GARCH

GARCH is discrete time:

```math
\sigma_t^2
=
\omega
+
\alpha \varepsilon_{t-1}^2
+
\beta \sigma_{t-1}^2.
```

Heston is continuous time:

```math
dv_t
=
\kappa(\theta-v_t)\,dt
+
\xi\sqrt{v_t}\,dW_t^{(2)}.
```

Both models express the same broad idea:

> Volatility is dynamic.

The difference is the mathematical framework.

| Feature | GARCH | Stochastic volatility |
|---|---|---|
| Time | Discrete | Continuous |
| Main volatility object | Conditional variance $\sigma_t^2$ | Instantaneous variance $v_t$ |
| Randomness in volatility | Indirect through shocks | Direct through a Brownian motion |
| Common use | Volatility forecasting | Option pricing, SDE modelling, simulation |
| Natural next step after GBM? | Yes | Yes, after GARCH |

GARCH helped us discover that volatility is not constant.

Stochastic volatility gives that idea a continuous-time SDE form.

---

## 10. What We Can Do With PSX Data

With only historical closing prices, we should be careful.

A full professional calibration of the Heston model often uses option prices, because option prices contain information about expected future volatility.

However, we can still use PSX data for learning.

We can:

1. estimate a GBM volatility benchmark;
2. estimate a GARCH volatility series;
3. use those estimates to choose reasonable Heston-style parameters;
4. simulate stochastic volatility paths;
5. compare stochastic volatility simulations with GBM simulations;
6. study how random variance changes the behavior of stock-price paths.

So our first goal is not perfect calibration.

Our first goal is understanding.

---

## 11. First Simulation Goal

The first stochastic volatility script should simulate:

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

We will simulate many paths for $S_t$ and $v_t$.

This will show:

- stock prices under stochastic volatility;
- variance paths;
- volatility spikes;
- how stochastic volatility differs from GBM.

---

## 12. Numerical Simulation

To simulate the Heston model, we use a discrete approximation.

For a small time step $\Delta t$:

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

For variance:

```math
v_{t+\Delta t}
\approx
v_t
+
\kappa(\theta-v_t)\Delta t
+
\xi\sqrt{v_t}\sqrt{\Delta t}Z_t^{(2)}.
```

To prevent variance from becoming negative in a basic simulation, we can use:

```math
v_t^+
=
\max(v_t,0).
```

This is a practical numerical safeguard.

---

## 13. What We Expect to See

Compared with GBM, stochastic volatility simulations should show:

- periods of low volatility;
- periods of high volatility;
- volatility spikes;
- price paths whose randomness changes through time;
- more realistic clustering of large and small movements.

This is the main visual advantage over GBM.

GBM paths have one fixed noise scale.

Stochastic volatility paths have a changing noise scale.

---

## 14. Learning Objective

The objective is not to claim that the Heston model is the final correct model for HBL.

The objective is to understand the modeling progression:

```text
GBM:
one SDE for price, constant volatility

GARCH:
discrete-time volatility dynamics

Stochastic volatility:
one SDE for price and one SDE for variance
```

This is the natural bridge from applied financial data analysis back into stochastic differential equations.

---

## 15. Main Takeaway

The key idea of stochastic volatility is:

> Volatility is not just an unknown constant. It is a state variable with its own dynamics.

The Heston model expresses this idea through the system:

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

This is the next natural model after GBM and GARCH.

It keeps the continuous-time SDE structure of GBM, but it allows volatility to change randomly through time.