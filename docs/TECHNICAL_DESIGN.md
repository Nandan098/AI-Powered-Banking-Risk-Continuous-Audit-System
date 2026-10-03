# Technical Design

## Data layers
1. Raw: immutable source CSVs.
2. Processed: cleaned and typed tables.
3. Feature: transaction behavioral feature store.
4. Risk: ML scores, rule scores and combined risk levels.
5. Audit: prioritized review queue.
6. Reporting: Power BI-ready aggregates and detail tables.

## Feature groups
- Amount behavior: log amount, customer median/IQR, robust deviation, amount-to-baseline ratio.
- Velocity: transactions in 10-minute, 1-hour and 24-hour windows; previous-transaction gap.
- Novelty/context: location distance/change, new device, channel rarity, merchant-category rarity.
- Time: hour, day-of-week, weekend, cyclical hour encoding.

## ML
Isolation Forest is trained on an earlier time period (`TRAIN_END`) and scores the full period. This gives a simple chronological development setup and avoids feeding synthetic ground-truth labels to the model.

## Explainability
Business rules generate explicit textual reasons. The final risk score keeps ML as the largest component while preserving rule evidence.

## Audit workflow
Risk score → risk level → case creation → reviewer status → resolution.
The FastAPI review endpoint updates case status and review information in PostgreSQL.
