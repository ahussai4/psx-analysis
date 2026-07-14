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


def fit_garch_model(df: pd.DataFrame):
    """
    Fit a GARCH(1,1) model to daily log returns.

    The arch package works better numerically when returns are expressed
    in percentage units, so we multiply log returns by 100.
    """

    returns_percent = df["log_return"] * 100

    model = arch_model(
        returns_percent,
        mean="Constant",
        vol="GARCH",
        p=1,
        q=1,
        dist="normal",
        rescale=False,
    )

    result = model.fit(disp="off")

    return result


def add_garch_outputs_to_dataframe(
    df: pd.DataFrame,
    result,
) -> pd.DataFrame:
    df = df.copy()

    df["garch_conditional_volatility_daily_percent"] = result.conditional_volatility

    df["garch_conditional_volatility_annual_percent"] = (
        df["garch_conditional_volatility_daily_percent"] * np.sqrt(252)
    )

    df["standardized_residual"] = result.std_resid

    return df


def estimate_gbm_constant_volatility(df: pd.DataFrame) -> float:
    daily_volatility = df["log_return"].std()
    annual_volatility_percent = daily_volatility * np.sqrt(252) * 100

    return annual_volatility_percent


def print_summary(symbol: str, df: pd.DataFrame, result, gbm_sigma_percent: float):
    params = result.params

    mu = params.get("mu", np.nan)
    omega = params.get("omega", np.nan)
    alpha = params.get("alpha[1]", np.nan)
    beta = params.get("beta[1]", np.nan)
    persistence = alpha + beta

    latest_garch_vol = df["garch_conditional_volatility_annual_percent"].iloc[-1]
    average_garch_vol = df["garch_conditional_volatility_annual_percent"].mean()

    print(f"Symbol: {symbol}")
    print(f"Number of return observations: {len(df)}")
    print(f"First date: {df['date'].min().date()}")
    print(f"Last date: {df['date'].max().date()}")
    print()
    print("GARCH(1,1) parameter estimates:")
    print(f"mu: {mu:.6f}")
    print(f"omega: {omega:.6f}")
    print(f"alpha[1]: {alpha:.6f}")
    print(f"beta[1]: {beta:.6f}")
    print(f"alpha[1] + beta[1]: {persistence:.6f}")
    print()
    print("Volatility comparison:")
    print(f"GBM constant annual volatility: {gbm_sigma_percent:.2f}%")
    print(f"Average GARCH annual volatility: {average_garch_vol:.2f}%")
    print(f"Latest GARCH annual volatility: {latest_garch_vol:.2f}%")
    print()
    print("Interpretation guide:")
    print("alpha measures the immediate reaction of volatility to shocks.")
    print("beta measures volatility persistence.")
    print("alpha + beta close to 1 means volatility shocks decay slowly.")
    print()
    print("Model summary:")
    print(result.summary())


def save_plots(df: pd.DataFrame, symbol: str, gbm_sigma_percent: float):
    garch_vol_path = OUTPUT_DIR / "garch_vs_gbm_volatility.png"
    returns_path = OUTPUT_DIR / "garch_log_returns.png"
    standardized_residuals_path = OUTPUT_DIR / "garch_standardized_residuals.png"
    standardized_residuals_hist_path = OUTPUT_DIR / "garch_standardized_residuals_histogram.png"

    plt.figure(figsize=(10, 6))
    plt.plot(
        df["date"],
        df["garch_conditional_volatility_annual_percent"],
        label="GARCH annualized conditional volatility",
    )
    plt.axhline(
        gbm_sigma_percent,
        linestyle="--",
        linewidth=2,
        label="GBM constant annual volatility",
    )
    plt.title(f"GARCH Volatility vs GBM Constant Volatility for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Annualized volatility (%)")
    plt.legend()
    plt.grid(True)
    plt.savefig(garch_vol_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(df["date"], df["log_return"])
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.title(f"Daily Log Returns for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Daily log return")
    plt.grid(True)
    plt.savefig(returns_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(df["date"], df["standardized_residual"])
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.axhline(2, linestyle="--", linewidth=1)
    plt.axhline(-2, linestyle="--", linewidth=1)
    plt.title(f"GARCH Standardized Residuals for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Standardized residual")
    plt.grid(True)
    plt.savefig(standardized_residuals_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.hist(df["standardized_residual"].dropna(), bins=60, density=True, alpha=0.7)

    x = np.linspace(-5, 5, 500)
    normal_density = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x**2)
    plt.plot(x, normal_density, linewidth=2)

    plt.title(f"GARCH Standardized Residuals for {symbol}: Histogram vs Normal")
    plt.xlabel("Standardized residual")
    plt.ylabel("Density")
    plt.grid(True)
    plt.savefig(standardized_residuals_hist_path, dpi=150)
    plt.close()

    return [
        garch_vol_path,
        returns_path,
        standardized_residuals_path,
        standardized_residuals_hist_path,
    ]


def main():
    symbol = "HBL"

    df = fetch_stock_data(symbol)
    df = compute_log_returns(df)

    result = fit_garch_model(df)
    df = add_garch_outputs_to_dataframe(df, result)

    gbm_sigma_percent = estimate_gbm_constant_volatility(df)

    print_summary(
        symbol=symbol,
        df=df,
        result=result,
        gbm_sigma_percent=gbm_sigma_percent,
    )

    saved_files = save_plots(
        df=df,
        symbol=symbol,
        gbm_sigma_percent=gbm_sigma_percent,
    )

    print()
    print("Charts saved:")
    for file_path in saved_files:
        print(file_path)


if __name__ == "__main__":
    main()