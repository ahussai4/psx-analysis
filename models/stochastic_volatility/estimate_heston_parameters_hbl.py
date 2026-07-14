import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from arch import arch_model


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


API_URL = "https://psx-rest-api.onrender.com"


def fetch_stock_data(symbol: str) -> pd.DataFrame:
    url = f"{API_URL}/historical/{symbol}?order=asc"

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    data = response.json()["data"]

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    df = df.dropna(subset=["date", "close"])
    df = df.sort_values("date").reset_index(drop=True)

    return df


def compute_log_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df = df.dropna(subset=["log_return"]).reset_index(drop=True)

    return df


def fit_student_t_garch(df: pd.DataFrame):
    """
    Fit Student-t GARCH(1,1) to daily log returns.

    The arch package is usually more stable when returns are expressed
    in percentage units, so log returns are multiplied by 100.
    """

    returns_percent = df["log_return"] * 100

    model = arch_model(
        returns_percent,
        mean="Constant",
        vol="GARCH",
        p=1,
        q=1,
        dist="t",
        rescale=False,
    )

    result = model.fit(disp="off")

    return result


def add_variance_proxy(df: pd.DataFrame, garch_result) -> pd.DataFrame:
    """
    Convert GARCH conditional volatility into an annualized variance proxy.

    arch returns conditional volatility in percentage units because
    the input returns were multiplied by 100.

    daily volatility in decimal units:
        conditional_volatility / 100

    annualized variance proxy:
        daily_volatility^2 * 252
    """

    df = df.copy()

    df["garch_daily_vol_percent"] = garch_result.conditional_volatility
    df["garch_daily_vol_decimal"] = df["garch_daily_vol_percent"] / 100

    df["variance_proxy"] = df["garch_daily_vol_decimal"] ** 2 * 252

    return df


def estimate_heston_variance_parameters(df: pd.DataFrame):
    """
    Estimate kappa, theta, and xi from the variance proxy.

    We approximate the Heston variance equation:

        dv_t = kappa(theta - v_t) dt + xi sqrt(v_t) dW_t

    with the discrete AR(1)-style regression:

        v_{t+1} = a + b v_t + error_t

    Comparing terms gives:

        b = 1 - kappa dt
        a = kappa theta dt

    Therefore:

        kappa = (1 - b) / dt
        theta = a / (1 - b)

    The volatility-of-volatility parameter xi is estimated from:

        error_t ≈ xi sqrt(v_t) sqrt(dt) Z_t
    """

    trading_days = 252
    dt = 1 / trading_days

    variance = df["variance_proxy"].dropna().to_numpy()

    v_t = variance[:-1]
    v_next = variance[1:]

    X = np.column_stack([np.ones(len(v_t)), v_t])

    coefficients, _, _, _ = np.linalg.lstsq(X, v_next, rcond=None)

    a = coefficients[0]
    b = coefficients[1]

    kappa = (1 - b) / dt

    if abs(1 - b) < 1e-10:
        theta = np.nan
    else:
        theta = a / (1 - b)

    fitted_v_next = a + b * v_t
    residuals = v_next - fitted_v_next

    epsilon = 1e-12
    xi_squared_terms = residuals**2 / (np.maximum(v_t, epsilon) * dt)
    xi = np.sqrt(np.mean(xi_squared_terms))

    return {
        "a": a,
        "b": b,
        "kappa": kappa,
        "theta": theta,
        "xi": xi,
        "v_t": v_t,
        "v_next": v_next,
        "fitted_v_next": fitted_v_next,
        "variance_residuals": residuals,
    }


