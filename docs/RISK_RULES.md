# Risk Rules

The rules below are **project-designed controls** for demonstration. They are not IndusInd Bank rules.

- Large relative transaction: amount is unusually large versus the customer's transaction baseline.
- Velocity: unusually many transactions in a short rolling window.
- Duplicate-like: near-duplicate business attributes within two minutes on the same account.
- Location: large geographic deviation from the customer's home city.
- New device: first-seen device with an unusually large amount relative to the customer's baseline.
- Rare channel: a channel historically uncommon for the customer.

The combined score uses ML, rule evidence, behavioral features and context. Thresholds are project configuration, not bank policy.
