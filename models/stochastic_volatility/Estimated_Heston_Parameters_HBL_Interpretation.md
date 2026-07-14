# Estimated Heston-Style Parameters for HBL

## 1. Purpose

This note documents the estimated Heston-style parameters for HBL and interprets the resulting simulations.

The goal is to connect the earlier empirical volatility work with a continuous-time stochastic volatility SDE.

The model is Heston-style:

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

Here, the stock price is driven by one Brownian motion, while the variance process is driven by another Brownian motion.

The key modeling idea is:

```text
volatility is no longer a fixed parameter;
it is a stochastic state variable.
```

---

## 2. Important Methodological Warning

These are not full option-implied Heston calibration estimates.

They are historical proxy estimates.

The hidden variance process \(v_t\) is not directly observed. Therefore, we approximated it using the conditional variance estimated from a Student-t GARCH(1,1) model.

So the correct description is:

```text
Heston-style parameters estimated from a Student-t GARCH variance proxy.
```

The incorrect description would be:

```text
fully calibrated Heston model.
```

That distinction is important.

A full Heston calibration usually requires option-price data, because option prices contain information about market expectations of future volatility, skewness, and tail risk.

---

## 3. Estimated Parameters

The estimated values were:

```text
S0     = 298.0400
mu     = 0.095046
v0     = 0.083360
theta  = 0.118732
kappa  = 60.328807
xi     = 3.241896
rho    = 0.220219
```

The estimated model is therefore approximately:

```math
dS_t
=
0.095046 S_t\,dt
+
\sqrt{v_t}S_t\,dW_t^{(1)},
```

```math
dv_t
=
60.328807(0.118732-v_t)\,dt
+
3.241896\sqrt{v_t}\,dW_t^{(2)}.
```

with

```math
dW_t^{(1)}dW_t^{(2)}
=
0.220219\,dt.
```

---

## 4. Interpretation of \(S_0\)

The value

```text
S0 = 298.0400
```

is the latest observed HBL closing price.

All simulated price paths begin from this value.

---

## 5. Interpretation of \(\mu\)

The estimated annual drift is

```text
mu = 0.095046
```

This corresponds to approximately 9.5 percent annual drift.

This does not mean that HBL will earn 9.5 percent in the future.

It simply means that, based on the historical return sample and the variance proxy adjustment, the estimated drift parameter in the simulation is about 9.5 percent per year.

In stochastic price modeling, drift is usually much harder to estimate reliably than volatility.

Therefore, the volatility parameters are more important for this analysis than the drift estimate.

---

## 6. Interpretation of \(v_0\)

The estimated initial variance is

```text
v0 = 0.083360
```

The corresponding initial annual volatility is:

```math
\sqrt{v_0}
=
\sqrt{0.083360}
\approx
0.288722.
```

So the initial annualized volatility is approximately:

```text
28.87 percent.
```

This means that the simulation starts from a volatility level close to 29 percent.

---

## 7. Interpretation of \(\theta\)

The estimated long-run variance is

```text
theta = 0.118732
```

The corresponding long-run annual volatility is:

```math
\sqrt{\theta}
=
\sqrt{0.118732}
\approx
0.344576.
```

So the estimated long-run annualized volatility is approximately:

```text
34.46 percent.
```

This means the model estimates that HBL's long-run volatility level is higher than the most recent volatility level.

In simple terms:

```text
latest estimated volatility ≈ 28.87 percent
long-run estimated volatility ≈ 34.46 percent
```

---

## 8. Interpretation of \(\kappa\)

The estimated mean-reversion speed is

```text
kappa = 60.328807
```

This is very large.

In the Heston variance equation,

```math
dv_t
=
\kappa(\theta-v_t)\,dt
+
\xi\sqrt{v_t}\,dW_t^{(2)},
```

\(\kappa\) controls how quickly variance is pulled back toward \(\theta\).

A large \(\kappa\) means variance mean-reverts very quickly.

The approximate half-life of a variance shock is:

```math
\frac{\log(2)}{\kappa}
=
\frac{\log(2)}{60.328807}
\approx
0.01149
```

years.

In trading days, this is approximately:

```math
0.01149 \times 252
\approx
2.9
```

trading days.

So this estimate suggests extremely fast variance mean reversion.

This should be interpreted cautiously. It is probably an artifact of estimating Heston-style dynamics from a GARCH-implied variance proxy rather than from option prices.

---

## 9. Interpretation of \(\xi\)

The estimated volatility of volatility is

```text
xi = 3.241896
```

This is also very large.

The parameter \(\xi\) controls how strongly the variance process itself fluctuates.

A large \(\xi\) means variance can move sharply from one day to the next.

This explains why the estimated Heston volatility-path plot looks extremely jagged and sometimes spikes above 100 percent annualized volatility.

That behavior is not necessarily a coding error.

It is a consequence of combining:

```text
large kappa
large xi
Euler simulation
non-negativity truncation
historical GARCH variance proxy estimation
```

The result is a very aggressive variance process.

---

## 10. Interpretation of \(\rho\)

The estimated correlation between price shocks and variance shocks is

```text
rho = 0.220219
```

This is mildly positive.

In many equity-market models, \(\rho\) is often negative, because falling prices are often associated with rising volatility.

Here, the estimate is positive.

This should not be over-interpreted.

The reason is that variance shocks are estimated from a GARCH variance proxy. GARCH variance reacts strongly to large squared returns, whether the return is positive or negative.

Therefore, the proxy-based variance shock may reflect the size of returns more than the direction of returns.

This is also visible in the price-shock versus variance-shock plot, where the pattern is not simply linear. The scatter has a curved shape: large positive and large negative price shocks both tend to be associated with large variance shocks.

