import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

PARAMETER_FILE = OUTPUT_DIR / "heston_parameter_estimates_hbl.csv"


def load_estimated_parameters() -> dict:
    """
    Load Heston-style parameters estimated from the Student-t GARCH
    variance proxy.

    These are historical proxy estimates, not full option-implied
    Heston calibration estimates.
    """

    if not PARAMETER_FILE.exists():
        raise FileNotFoundError(
            f"Could not find parameter file: {PARAMETER_FILE}\n"
            "Run estimate_heston_parameters_hbl.py first."
        )

    estimates = pd.read_csv(PARAMETER_FILE).iloc[0].to_dict()

    return {
        "symbol": estimates["symbol"],
        "S0": float(estimates["S0"]),
        "mu": float(estimates["mu"]),
        "v0": float(estimates["v0"]),
        "theta": float(estimates["theta"]),
        "kappa": float(estimates["kappa"]),
        "xi": float(estimates["xi"]),
        "rho": float(estimates["rho"]),
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

    This simulation uses historical proxy estimates from a GARCH variance
    series. It is not a full option-calibrated Heston model.
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

        variance_next = (
            variances[t - 1]
            + kappa * (theta - previous_variance) * dt
            + xi * np.sqrt(previous_variance) * np.sqrt(dt) * z2
        )

        variances[t] = np.maximum(variance_next, 0)

        variance_for_price = np.maximum(previous_variance, 0)

        exponent = (
            (mu - 0.5 * variance_for_price) * dt
            + np.sqrt(variance_for_price) * np.sqrt(dt) * z1
        )

        prices[t] = prices[t - 1] * np.exp(exponent)

    return prices, variances


def simulate_gbm_paths(
    S0: float,
    mu: float,
    sigma: float,
    days: int = 252,
    n_paths: int = 20,
    seed: int = 123,
):
    """
    Simulate GBM paths using constant volatility.

    The GBM volatility benchmark is taken as sqrt(theta), the estimated
    long-run volatility from the Heston-style parameter estimates.
    """

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


def print_summary(params: dict):
    print(f"Symbol: {params['symbol']}")
    print()
    print("Estimated Heston-style parameters used in simulation:")
    print(f"S0, latest close price: {params['S0']:.4f}")
    print(f"mu, annual drift estimate: {params['mu']:.6f}")
    print(f"v0, initial variance: {params['v0']:.6f}")
    print(f"sqrt(v0), initial annual volatility: {np.sqrt(params['v0']):.6f}")
    print(f"theta, long-run variance: {params['theta']:.6f}")
    print(f"sqrt(theta), long-run annual volatility: {np.sqrt(params['theta']):.6f}")
    print(f"kappa, speed of variance mean reversion: {params['kappa']:.6f}")
    print(f"xi, volatility of volatility: {params['xi']:.6f}")
    print(f"rho, price-volatility shock correlation: {params['rho']:.6f}")
    print()
    print("Important note:")
    print("These values are historical proxy estimates based on a Student-t GARCH variance proxy.")
    print("They are not full option-implied Heston calibration estimates.")


def save_plots(
    params: dict,
    heston_prices: np.ndarray,
    heston_variances: np.ndarray,
    gbm_prices: np.ndarray,
):
    symbol = params["symbol"]

    heston_price_path = OUTPUT_DIR / "estimated_heston_price_paths.png"
    heston_volatility_path = OUTPUT_DIR / "estimated_heston_volatility_paths.png"
    heston_vs_gbm_path = OUTPUT_DIR / "estimated_heston_vs_gbm_price_paths.png"

    heston_volatility = np.sqrt(heston_variances) * 100
    gbm_volatility_percent = np.sqrt(params["theta"]) * 100

    plt.figure(figsize=(10, 6))
    for i in range(heston_prices.shape[1]):
        plt.plot(heston_prices[:, i], alpha=0.7)

    plt.title(f"Estimated Heston-Style Price Paths for {symbol}")
    plt.xlabel("Trading days into future")
    plt.ylabel("Simulated price")
    plt.grid(True)
    plt.savefig(heston_price_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))
    for i in range(heston_volatility.shape[1]):
        plt.plot(heston_volatility[:, i], alpha=0.7)

    plt.axhline(
        gbm_volatility_percent,
        linestyle="--",
        linewidth=2,
        label="Long-run volatility sqrt(theta)",
    )

    plt.title(f"Estimated Heston-Style Volatility Paths for {symbol}")
    plt.xlabel("Trading days into future")
    plt.ylabel("Annualized volatility (%)")
    plt.legend()
    plt.grid(True)
    plt.savefig(heston_volatility_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 6))

    for i in range(min(10, heston_prices.shape[1])):
        plt.plot(heston_prices[:, i], alpha=0.7)

    for i in range(min(10, gbm_prices.shape[1])):
        plt.plot(gbm_prices[:, i], linestyle="--", alpha=0.7)

    plt.title(f"Estimated Heston-Style Paths vs GBM Paths for {symbol}")
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
    params = load_estimated_parameters()

    days = 252
    n_paths = 20

    heston_prices, heston_variances = simulate_heston_paths(
        S0=params["S0"],
        v0=params["v0"],
        mu=params["mu"],
        theta=params["theta"],
        kappa=params["kappa"],
        xi=params["xi"],
        rho=params["rho"],
        days=days,
        n_paths=n_paths,
    )

    gbm_sigma = np.sqrt(params["theta"])

    gbm_prices = simulate_gbm_paths(
        S0=params["S0"],
        mu=params["mu"],
        sigma=gbm_sigma,
        days=days,
        n_paths=n_paths,
    )

    print_summary(params)

    saved_files = save_plots(
        params=params,
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