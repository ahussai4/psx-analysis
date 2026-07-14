import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path


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


def estimate_basic_parameters(df: pd.DataFrame):
    df = df.copy()

    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df = df.dropna(subset=["log_return"]).reset_index(drop=True)

    trading_days = 252

    daily_mean = df["log_return"].mean()
    daily_volatility = df["log_return"].std()

    annual_sigma = daily_volatility * np.sqrt(trading_days)
    annual_mu = daily_mean * trading_days + 0.5 * annual_sigma**2

    latest_close = df["close"].iloc[-1]

    recent_daily_volatility = df["log_return"].tail(60).std()
    recent_annual_sigma = recent_daily_volatility * np.sqrt(trading_days)

    long_run_variance = annual_sigma**2
    initial_variance = recent_annual_sigma**2

    return {
        "df": df,
        "S0": latest_close,
        "mu": annual_mu,
        "annual_sigma": annual_sigma,
        "v0": initial_variance,
        "theta": long_run_variance,
    }


def simulate_heston_paths(
    S0: float,
    v0: float,
    mu: float,
    theta: float,
    kappa: float,
    xi: float,
    rho: float,
    days: int = 252,
    n_paths: int = 20,
    seed: int = 42,
):
    """
    Simulate a Heston-style stochastic volatility model.

    Price equation:
        dS_t = mu S_t dt + sqrt(v_t) S_t dW_1(t)

    Variance equation:
        dv_t = kappa(theta - v_t)dt + xi sqrt(v_t)dW_2(t)

    This is a learning simulation, not a full professional calibration.
    """

    np.random.seed(seed)

    trading_days = 252
    dt = 1 / trading_days

    prices = np.zeros((days + 1, n_paths))
    variances = np.zeros((days + 1, n_paths))

    prices[0] = S0
    variances[0] = v0

    for t in range(1, days + 1):
        z1 = np.random.normal(size=n_paths)
        z_independent = np.random.normal(size=n_paths)

        z2 = rho * z1 + np.sqrt(1 - rho**2) * z_independent

        previous_variance = np.maximum(variances[t - 1], 0)

        variances[t] = (
            variances[t - 1]
            + kappa * (theta - previous_variance) * dt
            + xi * np.sqrt(previous_variance) * np.sqrt(dt) * z2
        )

        variance_for_price = np.maximum(previous_variance, 0)

        prices[t] = prices[t - 1] * np.exp(
            (mu - 0.5 * variance_for_price) * dt
            + np.sqrt(variance_for_price) * np.sqrt(dt) * z1
        )

        variances[t] = np.maximum(variances[t], 0)

    return prices, variances


def simulate_gbm_paths(
    S0: float,
    mu: float,
    sigma: float,
    days: int = 252,
    n_paths: int = 20,
    seed: int = 123,
):
    np.random.seed(seed)

    trading_days = 252
    dt = 1 / trading_days

    paths = np.zeros((days + 1, n_paths))
    paths[0] = S0

    for t in range(1, days + 1):
        z = np.random.normal(size=n_paths)
        paths[t] = paths[t - 1] * np.exp(
            (mu - 0.5 * sigma**2) * dt
            + sigma * np.sqrt(dt) * z
        )

    return paths


def print_summary(symbol: str, params: dict, kappa: float, xi: float, rho: float):
    print(f"Symbol: {symbol}")
    print()
    print("Data-informed inputs:")
    print(f"S0, latest close price: {params['S0']:.4f}")
    print(f"mu, annual drift estimate: {params['mu']:.4f}")
    print(f"GBM annual sigma estimate: {params['annual_sigma']:.4f}")
    print(f"v0, initial variance from recent volatility: {params['v0']:.4f}")
    print(f"theta, long-run variance estimate: {params['theta']:.4f}")
    print()
    print("Chosen Heston-style simulation parameters:")
    print(f"kappa, speed of variance mean reversion: {kappa:.4f}")
    print(f"xi, volatility of volatility: {xi:.4f}")
    print(f"rho, correlation between price and variance shocks: {rho:.4f}")
    print()
    print("Important note:")
    print("This is a data-informed Heston-style simulation, not a full Heston calibration.")
    print("Full Heston calibration usually requires option-price data.")


def save_plots(
    symbol: str,
    heston_prices: np.ndarray,
    heston_variances: np.ndarray,
    gbm_prices: np.ndarray,
):
    heston_price_path = OUTPUT_DIR / "heston_price_paths.png"
    heston_volatility_path = OUTPUT_DIR / "heston_volatility_paths.png"
    heston_vs_gbm_path = OUTPUT_DIR / "heston_vs_gbm_price_paths.png"

    heston_volatility = np.sqrt(heston_variances) * 100

    plt.figure(figsize=(10, 6))
    for i in range(heston_prices.shape[1]):
        plt.plot(heston_prices[:, i], alpha=0.7)

    plt.title(f"Heston-Style Stochastic Volatility Price Paths for {symbol}")
    plt.xlabel("Trading days into future")
    plt.ylabel("Simulated price")
    plt.grid(True)
    plt.savefig(heston_price_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    for i in range(heston_volatility.shape[1]):
        plt.plot(heston_volatility[:, i], alpha=0.7)

    plt.title(f"Simulated Stochastic Volatility Paths for {symbol}")
    plt.xlabel("Trading days into future")
    plt.ylabel("Annualized volatility (%)")
    plt.grid(True)
    plt.savefig(heston_volatility_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))

    for i in range(min(10, heston_prices.shape[1])):
        plt.plot(heston_prices[:, i], alpha=0.7)

    for i in range(min(10, gbm_prices.shape[1])):
        plt.plot(gbm_prices[:, i], linestyle="--", alpha=0.7)

    plt.title(f"Heston-Style Paths vs GBM Paths for {symbol}")
    plt.xlabel("Trading days into future")
    plt.ylabel("Simulated price")
    plt.grid(True)
    plt.savefig(heston_vs_gbm_path, dpi=150)
    plt.close()

    return [
        heston_price_path,
        heston_volatility_path,
        heston_vs_gbm_path,
    ]


def main():
    symbol = "HBL"

    df = fetch_stock_data(symbol)
    params = estimate_basic_parameters(df)

    kappa = 2.0
    xi = 0.50
    rho = 0.0

    days = 252
    n_paths = 20

    heston_prices, heston_variances = simulate_heston_paths(
        S0=params["S0"],
        v0=params["v0"],
        mu=params["mu"],
        theta=params["theta"],
        kappa=kappa,
        xi=xi,
        rho=rho,
        days=days,
        n_paths=n_paths,
    )

    gbm_prices = simulate_gbm_paths(
        S0=params["S0"],
        mu=params["mu"],
        sigma=params["annual_sigma"],
        days=days,
        n_paths=n_paths,
    )

    print_summary(
        symbol=symbol,
        params=params,
        kappa=kappa,
        xi=xi,
        rho=rho,
    )

    saved_files = save_plots(
        symbol=symbol,
        heston_prices=heston_prices,
        heston_variances=heston_variances,
        gbm_prices=gbm_prices,
    )

    print()
    print("Charts saved:")
    for file_path in saved_files:
        print(file_path)


if __name__ == "__main__":
    main()