# Interview Story

## 30-second version
I built an AI-powered banking risk and continuous-audit platform using synthetic banking transactions. I first profiled and cleaned relational customer, account, merchant, device and transaction data. I then engineered behavioral features such as transaction velocity, customer amount deviation, device novelty, channel rarity and location distance. An Isolation Forest model generated anomaly scores, while explainable business rules added auditable evidence. I combined those signals into a configurable risk score, created an audit-case queue, persisted the results for PostgreSQL/API access, and exposed Power BI-ready reporting tables.

## Why the design is realistic
The system does not assume every transaction is equally risky. Most transactions are ordinary, transaction amounts are long-tailed, customer activity varies widely, and anomaly scenarios are deliberately rare and uneven. The evaluation labels are kept in a separate file and are never used as unsupervised model inputs.

## Important wording
Say **potentially unusual / higher-risk transaction** rather than claiming a transaction is fraudulent. A real bank implementation would require model validation, governance, human review and production controls.
