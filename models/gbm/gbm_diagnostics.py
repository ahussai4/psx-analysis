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


def estimate_gbm_parameters(df: pd.DataFrame):
    df = df.copy()

    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    df = df.dropna(subset=["log_return"])

    daily_mean = df["log_return"].mean()
    daily_volatility = df["log_return"].std()

    trading_days = 252

    sigma_annual = daily_volatility * np.sqrt(trading_days)
    mu_annual = daily_mean * trading_days + 0.5 * sigma_annual**2

    return df, daily_mean, daily_volatility, mu_annual, sigma_annual


def extract_standardized_shocks(
    df: pd.DataFrame,
    mu: float,
    sigma: float,
) -> pd.DataFrame:
    df = df.copy()

    trading_days = 252
    dt = 1 / trading_days

    gbm_daily_log_drift = (mu - 0.5 * sigma**2) * dt
    gbm_daily_log_volatility = sigma * np.sqrt(dt)

    df["standardized_shock"] = (
        df["log_return"] - gbm_daily_log_drift
    ) / gbm_daily_log_volatility

    return df


def summarize_shocks(df: pd.DataFrame):
    z = df["standardized_shock"]

    print("Standardized shock diagnostics:")
    print(f"Mean of Z: {z.mean():.4f}")
    print(f"Standard deviation of Z: {z.std():.4f}")
    print(f"Minimum Z: {z.min():.4f}")
    print(f"Maximum Z: {z.max():.4f}")
    print()
    print("Selected quantiles:")
    print(f"1% quantile: {z.quantile(0.01):.4f}")
    print(f"5% quantile: {z.quantile(0.05):.4f}")
    print(f"50% quantile: {z.quantile(0.50):.4f}")
    print(f"95% quantile: {z.quantile(0.95):.4f}")
    print(f"99% quantile: {z.quantile(0.99):.4f}")
    print()
    print("Reference values for standard normal:")
    print("Mean should be close to 0")
    print("Standard deviation should be close to 1")
    print("5% quantile should be close to -1.645")
    print("95% quantile should be close to 1.645")
    print("1% quantile should be close to -2.326")
    print("99% quantile should be close to 2.326")


def save_plots(df: pd.DataFrame, symbol: str):
    z = df["standardized_shock"]

    standardized_histogram_path = OUTPUT_DIR / "standardized_shocks_histogram.png"
    shocks_over_time_path = OUTPUT_DIR / "standardized_shocks_over_time.png"
    log_returns_path = OUTPUT_DIR / "log_returns_over_time.png"
    rolling_volatility_path = OUTPUT_DIR / "rolling_volatility_60d.png"

    plt.figure(figsize=(10, 6))
    plt.hist(z, bins=60, density=True, alpha=0.7)

    x = np.linspace(-5, 5, 500)
    normal_density = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x**2)
    plt.plot(x, normal_density, linewidth=2)

    plt.title(f"Standardized Shocks for {symbol}: Histogram vs Standard Normal")
    plt.xlabel("Standardized shock")
    plt.ylabel("Density")
    plt.grid(True)
    plt.savefig(standardized_histogram_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(df["date"], df["standardized_shock"])
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.axhline(2, linestyle="--", linewidth=1)
    plt.axhline(-2, linestyle="--", linewidth=1)
    plt.title(f"Standardized Shocks Over Time for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Standardized shock")
    plt.grid(True)
    plt.savefig(shocks_over_time_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(df["date"], df["log_return"])
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.title(f"Daily Log Returns Over Time for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Daily log return")
    plt.grid(True)
    plt.savefig(log_returns_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(df["date"], df["log_return"].rolling(window=60).std())
    plt.title(f"60-Day Rolling Volatility for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("60-day rolling standard deviation of log returns")
    plt.grid(True)
    plt.savefig(rolling_volatility_path, dpi=150)
    plt.close()

    return [
        standardized_histogram_path,
        shocks_over_time_path,
        log_returns_path,
        rolling_volatility_path,
    ]


def main():
    symbol = "HBL"

    df = fetch_stock_data(symbol)
    df, daily_mean, daily_volatility, mu, sigma = estimate_gbm_parameters(df)
    df = extract_standardized_shocks(df, mu=mu, sigma=sigma)

    print(f"Symbol: {symbol}")
    print(f"Number of observations: {len(df)}")
    print(f"First date: {df['date'].min().date()}")
    print(f"Last date: {df['date'].max().date()}")
    print()
    print("Estimated GBM parameters:")
    print(f"Daily mean log return: {daily_mean:.6f}")
    print(f"Daily volatility: {daily_volatility:.6f}")
    print(f"Annual mu: {mu:.4f}")
    print(f"Annual sigma: {sigma:.4f}")
    print()

    summarize_shocks(df)

    saved_files = save_plots(df, symbol)

    print()
    print("Charts saved:")
    for file_path in saved_files:
        print(file_path)


if __name__ == "__main__":
    main()