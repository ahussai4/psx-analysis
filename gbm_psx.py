import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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


def simulate_gbm(
    S0: float,
    mu: float,
    sigma: float,
    days: int,
    n_paths: int = 20,
):
    trading_days = 252
    dt = 1 / trading_days

    paths = np.zeros((days + 1, n_paths))
    paths[0] = S0

    for t in range(1, days + 1):
        z = np.random.normal(size=n_paths)
        paths[t] = paths[t - 1] * np.exp(
            (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
        )

    return paths


def main():
    symbol = "HBL"

    df = fetch_stock_data(symbol)

    df, daily_mean, daily_volatility, mu, sigma = estimate_gbm_parameters(df)

    print(f"Symbol: {symbol}")
    print(f"Number of observations: {len(df)}")
    print(f"First date: {df['date'].min().date()}")
    print(f"Last date: {df['date'].max().date()}")
    print()
    print("Daily estimates:")
    print(f"Average daily log return: {daily_mean:.6f}")
    print(f"Daily volatility: {daily_volatility:.6f}")
    print()
    print("Annualized GBM parameters:")
    print(f"mu: {mu:.4f}")
    print(f"sigma: {sigma:.4f}")

    S0 = df["close"].iloc[-1]
    days = 252

    simulated_paths = simulate_gbm(
        S0=S0,
        mu=mu,
        sigma=sigma,
        days=days,
        n_paths=20,
    )

    plt.figure(figsize=(10, 6))
    for i in range(simulated_paths.shape[1]):
        plt.plot(simulated_paths[:, i], alpha=0.7)

    plt.title(f"GBM Simulated Future Paths for {symbol}")
    plt.xlabel("Trading days into future")
    plt.ylabel("Simulated price")
    plt.grid(True)
    plt.savefig("gbm_simulated_paths.png", dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(df["date"], df["close"])
    plt.title(f"Historical Closing Price for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Closing price")
    plt.grid(True)
    plt.savefig("historical_price.png", dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.hist(df["log_return"], bins=50)
    plt.title(f"Daily Log Returns for {symbol}")
    plt.xlabel("Daily log return")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.savefig("log_returns_histogram.png", dpi=150)
    plt.close()

    print()
    print("Charts saved:")
    print("gbm_simulated_paths.png")
    print("historical_price.png")
    print("log_returns_histogram.png")


if __name__ == "__main__":
    main()
