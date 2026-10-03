# Project Results (Synthetic Development Dataset)

The pipeline was executed on the included synthetic dataset.

## Pipeline output
- Transactions scored: 200,000
- High risk: 247
- Medium risk: 2,961
- Low risk: 196,792
- Audit cases created: 3,208

## Isolation Forest evaluation
- Average precision: 0.0673
- Precision at the top-1.5% anomaly-score cutoff: 0.0623
- Recall: 0.0656
- F1: 0.0639

## Combined risk-score evaluation
- Average precision: 0.0703
- Precision at the configured high-risk threshold: 0.1093
- Recall: 0.0095
- F1: 0.0174

These are **development metrics on synthetic controlled scenarios**, not production performance measures. The evaluation labels are kept outside the unsupervised model feature set.