def estimate_mu_and_rho(df: pd.DataFrame, variance_estimates: dict):
    """
    Estimate annual drift mu and price-volatility shock correlation rho.

    For the stock-price equation:

        dS_t = mu S_t dt + sqrt(v_t) S_t dW_1(t)

    log returns approximately satisfy:

        r_t ≈ (mu - 0.5 v_t)dt + sqrt(v_t) sqrt(dt) Z_1,t

    We estimate:

        mu ≈ 252 * mean(log_return) + 0.5 * mean(v_t)

    Then we estimate price shocks Z_1,t and variance shocks Z_2,t.

    Finally:

        rho ≈ Corr(Z_1,t, Z_2,t)

    This is a historical proxy estimate, not a full Heston calibration.
    """

    trading_days = 252
    dt = 1 / trading_days

    variance = df["variance_proxy"].dropna().to_numpy()
    returns = df["log_return"].dropna().to_numpy()

    n = min(len(returns), len(variance))

    returns = returns[:n]
    variance = variance[:n]

    mu = returns.mean() * trading_days + 0.5 * variance.mean()

    v_t = variance_estimates["v_t"]
    residuals = variance_estimates["variance_residuals"]
    xi = variance_estimates["xi"]

    n_shocks = min(len(v_t), len(residuals), len(returns))

    v_for_shocks = v_t[:n_shocks]
    returns_for_shocks = returns[:n_shocks]
    residuals_for_shocks = residuals[:n_shocks]

    epsilon = 1e-12

    price_shocks = (
        returns_for_shocks - (mu - 0.5 * v_for_shocks) * dt
    ) / (np.sqrt(np.maximum(v_for_shocks, epsilon)) * np.sqrt(dt))

    variance_shocks = residuals_for_shocks / (
        xi * np.sqrt(np.maximum(v_for_shocks, epsilon)) * np.sqrt(dt)
    )

    valid = np.isfinite(price_shocks) & np.isfinite(variance_shocks)

    if valid.sum() < 2:
        rho = np.nan
    else:
        rho = np.corrcoef(price_shocks[valid], variance_shocks[valid])[0, 1]

    return {
        "mu": mu,
        "rho": rho,
        "price_shocks": price_shocks,
        "variance_shocks": variance_shocks,
    }


def summarize_results(
    symbol: str,
    df: pd.DataFrame,
    garch_result,
    variance_estimates: dict,
    shock_estimates: dict,
):
    latest_close = df["close"].iloc[-1]
    latest_variance = df["variance_proxy"].iloc[-1]
    latest_volatility = np.sqrt(latest_variance)

    long_run_volatility = np.sqrt(variance_estimates["theta"])
    initial_volatility = latest_volatility

    print(f"Symbol: {symbol}")
    print()
    print("Student-t GARCH model used to estimate variance proxy:")
    print(f"Log-likelihood: {garch_result.loglikelihood:.4f}")
    print(f"AIC: {garch_result.aic:.4f}")
    print(f"BIC: {garch_result.bic:.4f}")
    print()

    print("Estimated Heston-style parameters from historical variance proxy:")
    print(f"S0, latest close price: {latest_close:.4f}")
    print(f"mu, annual drift estimate: {shock_estimates['mu']:.6f}")
    print(f"v0, latest variance proxy: {latest_variance:.6f}")
    print(f"sqrt(v0), latest annual volatility: {initial_volatility:.6f}")
    print(f"theta, long-run variance estimate: {variance_estimates['theta']:.6f}")
    print(f"sqrt(theta), long-run annual volatility: {long_run_volatility:.6f}")
    print(f"kappa, speed of variance mean reversion: {variance_estimates['kappa']:.6f}")
    print(f"xi, volatility of volatility: {variance_estimates['xi']:.6f}")
    print(f"rho, price-volatility shock correlation: {shock_estimates['rho']:.6f}")
    print()

    print("AR(1) variance proxy regression:")
    print(f"a: {variance_estimates['a']:.8f}")
    print(f"b: {variance_estimates['b']:.8f}")
    print()

    print("Important interpretation:")
    print("These are historical proxy estimates, not a full Heston calibration.")
    print("The hidden variance process is approximated using Student-t GARCH conditional variance.")
    print("A full Heston calibration usually requires option-price data.")


