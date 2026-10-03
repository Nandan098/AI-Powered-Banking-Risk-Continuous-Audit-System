# Assumptions and Limitations

- All records are synthetic.
- Controlled anomaly scenarios are created for model-development evaluation and are not real fraud labels.
- Rule thresholds, score weights and risk-level cutoffs are project configurations.
- Location distance uses synthetic city coordinates.
- Demographic fields are retained for descriptive context but are excluded from the model's risk features.
- Annual income is excluded from model scoring.
- Isolation Forest is an unsupervised anomaly detector; high anomaly score means unusual relative to learned behavior, not proof of fraud.
- A production system would need real historical validation, model governance, monitoring, human review, security, access controls, regulatory review and threshold calibration.