This means a single linear correlation parameter \(\rho\) only partially summarizes the relationship.

---

## 11. AR(1) Variance Proxy Regression

The variance proxy was approximated using an AR(1)-style regression:

```math
v_{t+1}
=
a
+
b v_t
+
e_t.
```

The estimated values were:

```text
a = 0.02842453
b = 0.76059997
```

Comparing this with the discretized Heston variance equation gives:

```math
\kappa
=
\frac{1-b}{\Delta t},
```

where

```math
\Delta t = \frac{1}{252}.
```

Thus:

```math
\kappa
=
\frac{1-0.76059997}{1/252}
\approx
60.328807.
```

The long-run variance estimate is:

```math
\theta
=
\frac{a}{1-b}
=
\frac{0.02842453}{1-0.76059997}
\approx
0.118732.
```

The fitted AR(1) line captures the average direction of variance transitions, but the scatter is wide. This shows that the variance proxy is noisy.

So the AR(1) regression is useful for learning, but it is not a perfect description of the variance process.

---

## 12. Interpretation of the Estimated Volatility Paths

The estimated volatility paths are very jagged.

Many paths move rapidly between low volatility and very high volatility.

Some paths hit or approach zero because the Euler simulation uses a non-negativity correction:

```math
v_t^+
=
\max(v_t,0).
```

This correction prevents variance from becoming negative, but it can create artificial behavior near zero.

The jaggedness of the plot tells us something important:

```text
The estimated kappa and xi are too aggressive to be treated as clean Heston calibration parameters.
```

The plot is still valuable because it teaches us that proxy-based historical estimation can produce unstable stochastic-volatility simulations.

---

## 13. Interpretation of the Estimated Price Paths

The estimated Heston-style price paths show a wider range of possible outcomes than the earlier manually chosen stochastic-volatility simulation.

This is expected because the estimated volatility-of-volatility parameter is large.

When variance spikes, the stock price paths become more turbulent.

The price paths therefore reflect the dynamic variance process:

```math
dS_t
=
\mu S_t\,dt
+
\sqrt{v_t}S_t\,dW_t^{(1)}.
```

The uncertainty in price is no longer controlled by one fixed volatility number. It changes path by path and day by day.

---

## 14. Comparison With GBM

The estimated Heston-style model differs from GBM in a fundamental way.

GBM uses:

```math
dS_t
=
\mu S_t\,dt
+
\sigma S_t\,dW_t.
```

Here, \(\sigma\) is constant.

The Heston-style model uses:

```math
dS_t
=
\mu S_t\,dt
+
\sqrt{v_t}S_t\,dW_t^{(1)}.
```

Here, \(v_t\) changes randomly through time.

So GBM has one fixed volatility level, while the Heston-style model has a stochastic volatility process.

The comparison plot shows this difference clearly. The Heston-style paths can become calm or turbulent depending on their variance path.

---

## 15. Interpretation of the Price-Shock and Variance-Shock Plot

The price-shock versus variance-shock scatter plot is very important.

It does not show a simple straight-line relationship.

Instead, it has a curved shape.

This makes sense because the GARCH variance proxy is driven by the size of return shocks. Large positive returns and large negative returns can both increase the estimated variance.

Therefore, the estimated variance shock is related to return magnitude, not only return direction.

This is why the estimated \(\rho\) should be treated cautiously.

The Heston model summarizes dependence between price and variance shocks using a single correlation parameter. But the GARCH-based proxy relationship appears more nonlinear.

---

## 16. Main Empirical Lessons

The estimated Heston-style parameters teach four main lessons.

First, HBL volatility is clearly not constant.

Second, the long-run volatility estimate is around 34.46 percent, while the latest volatility estimate is around 28.87 percent.

Third, the proxy-based estimates imply very fast variance mean reversion and very high volatility-of-volatility.

Fourth, estimating Heston-style parameters from historical GARCH variance proxies is possible, but the results are rough and must be interpreted with care.

---

## 17. Limitations

This analysis has several limitations.

First, the variance process is not observed directly.

Second, the variance proxy comes from a fitted Student-t GARCH model.

Third, the estimated parameters are historical, not option-implied.

Fourth, the Euler simulation with truncation is simple and can behave poorly when \(\xi\) is large.

Fifth, the estimated \(\rho\) does not fully capture the nonlinear relationship between price shocks and variance shocks.

Sixth, the model does not include jumps, regime changes, liquidity effects, or market microstructure effects.

Therefore, this should be interpreted as a learning and research exercise, not as a final trading or pricing model.

---

## 18. Final Conclusion

The estimated Heston-style simulation is a valuable next step after GBM and GARCH.

It shows how one can move from:

```text
constant volatility
```

to:

```text
discrete-time conditional volatility
```

to:

```text
continuous-time stochastic volatility.
```

However, the estimated parameters also show why full Heston calibration is difficult.

The proxy estimates produce very aggressive variance dynamics:

```text
kappa is very large
xi is very large
rho is only a rough linear summary
```

The correct conclusion is:

```text
The Heston-style framework is conceptually appropriate for modeling dynamic volatility,
but historical proxy estimation from GARCH variance should be treated cautiously.
```

This is an important research lesson.

The mathematics gives us a powerful model, but the data and estimation method determine whether the fitted model behaves reasonably.

---

## 19. Learning Takeaway

The main learning takeaway is:

```text
Stochastic volatility is not just a more complicated version of GBM.

It changes the nature of the model by making volatility itself random.
```

For HBL, the data supports the need for dynamic volatility models.

GBM was useful as a baseline.

GARCH showed that volatility changes over time.

Student-t GARCH showed that shocks are heavy-tailed.

The Heston-style model translated these ideas into a continuous-time SDE system.

