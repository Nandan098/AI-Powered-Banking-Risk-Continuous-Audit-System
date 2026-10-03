# Model Card — Isolation Forest

## Purpose
Identify transactions that are unusual relative to learned transaction behavior and prioritize them for review.

## Model
Isolation Forest with RobustScaler preprocessing.

## Features
Behavioral and transaction-context features such as amount deviation from customer baseline, transaction velocity,
location distance from home city, device novelty, channel rarity and time features.

## Features intentionally excluded from model scoring
Demographic fields such as gender and occupation are not used as model inputs. Annual income is also excluded from
risk scoring so that the anomaly detector concentrates on observed transaction behavior rather than socioeconomic
attributes.

## Ground-truth evaluation
`data/reference/transaction_ground_truth.csv` contains synthetic, project-created anomaly scenarios for evaluation only.
The labels are not used as model input.

## Limitations
This is a portfolio project using synthetic data. It is not a production fraud model, and model scores should not be
interpreted as proof of fraud or misconduct. A real deployment would require model governance, validation on real data,
threshold calibration, explainability review, access controls, monitoring, and human investigation workflows.
