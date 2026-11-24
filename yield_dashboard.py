"""
Government bond yield dashboard: UK gilts vs US Treasuries vs German Bunds.

What it does
1. Downloads monthly 10-year government bond yields from FRED (free, no account needed).
2. Plots the three yields on one chart.
3. Plots the spreads (difference in yield) between them.
4. Prints the latest numbers in the terminal.

Run:  python yield_dashboard.py
Test without internet:  python yield_dashboard.py --demo   (uses made-up data, for testing only)
"""

import sys

import matplotlib.pyplot as plt
import pandas as pd

# --- 1. SETTINGS -----------------------------------------------------------
# Each country maps to a FRED series code (OECD monthly 10-year government bond yields).
SERIES = {
    "UK Gilt 10Y": "IRLTLT01GBM156N",
    "US Treasury 10Y": "IRLTLT01USM156N",
    "German Bund 10Y": "IRLTLT01DEM156N",
}
START_DATE = "2015-01-01"  # change this to look at a longer or shorter period


# --- 2. GET THE DATA -------------------------------------------------------
def download_yields() -> pd.DataFrame:
    """Download each series from FRED and put them side by side in one table."""
    columns = {}
    for name, code in SERIES.items():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={code}"
        data = pd.read_csv(url, index_col=0, parse_dates=True)
        columns[name] = pd.to_numeric(data.iloc[:, 0], errors="coerce")
    table = pd.DataFrame(columns)
    return table.loc[START_DATE:].dropna()


def demo_yields() -> pd.DataFrame:
    """FAKE data, only to test that the charts work offline. Never use for analysis."""
    import numpy as np

    dates = pd.date_range(START_DATE, periods=120, freq="MS")
    rng = np.random.default_rng(0)
    base = np.cumsum(rng.normal(0, 0.1, len(dates))) + 2
    return pd.DataFrame(
        {
            "UK Gilt 10Y": base + 0.3,
            "US Treasury 10Y": base + 0.5,
            "German Bund 10Y": base - 1.0,
        },
        index=dates,
    )


# --- 3. CALCULATE SPREADS --------------------------------------------------
def add_spreads(yields: pd.DataFrame) -> pd.DataFrame:
    """A spread is one yield minus another. 1 percentage point = 100 basis points (bp)."""
    spreads = pd.DataFrame(index=yields.index)
    spreads["Gilt minus Bund (bp)"] = (yields["UK Gilt 10Y"] - yields["German Bund 10Y"]) * 100
    spreads["Treasury minus Bund (bp)"] = (yields["US Treasury 10Y"] - yields["German Bund 10Y"]) * 100
    spreads["Gilt minus Treasury (bp)"] = (yields["UK Gilt 10Y"] - yields["US Treasury 10Y"]) * 100
    return spreads


# --- 4. DRAW THE DASHBOARD -------------------------------------------------
def draw(yields: pd.DataFrame, spreads: pd.DataFrame, demo: bool) -> None:
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    yields.plot(ax=top)
    top.set_title("10-year government bond yields" + ("  [DEMO DATA - NOT REAL]" if demo else ""))
    top.set_ylabel("Yield (%)")
    top.grid(alpha=0.3)

    spreads.plot(ax=bottom)
    bottom.set_title("Yield spreads (basis points)")
    bottom.set_ylabel("Spread (bp)")
    bottom.axhline(0, color="black", linewidth=0.8)
    bottom.grid(alpha=0.3)

    source = "Source: OECD via FRED" if not demo else "Fake data for testing"
    fig.text(0.01, 0.01, source, fontsize=8, color="grey")
    fig.tight_layout()
    output = "yield_dashboard_demo.png" if demo else "yield_dashboard.png"
    fig.savefig(output, dpi=150)
    print(f"Chart saved as {output}")


# --- 5. RUN EVERYTHING -----------------------------------------------------
def main() -> None:
    demo = "--demo" in sys.argv
    yields = demo_yields() if demo else download_yields()
    spreads = add_spreads(yields)

    print("Latest values:")
    print(yields.iloc[-1].round(2).to_string())
    print()
    print(spreads.iloc[-1].round(0).to_string())

    draw(yields, spreads, demo)


if __name__ == "__main__":
    main()
