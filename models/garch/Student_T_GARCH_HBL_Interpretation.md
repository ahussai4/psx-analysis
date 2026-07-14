# Student-t GARCH(1,1) Analysis of HBL

## 1. Purpose

The purpose of this analysis is to compare two volatility models for HBL returns:

1. GARCH(1,1) with normal innovations;
2. GARCH(1,1) with Student-t innovations.

The earlier GARCH analysis showed that HBL volatility is time-varying, shock-sensitive, persistent, and mean-reverting. However, the standardized residuals still appeared more sharply peaked and heavy-tailed than a normal distribution.

This motivates the Student-t GARCH model.

The main question is:

> Does allowing heavy-tailed innovations improve the GARCH model for HBL returns?

---

## 2. Why Student-t Innovations?

The normal GARCH model assumes that standardized shocks are normally distributed:

```math
z_t \sim N(0,1).
```

This assumption is often too restrictive for financial returns.

Real financial returns commonly exhibit heavy tails. This means extreme positive and negative shocks occur more often than the normal distribution predicts.

A Student-t distribution is more flexible because it can assign more probability to extreme observations.

In the Student-t GARCH model, the return equation remains

```math
r_t = \mu + \sigma_t z_t,
```

but the innovation distribution becomes Student-t rather than normal.

The GARCH variance equation remains

```math
\sigma_t^2
=
\omega
+
\alpha \varepsilon_{t-1}^2
+
\beta \sigma_{t-1}^2.
```

Thus, the Student-t model changes the assumed distribution of shocks, not the basic volatility recursion.

---

## 3. Model Comparison Results

The estimated model comparison was:

| Model | Log-likelihood | AIC | BIC | Alpha + Beta | Nu |
|---|---:|---:|---:|---:|---:|
| Normal GARCH(1,1) | -5040.53 | 10089.05 | 10112.31 | 0.8612 | — |
| Student-t GARCH(1,1) | -4910.63 | 9831.26 | 9860.33 | 0.8926 | 3.8281 |

The Student-t model improves the fit substantially.

It has:

- higher log-likelihood;
- lower AIC;
- lower BIC.

The improvement is not marginal. It is large enough to conclude that the Student-t innovation assumption is more appropriate for HBL returns than the normal innovation assumption.

---

## 4. Interpreting the Student-t Parameters

The Student-t GARCH model produced approximately:

```text
mu:       -0.0876
omega:     0.7419
alpha[1]:  0.3320
beta[1]:   0.5606
alpha[1] + beta[1]: 0.8926
nu:        3.8281
```

The fitted variance equation is approximately

```math
\sigma_t^2
=
0.7419
+
0.3320\varepsilon_{t-1}^2
+
0.5606\sigma_{t-1}^2.
```

---

## 5. Shock Response

The estimate

```text
alpha[1] = 0.3320
```

is relatively large.

This means that HBL volatility reacts strongly to recent unexpected returns.

In practical terms:

> Large shocks to HBL returns quickly increase the model’s estimate of conditional volatility.

Compared with the normal GARCH model, the Student-t model attributes a larger role to recent shocks.

---

## 6. Volatility Persistence

The estimate

```text
beta[1] = 0.5606
```

shows that volatility is persistent.

This means that once volatility rises, it tends to remain elevated for some time.

The persistence measure is

```text
alpha[1] + beta[1] = 0.8926
```

Since this is below one, the fitted volatility process is mean-reverting in the standard GARCH sense.

However, it is close enough to one to indicate that volatility shocks decay slowly.

Thus, the Student-t GARCH model suggests that HBL volatility is:

```text
persistent but not permanent.
```

---

## 7. Interpreting the Nu Parameter

The Student-t model estimates

```text
nu = 3.8281
```

The parameter $\nu$ controls the thickness of the tails of the Student-t distribution.

A smaller value of $\nu$ means heavier tails.

The estimate $\nu = 3.8281$ is fairly low, which indicates that HBL returns have heavy-tailed shocks.

This is one of the most important findings of the Student-t GARCH analysis.

