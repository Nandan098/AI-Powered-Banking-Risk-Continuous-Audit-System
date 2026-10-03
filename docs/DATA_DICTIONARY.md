# Data Dictionary

## customers.csv
`customer_id`, `customer_name`, `age`, `gender`, `city`, `occupation`, `annual_income`, `customer_since`

## accounts.csv
`account_id`, `customer_id`, `account_type`, `opening_date`, `balance`, `status`

## merchants.csv
`merchant_id`, `merchant_category`, `city`, `merchant_risk_band`, `merchant_size`

## customer_devices.csv
`device_id`, `customer_id`, `device_type`, `first_seen`, `last_seen`

## transactions.csv
`transaction_id`, `account_id`, `customer_id`, `transaction_date`, `transaction_type`, `channel`, `amount`, `merchant_id`, `merchant_category`, `location`, `device_id`, `status`

## transaction_ground_truth.csv
`transaction_id`, `scenario`, `is_controlled_anomaly` — evaluation-only; never use as model input.
