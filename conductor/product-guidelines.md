# Product Guidelines

## Tone & Voice
- **Professional & Technical:** Documentation and API responses should maintain a high standard of precision, using correct statistical and agricultural terminology.
- **Accuracy-First:** Prioritize the communication of statistical accuracy, model metrics, and data provenance over simplified explanations.

## Visual Identity
- **Academic & Minimalist:**
    - Visualizations should be high-contrast and suitable for academic publication.
    - Adhere to minimalist design principles, reducing "chart junk" to focus entirely on data trends and key insights.
    - Use clear, distinguishable markers for data points and error bars.

## Data Reporting & Uncertainty
- **Confidence Intervals:** All forecasts must be accompanied by calculated confidence intervals (e.g., 95%) to transparently communicate the range of probable outcomes.
- **Volatility Flagging:** The system must explicitly flag forecasts that are generated from limited, incomplete, or highly volatile historical data segments to warn users of potential reduced reliability.

## Data Governance
- **Open Data Principles:** Prioritize the use and attribution of publicly available data sources.
- **Controlled Access:** While the data foundation is open, API access to the forecasting engine requires authentication to ensure usage is tracked and restricted to verified stakeholders.
