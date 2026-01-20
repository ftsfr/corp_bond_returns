# %%
"""
# Corporate Bond Returns Summary
"""

# %%
import sys
sys.path.insert(0, "./src")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import chartbook

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"

# %%
"""
## Data Overview

This pipeline produces corporate bond returns data from OpenBondAssetPricing.com, including:
- Individual bond returns
- Portfolio returns grouped by credit spread deciles

### Data Source

The data comes from [openbondassetpricing.com](https://openbondassetpricing.com/), which provides
TRACE (Trade Reporting and Compliance Engine) data with market microstructure noise (MMN) adjustments.

### Data Cleaning (Following Nozawa 2017)

The data cleaning procedure follows the methodology established by Nozawa (2017):

1. **Bond Selection**: Exclude bonds with floating rate coupons and non-callable option features
2. **Price Filters**: Remove observations where bond price exceeds matched Treasury price
3. **Return Reversals**: Eliminate observations with adjacent return products < -0.04
4. **Synthetic Treasury Construction**: For each corporate bond, a synthetic Treasury with identical cash flows is constructed

### Portfolio Construction

Bonds are sorted into 10 deciles based on credit spread (CS), and value-weighted returns are computed:

$$r_{portfolio, t} = \sum_{i \\in portfolio} w_{i,t} \\cdot ret_{i,t}$$

where weights are based on bond market value (MMN-adjusted clean price × amount outstanding).
"""

# %%
"""
## Individual Bond Returns
"""

# %%
df_bonds = pd.read_parquet(DATA_DIR / "ftsfr_corp_bond_returns.parquet")
print(f"Shape: {df_bonds.shape}")
print(f"Columns: {df_bonds.columns.tolist()}")
print(f"\nDate range: {df_bonds['ds'].min()} to {df_bonds['ds'].max()}")
print(f"Number of unique bonds: {df_bonds['unique_id'].nunique()}")

# %%
df_bonds.describe()

# %%
"""
## Portfolio Returns by Credit Spread Decile
"""

# %%
df_portfolio = pd.read_parquet(DATA_DIR / "ftsfr_corp_bond_portfolio_returns.parquet")
print(f"Shape: {df_portfolio.shape}")
print(f"Columns: {df_portfolio.columns.tolist()}")
print(f"\nDate range: {df_portfolio['ds'].min()} to {df_portfolio['ds'].max()}")
print(f"Credit spread deciles: {sorted(df_portfolio['unique_id'].unique())}")

# %%
# Summary statistics by decile
portfolio_stats = df_portfolio.groupby("unique_id")["y"].agg(
    ["count", "mean", "std", "min", "max"]
)
portfolio_stats.columns = ["Count", "Mean", "Std", "Min", "Max"]
portfolio_stats

# %%
"""
## Time Series of Portfolio Returns
"""

# %%
# Pivot for plotting
df_pivot = df_portfolio.pivot(index="ds", columns="unique_id", values="y")
df_pivot = df_pivot[sorted(df_pivot.columns, key=lambda x: int(x))]

fig, ax = plt.subplots(figsize=(12, 6))
for col in df_pivot.columns:
    ax.plot(df_pivot.index, df_pivot[col], label=f"Decile {col}", alpha=0.7)
ax.set_xlabel("Date")
ax.set_ylabel("Monthly Return")
ax.set_title("Corporate Bond Portfolio Returns by Credit Spread Decile")
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# %%
"""
## Correlation Matrix

Correlation between credit spread deciles shows how returns move together across the credit risk spectrum.
"""

# %%
corr_matrix = df_pivot.corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Correlation Matrix of Portfolio Returns by Credit Spread Decile")
plt.tight_layout()
plt.show()

# %%
"""
## Return Distribution by Decile
"""

# %%
fig, ax = plt.subplots(figsize=(12, 6))
df_portfolio.boxplot(column="y", by="unique_id", ax=ax)
ax.set_xlabel("Credit Spread Decile")
ax.set_ylabel("Monthly Return")
ax.set_title("Distribution of Returns by Credit Spread Decile")
plt.suptitle("")  # Remove automatic title
plt.tight_layout()
plt.show()

# %%
"""
## Credit Spread Decile Definitions

| Decile | Description |
|--------|-------------|
| 1 | Lowest credit spread (safest bonds) |
| 2-9 | Intermediate credit spreads |
| 10 | Highest credit spread (riskiest bonds) |

Bonds are sorted into deciles based on their credit spread relative to matched Treasury securities.
Higher deciles represent bonds with wider credit spreads, typically indicating higher credit risk.
"""