def save_estimates(
    symbol: str,
    df: pd.DataFrame,
    garch_result,
    variance_estimates: dict,
    shock_estimates: dict,
):
    latest_close = df["close"].iloc[-1]
    latest_variance = df["variance_proxy"].iloc[-1]

    estimates = {
        "symbol": symbol,
        "S0": latest_close,
        "mu": shock_estimates["mu"],
        "v0": latest_variance,
        "theta": variance_estimates["theta"],
        "kappa": variance_estimates["kappa"],
        "xi": variance_estimates["xi"],
        "rho": shock_estimates["rho"],
        "garch_log_likelihood": garch_result.loglikelihood,
        "garch_aic": garch_result.aic,
        "garch_bic": garch_result.bic,
        "ar1_a": variance_estimates["a"],
        "ar1_b": variance_estimates["b"],
    }

    estimates_df = pd.DataFrame([estimates])

    output_path = OUTPUT_DIR / "heston_parameter_estimates_hbl.csv"
    estimates_df.to_csv(output_path, index=False)

    return output_path


def save_plots(
    df: pd.DataFrame,
    variance_estimates: dict,
    shock_estimates: dict,
    symbol: str,
):
    variance_proxy_path = OUTPUT_DIR / "heston_variance_proxy_from_garch.png"
    variance_regression_path = OUTPUT_DIR / "heston_variance_ar1_fit.png"
    shock_correlation_path = OUTPUT_DIR / "heston_price_vs_variance_shocks.png"

    plt.figure(figsize=(10, 6))
    plt.plot(df["date"], df["variance_proxy"])
    plt.axhline(
        variance_estimates["theta"],
        linestyle="--",
        linewidth=2,
        label="Estimated long-run variance theta",
    )
    plt.title(f"Heston Variance Proxy from Student-t GARCH for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Annualized variance proxy")
    plt.legend()
    plt.grid(True)
    plt.savefig(variance_proxy_path, dpi=150)
    plt.close()

    v_t = variance_estimates["v_t"]
    v_next = variance_estimates["v_next"]
    fitted_v_next = variance_estimates["fitted_v_next"]

    plt.figure(figsize=(10, 6))
    plt.scatter(v_t, v_next, alpha=0.5, label="Observed variance transition")

    sort_index = np.argsort(v_t)
    plt.plot(
        v_t[sort_index],
        fitted_v_next[sort_index],
        linewidth=2,
        label="AR(1) fitted transition",
    )

    plt.title(f"Variance Proxy AR(1) Fit for {symbol}")
    plt.xlabel("v_t")
    plt.ylabel("v_{t+1}")
    plt.legend()
    plt.grid(True)
    plt.savefig(variance_regression_path, dpi=150)
    plt.close()

    price_shocks = shock_estimates["price_shocks"]
    variance_shocks = shock_estimates["variance_shocks"]

    n = min(len(price_shocks), len(variance_shocks))

    plt.figure(figsize=(10, 6))
    plt.scatter(price_shocks[:n], variance_shocks[:n], alpha=0.5)
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.axvline(0, linestyle="--", linewidth=1)
    plt.title(f"Estimated Price Shocks vs Variance Shocks for {symbol}")
    plt.xlabel("Estimated price shock")
    plt.ylabel("Estimated variance shock")
    plt.grid(True)
    plt.savefig(shock_correlation_path, dpi=150)
    plt.close()

    return [
        variance_proxy_path,
        variance_regression_path,
        shock_correlation_path,
    ]


def main():
    symbol = "HBL"

    df = fetch_stock_data(symbol)
    df = compute_log_returns(df)

    garch_result = fit_student_t_garch(df)
    df = add_variance_proxy(df, garch_result)

    variance_estimates = estimate_heston_variance_parameters(df)
    shock_estimates = estimate_mu_and_rho(df, variance_estimates)

    summarize_results(
        symbol=symbol,
        df=df,
        garch_result=garch_result,
        variance_estimates=variance_estimates,
        shock_estimates=shock_estimates,
    )

    estimates_path = save_estimates(
        symbol=symbol,
        df=df,
        garch_result=garch_result,
        variance_estimates=variance_estimates,
        shock_estimates=shock_estimates,
    )

    plot_paths = save_plots(
        df=df,
        variance_estimates=variance_estimates,
        shock_estimates=shock_estimates,
        symbol=symbol,
    )

    print()
    print("Files saved:")
    print(estimates_path)
    for path in plot_paths:
        print(path)


if __name__ == "__main__":
    main()