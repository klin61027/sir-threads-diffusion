"""
Fit the SIR model to Threads view-count data.

For each post, beta and gamma are chosen by nonlinear least squares so that
the model's cumulative proportion 1 - S(t) matches the observed views.

Input : data/threads_SIR_ready.csv
Output: figures/threads_ALL_analysis.png  and a table of beta, gamma, R0
"""
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import odeint
from scipy.optimize import curve_fit

CSV_FILE = os.path.join("data", "threads_SIR_ready.csv")
SAVE_PATH = os.path.join("figures", "threads_ALL_analysis.png")

PLOT_LABELS = None   # e.g. ["trends", "Costco"]; None plots every post
MIN_POINTS = 4       # minimum points needed to fit a curve
R0_THRESHOLD = 1.0   # R0 above this is marked "Viral"


def sir_derivatives(y, t, beta, gamma):
    """Right-hand side of the SIR system (in fractions)."""
    S, I, R = y
    dSdt = -beta * S * I
    dIdt = beta * S * I - gamma * I
    dRdt = gamma * I
    return dSdt, dIdt, dRdt


def make_fit_func(initial_I0):
    """Return f(t, beta, gamma) = 1 - S(t), the cumulative viewed fraction."""
    def fit_func(t, beta, gamma):
        y0 = [1.0 - initial_I0, initial_I0, 0.0]
        sol = odeint(sir_derivatives, y0, t, args=(beta, gamma))
        S_t, _, _ = sol.T
        return 1.0 - S_t
    return fit_func


def load_data(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Could not find file at {csv_path}")
    return pd.read_csv(csv_path)


def fit_post(subset):
    """Fit the SIR model for one post."""
    subset = subset.sort_values(by="Hours_Elapsed")
    t_data = subset["Hours_Elapsed"].values
    y_data = subset["Views_Cleaned"].values

    if len(t_data) < MIN_POINTS:
        raise ValueError("Too few data points for fitting")

    N = y_data.max() * 1.2          # effective audience size
    y_norm = y_data / N
    fit_func = make_fit_func(y_norm[0])

    params, _ = curve_fit(fit_func, t_data, y_norm,
                          p0=[0.5, 0.1], bounds=(0, [10.0, 5.0]))
    beta, gamma = params
    gamma = max(gamma, 1e-4)        # avoid dividing by a tiny gamma
    R0 = beta / gamma

    t_smooth = np.linspace(0, t_data.max() + 12, 200)
    y_smooth = fit_func(t_smooth, beta, gamma) * N
    return beta, gamma, R0, t_data, y_data, t_smooth, y_smooth


def main():
    df = load_data(CSV_FILE)
    all_labels = df["Post_Label"].unique()
    labels = all_labels if PLOT_LABELS is None else [l for l in all_labels if l in PLOT_LABELS]
    print(f"Found {len(all_labels)} post labels: {all_labels}\n")

    results = []
    print(f"{'Label':<15} | {'Beta':<8} | {'Gamma':<8} | {'R0':<10} | Status")
    print("-" * 70)

    plt.figure(figsize=(12, 7))
    cmap = plt.get_cmap("tab10")

    for idx, label in enumerate(labels):
        subset = df[df["Post_Label"] == label].copy()
        try:
            beta, gamma, R0, t_data, y_data, t_smooth, y_smooth = fit_post(subset)
            status = "Viral" if R0 > R0_THRESHOLD else "Not viral"
            print(f"{label:<15} | {beta:.4f}   | {gamma:.4f}   | {R0:.4f}     | {status}")

            color = cmap(idx % 10)
            plt.scatter(t_data, y_data, color=color, s=15, alpha=0.6)
            plt.plot(t_smooth, y_smooth, color=color, linewidth=2.2,
                     label=f"{label} ($R_0={R0:.1f}$)")
            results.append((label, R0))
        except Exception as e:
            print(f"{label:<15} | Fit failed: {e}")

    # Sort the legend by R0, largest first
    if results:
        handles, legend_labels = plt.gca().get_legend_handles_labels()
        r0_map = {lab: r for lab, r in results}
        order = sorted(range(len(legend_labels)),
                       key=lambda i: r0_map.get(legend_labels[i].split(" ($")[0], 0.0),
                       reverse=True)
        plt.legend([handles[i] for i in order], [legend_labels[i] for i in order],
                   bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0.0, fontsize=9)

    plt.title("SIR Model Analysis: Viral Growth on Threads", fontsize=16)
    plt.xlabel("Hours Since First Observation", fontsize=13)
    plt.ylabel("Total Views", fontsize=13)
    plt.grid(alpha=0.3)
    plt.tight_layout()

    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    plt.savefig(SAVE_PATH, dpi=300)
    print(f"\nAnalysis complete. Graph saved to: {SAVE_PATH}")
    plt.show()


if __name__ == "__main__":
    main()