It means:

> Extreme return shocks occur more often than a normal-distribution model would suggest.

This supports what was already visible in the residual histograms.

---

## 8. Comparison With Normal GARCH

The normal GARCH model already improved on GBM by allowing volatility to change over time.

However, it still assumed normally distributed standardized shocks.

The Student-t GARCH model improves on normal GARCH by allowing the shocks to be heavy-tailed.

The results show that this matters for HBL.

The Student-t model has:

```text
Lower AIC
Lower BIC
Higher log-likelihood
Heavy-tail parameter nu around 3.83
```

Therefore, the Student-t model is the better specification among the two GARCH models considered.

---

## 9. Comparison With GBM

The GBM model assumes constant volatility:

```math
dS_t
=
\mu S_t\,dt
+
\sigma S_t\,dW_t.
```

This was useful as a first stochastic model, but it could not capture the changing volatility seen in the HBL data.

Normal GARCH improved the model by introducing time-varying volatility.

Student-t GARCH improved it further by allowing heavy-tailed shocks.

The progression is:

```text
GBM:
constant volatility and Brownian shocks

Normal GARCH:
time-varying volatility but normal shocks

Student-t GARCH:
time-varying volatility and heavy-tailed shocks
```

For HBL, the third model is the most realistic among these three.

---

## 10. Interpretation of the Volatility Plot

The plot

```text
normal_vs_student_t_garch_volatility.png
```

compares:

1. normal GARCH annualized volatility;
2. Student-t GARCH annualized volatility;
3. GBM constant annual volatility.

The GBM volatility is a flat benchmark.

The GARCH volatilities move through time, reflecting changing market risk.

The Student-t volatility curve follows a similar broad pattern to the normal GARCH curve, but it reacts differently around extreme observations because the innovation distribution is heavier-tailed.

The plot reinforces the main conclusion:

> HBL volatility is not constant, and models with time-varying volatility are more appropriate than GBM alone.

---

## 11. Interpretation of the Residual Plots

The Student-t standardized residual histogram still shows a sharp center and visible tail behavior.

This does not invalidate the Student-t GARCH model.

Instead, it confirms that HBL returns have strong non-normal features.

The Student-t model is better suited to this behavior than the normal model because it explicitly allows heavier tails.

The standardized residuals over time mostly fluctuate around zero, but some large residuals remain.

This means that Student-t GARCH captures important features of the data, but it is still not a perfect model.

---

## 12. Main Empirical Conclusion

The Student-t GARCH(1,1) model is clearly preferred to the normal GARCH(1,1) model for HBL returns.

The evidence is:

- substantially higher log-likelihood;
- substantially lower AIC;
- substantially lower BIC;
- estimated $\nu$ around 3.83, indicating heavy tails;
- persistent but mean-reverting volatility.

The main empirical conclusion is:

```text
HBL returns exhibit time-varying volatility and heavy-tailed shocks.
```

Therefore, among the models fitted so far, Student-t GARCH(1,1) gives the best description of HBL return volatility.

---

## 13. Connection to Stochastic Volatility

This analysis also prepares the ground for stochastic volatility models.

GBM treats volatility as constant.

GARCH treats volatility as time-varying in discrete time.

A stochastic volatility SDE treats volatility as a random process in continuous time.

For example, a stochastic volatility model may have the structure

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

The GARCH results motivate this move because they show that volatility should not be treated as a fixed constant.

The data itself suggests that volatility has dynamics.

---

## 14. Final Summary

The analysis has produced the following learning progression:

```text
GBM showed how to connect stock prices with an SDE.

GBM diagnostics showed that constant volatility and normal shocks are too simple.

Normal GARCH captured time-varying volatility.

Student-t GARCH captured time-varying volatility and heavy-tailed shocks.
```

For HBL, Student-t GARCH(1,1) is the best model fitted so far.

It suggests that volatility is dynamic, persistent, mean-reverting, and driven by heavy-tailed innovations.

This provides a strong empirical foundation for moving next toward stochastic volatility SDEs.