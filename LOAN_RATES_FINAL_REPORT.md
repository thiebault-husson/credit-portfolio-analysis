# Loan Rates Analysis - Final Report
*Generated: 2025-07-28 22:13:00*

## Executive Summary

This report provides a comprehensive analysis of delinquency, default, and charge-off rates for all loans in the `test_loan_tape.csv` dataset. The analysis covers 191 unique loans across 2,955 total records spanning from April 2022 to July 2025.

## Key Findings

### Portfolio Overview
- **Total Loans**: 191
- **Total Records**: 2,955
- **Date Range**: April 2022 - July 2025
- **Account Types**: 5 (LineRevolving, CardLegacy, CardCash, CardFlex, CardExtend)

### Overall Risk Metrics
- **Loans with Delinquency**: 23 (12.04%)
- **Loans with Default**: 15 (7.85%)
- **Loans with Charge-off**: 5 (2.62%)
- **Loans with Any Issues**: 23 (12.04%)
- **High-Risk Loans (Multiple Issues)**: 16 (8.38%)

### Average Rates
- **Average Delinquency Rate**: 0.80%
- **Average Default Rate**: 1.49%
- **Average Charge-off Rate**: 1.31%

## Account Type Analysis

### LineRevolving (126 loans, 66.0% of portfolio)
- **Loans with Delinquency**: 17 (13.49%)
- **Loans with Default**: 11 (8.73%)
- **Loans with Charge-off**: 2 (1.59%)
- **Average Delinquency Rate**: 0.83%
- **Average Default Rate**: 1.88%
- **Average Charge-off Rate**: 0.99%

### CardLegacy (23 loans, 12.0% of portfolio)
- **Loans with Delinquency**: 6 (26.09%)
- **Loans with Default**: 4 (17.39%)
- **Loans with Charge-off**: 3 (13.04%)
- **Average Delinquency Rate**: 2.14%
- **Average Default Rate**: 2.05%
- **Average Charge-off Rate**: 5.47%

### CardCash (24 loans, 12.6% of portfolio)
- **Loans with Delinquency**: 0 (0.00%)
- **Loans with Default**: 0 (0.00%)
- **Loans with Charge-off**: 0 (0.00%)
- **Average Delinquency Rate**: 0.00%
- **Average Default Rate**: 0.00%
- **Average Charge-off Rate**: 0.00%

### CardExtend (7 loans, 3.7% of portfolio)
- **Loans with Delinquency**: 0 (0.00%)
- **Loans with Default**: 0 (0.00%)
- **Loans with Charge-off**: 0 (0.00%)
- **Average Delinquency Rate**: 0.00%
- **Average Default Rate**: 0.00%
- **Average Charge-off Rate**: 0.00%

### CardFlex (11 loans, 5.8% of portfolio)
- **Loans with Delinquency**: 0 (0.00%)
- **Loans with Default**: 0 (0.00%)
- **Loans with Charge-off**: 0 (0.00%)
- **Average Delinquency Rate**: 0.00%
- **Average Default Rate**: 0.00%
- **Average Charge-off Rate**: 0.00%

## Current Status Distribution
- **Current**: 96 loans (50.26%)
- **Closed**: 89 loans (46.60%)
- **ChargedOff**: 5 loans (2.62%)
- **Default**: 1 loan (0.52%)

## High-Risk Loans Analysis

### Top 10 Riskiest Loans

1. **28e17309** (LineRevolving)
   - Delinquency Rate: 6.90%
   - Default Rate: 13.79%
   - Charge-off Rate: 58.62%
   - Status: ChargedOff

2. **90c5c2ac** (LineRevolving)
   - Delinquency Rate: 4.17%
   - Default Rate: 16.67%
   - Charge-off Rate: 66.67%
   - Status: ChargedOff

3. **d08b34d6** (CardLegacy)
   - Delinquency Rate: 11.54%
   - Default Rate: 3.85%
   - Charge-off Rate: 61.54%
   - Status: ChargedOff

4. **30aeea1b** (LineRevolving)
   - Delinquency Rate: 6.67%
   - Default Rate: 43.33%
   - Charge-off Rate: 0.00%
   - Status: Closed

5. **eec49c68** (LineRevolving)
   - Delinquency Rate: 5.88%
   - Default Rate: 82.35%
   - Charge-off Rate: 0.00%
   - Status: Default

6. **711554f2** (CardLegacy)
   - Delinquency Rate: 4.35%
   - Default Rate: 0.00%
   - Charge-off Rate: 43.48%
   - Status: ChargedOff

7. **32b536c7** (CardLegacy)
   - Delinquency Rate: 6.90%
   - Default Rate: 3.45%
   - Charge-off Rate: 20.69%
   - Status: ChargedOff

8. **3793702f** (LineRevolving)
   - Delinquency Rate: 5.88%
   - Default Rate: 20.59%
   - Charge-off Rate: 0.00%
   - Status: Closed

9. **c6956742** (LineRevolving)
   - Delinquency Rate: 14.81%
   - Default Rate: 14.81%
   - Charge-off Rate: 0.00%
   - Status: Closed

10. **d81be2b2** (CardLegacy)
    - Delinquency Rate: 4.35%
    - Default Rate: 30.43%
    - Charge-off Rate: 0.00%
    - Status: Closed

## Risk Insights

### Account Type Risk Profile
- **CardLegacy** shows the highest risk profile with 26.09% of loans experiencing delinquency
- **LineRevolving** accounts for the majority of the portfolio but shows moderate risk
- **CardCash, CardExtend, and CardFlex** show no risk issues in this dataset

### Portfolio Health Indicators
- **12.04%** of loans have experienced some form of risk event
- **8.38%** of loans have multiple risk issues
- **50.26%** of loans are currently in good standing
- **46.60%** of loans have been closed (likely paid off or refinanced)

### Charge-off Analysis
- Only **5 loans (2.62%)** have been charged off
- All charge-offs occurred in **LineRevolving** and **CardLegacy** products
- The highest charge-off rate is **66.67%** for loan 90c5c2ac

## Recommendations

1. **Monitor CardLegacy Portfolio**: This product shows the highest risk rates and should be closely monitored
2. **Review LineRevolving Risk Management**: While the default rate is acceptable, the delinquency rate suggests room for improvement
3. **Investigate High-Risk Loans**: The top 10 riskiest loans should be reviewed for common characteristics
4. **Product Performance**: CardCash, CardExtend, and CardFlex show excellent performance and could be expanded

## Data Quality Notes

- All dates were successfully parsed with some warnings about format inference
- No missing critical data fields
- Status transitions appear logical and consistent
- Balance and limit data are properly formatted

---

*Report generated using comprehensive analysis of 2,955 records across 191 unique loans* 