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


def fit_garch_model(df: pd.DataFrame, distribution: str):
    """
    Fit a GARCH(1,1) model.

    Returns are multiplied by 100 because the arch package usually behaves
    better numerically when returns are expressed in percentage units.
    """

    returns_percent = df["log_return"] * 100

    model = arch_model(
        returns_percent,
        mean="Constant",
        vol="GARCH",
        p=1,
        q=1,
        dist=distribution,
        rescale=False,
    )

    result = model.fit(disp="off")

    return result


def extract_model_summary(result, model_name: str) -> dict:
    params = result.params

    mu = params.get("mu", np.nan)
    omega = params.get("omega", np.nan)
    alpha = params.get("alpha[1]", np.nan)
    beta = params.get("beta[1]", np.nan)
    nu = params.get("nu", np.nan)

    return {
        "model": model_name,
        "mu": mu,
        "omega": omega,
        "alpha": alpha,
        "beta": beta,
        "alpha_plus_beta": alpha + beta,
        "nu": nu,
        "log_likelihood": result.loglikelihood,
        "aic": result.aic,
        "bic": result.bic,
    }


def add_volatility_series(
    df: pd.DataFrame,
    normal_result,
    student_t_result,
) -> pd.DataFrame:
    df = df.copy()

    df["normal_garch_daily_vol_percent"] = normal_result.conditional_volatility
    df["student_t_garch_daily_vol_percent"] = student_t_result.conditional_volatility

    df["normal_garch_annual_vol_percent"] = (
        df["normal_garch_daily_vol_percent"] * np.sqrt(252)
    )
    df["student_t_garch_annual_vol_percent"] = (
        df["student_t_garch_daily_vol_percent"] * np.sqrt(252)
    )

    df["normal_standardized_residual"] = normal_result.std_resid
    df["student_t_standardized_residual"] = student_t_result.std_resid

    return df


def estimate_gbm_constant_volatility(df: pd.DataFrame) -> float:
    daily_volatility = df["log_return"].std()
    annual_volatility_percent = daily_volatility * np.sqrt(252) * 100

    return annual_volatility_percent


def print_comparison(
    symbol: str,
    df: pd.DataFrame,
    normal_result,
    student_t_result,
    comparison_df: pd.DataFrame,
    gbm_sigma_percent: float,
):
    print(f"Symbol: {symbol}")
    print(f"Number of return observations: {len(df)}")
    print(f"First date: {df['date'].min().date()}")
    print(f"Last date: {df['date'].max().date()}")
    print()

    print("Model comparison:")
    print(comparison_df.to_string(index=False))
    print()

    normal_latest_vol = df["normal_garch_annual_vol_percent"].iloc[-1]
    student_t_latest_vol = df["student_t_garch_annual_vol_percent"].iloc[-1]

    normal_average_vol = df["normal_garch_annual_vol_percent"].mean()
    student_t_average_vol = df["student_t_garch_annual_vol_percent"].mean()

    print("Volatility comparison:")
    print(f"GBM constant annual volatility: {gbm_sigma_percent:.2f}%")
    print(f"Normal GARCH average annual volatility: {normal_average_vol:.2f}%")
    print(f"Student-t GARCH average annual volatility: {student_t_average_vol:.2f}%")
    print(f"Normal GARCH latest annual volatility: {normal_latest_vol:.2f}%")
    print(f"Student-t GARCH latest annual volatility: {student_t_latest_vol:.2f}%")
    print()

    print("Interpretation guide:")
    print("Lower AIC and BIC usually indicate a better model fit.")
    print("Higher log-likelihood indicates a better fit.")
    print("The Student-t model is useful when residuals have heavy tails.")
    print("The nu parameter controls tail thickness in the Student-t distribution.")
    print("Smaller nu means heavier tails.")
    print()

    print("Normal GARCH summary:")
    print(normal_result.summary())
    print()

    print("Student-t GARCH summary:")
    print(student_t_result.summary())


def save_plots(
    df: pd.DataFrame,
    symbol: str,
    gbm_sigma_percent: float,
):
    volatility_comparison_path = OUTPUT_DIR / "normal_vs_student_t_garch_volatility.png"
    residual_histogram_path = OUTPUT_DIR / "student_t_garch_standardized_residuals_histogram.png"
    residuals_over_time_path = OUTPUT_DIR / "student_t_garch_standardized_residuals.png"
    model_comparison_path = OUTPUT_DIR / "normal_vs_student_t_garch_model_comparison.csv"

    plt.figure(figsize=(10, 6))
    plt.plot(
        df["date"],
        df["normal_garch_annual_vol_percent"],
        label="Normal GARCH annualized volatility",
    )
    plt.plot(
        df["date"],
        df["student_t_garch_annual_vol_percent"],
        label="Student-t GARCH annualized volatility",
    )
    plt.axhline(
        gbm_sigma_percent,
        linestyle="--",
        linewidth=2,
        label="GBM constant annual volatility",
    )
    plt.title(f"Normal vs Student-t GARCH Volatility for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Annualized volatility (%)")
    plt.legend()
    plt.grid(True)
    plt.savefig(volatility_comparison_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    residuals = df["student_t_standardized_residual"].dropna()
    plt.hist(residuals, bins=60, density=True, alpha=0.7)

    x = np.linspace(-5, 5, 500)
    normal_density = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x**2)
    plt.plot(x, normal_density, linewidth=2)

    plt.title(f"Student-t GARCH Standardized Residuals for {symbol}")
    plt.xlabel("Standardized residual")
    plt.ylabel("Density")
    plt.grid(True)
    plt.savefig(residual_histogram_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(df["date"], df["student_t_standardized_residual"])
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.axhline(2, linestyle="--", linewidth=1)
    plt.axhline(-2, linestyle="--", linewidth=1)
    plt.title(f"Student-t GARCH Standardized Residuals Over Time for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Standardized residual")
    plt.grid(True)
    plt.savefig(residuals_over_time_path, dpi=150)
    plt.close()

    return [
        volatility_comparison_path,
        residual_histogram_path,
        residuals_over_time_path,
        model_comparison_path,
    ]


def main():
    symbol = "HBL"

    df = fetch_stock_data(symbol)
    df = compute_log_returns(df)

    normal_result = fit_garch_model(df, distribution="normal")
    student_t_result = fit_garch_model(df, distribution="t")

    df = add_volatility_series(
        df=df,
        normal_result=normal_result,
        student_t_result=student_t_result,
    )

    gbm_sigma_percent = estimate_gbm_constant_volatility(df)

    normal_summary = extract_model_summary(
        result=normal_result,
        model_name="Normal GARCH(1,1)",
    )
    student_t_summary = extract_model_summary(
        result=student_t_result,
        model_name="Student-t GARCH(1,1)",
    )

    comparison_df = pd.DataFrame([normal_summary, student_t_summary])

    model_comparison_path = OUTPUT_DIR / "normal_vs_student_t_garch_model_comparison.csv"
    comparison_df.to_csv(model_comparison_path, index=False)

    print_comparison(
        symbol=symbol,
        df=df,
        normal_result=normal_result,
        student_t_result=student_t_result,
        comparison_df=comparison_df,
        gbm_sigma_percent=gbm_sigma_percent,
    )

    saved_files = save_plots(
        df=df,
        symbol=symbol,
        gbm_sigma_percent=gbm_sigma_percent,
    )

    print()
    print("Files saved:")
    for file_path in saved_files:
        print(file_path)


if __name__ == "__main__":
    main()