# Corporate Bond Returns Pipeline

This pipeline downloads and processes corporate bond returns from OpenBondAssetPricing.com.

## Data Source

- [OpenBondAssetPricing.com](https://openbondassetpricing.com/) - TRACE data with market microstructure noise (MMN) adjustments

## Outputs

- `ftsfr_corp_bond_returns.parquet`: Individual corporate bond monthly returns
- `ftsfr_corp_bond_portfolio_returns.parquet`: Portfolio returns by credit spread decile
- `corporate_bond_returns.parquet`: Raw corporate bond data
- `treasury_bond_returns.parquet`: Treasury bond returns for comparison

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the pipeline:
   ```bash
   doit
   ```

3. View the generated documentation in `docs/index.html`

## Data Coverage

- Time period: 2002 - present (TRACE data)
- Frequency: Monthly
- Granularity: Individual bonds and credit spread-sorted portfolios

## Portfolio Construction

Bonds are sorted into 10 deciles based on credit spread:
- Decile 1: Lowest credit spread (safest bonds)
- Decile 10: Highest credit spread (riskiest bonds)

Returns are value-weighted within each decile.

## Academic References

### Primary Papers

- **He, Kelly, and Manela (2017)** - "Intermediary Asset Pricing: New Evidence from Many Asset Classes"
  - Journal of Financial Economics
  - Corporate bonds as test assets for intermediary capital factor

- **Dickerson, Mueller, and Robotti (2023)** - "Priced Risk in Corporate Bonds"
  - Critical examination of corporate bond factor models

### Key Findings

- Intermediary capital shocks explain cross-sectional variation in corporate bond returns
- Credit spread-sorted portfolios capture systematic risk in corporate bonds
