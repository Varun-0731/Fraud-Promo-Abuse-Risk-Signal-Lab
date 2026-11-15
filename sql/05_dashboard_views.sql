USE fraud_lab;

CREATE OR REPLACE VIEW v_daily_risk AS
SELECT
    FLOOR(TransactionDT / 86400) AS day_no,
    COUNT(*) AS transactions,
    SUM(isFraud) AS frauds,
    ROUND(AVG(isFraud) * 100, 3) AS fraud_rate_pct,
    SUM(tier_flag) AS tier_flagged,
    ROUND(AVG(tier_flag) * 100, 3) AS tier_flag_rate_pct,
    SUM(tier_flag * isFraud) AS tier_caught,
    ROUND(AVG(forest_score), 4) AS avg_forest_score,
    ROUND(AVG(TransactionAmt), 2) AS avg_amount
FROM tx_scored
GROUP BY
    FLOOR(TransactionDT / 86400);

CREATE OR REPLACE VIEW v_rule_performance AS
WITH
    totals AS (
        SELECT period, COUNT(*) AS n, SUM(isFraud) AS frauds
        FROM tx_scored
        GROUP BY
            period
    ),
    rules AS (
        SELECT
            period,
            'R1 device profile' AS rule_name,
            SUM(r1_device_profile) AS flagged,
            SUM(r1_device_profile * isFraud) AS caught
        FROM tx_scored
        GROUP BY
            period
        UNION ALL
        SELECT period, 'R2 identity, no device info', SUM(r2_identity_no_device), SUM(
                r2_identity_no_device * isFraud
            )
        FROM tx_scored
        GROUP BY
            period
        UNION ALL
        SELECT period, 'Tier (R1 or R2)', SUM(tier_flag), SUM(tier_flag * isFraud)
        FROM tx_scored
        GROUP BY
            period
    )
SELECT
    r.period,
    r.rule_name,
    r.flagged,
    r.caught,
    t.n AS total_tx,
    t.frauds AS total_frauds,
    ROUND(r.caught / r.flagged * 100, 2) AS precision_pct,
    ROUND(r.caught / t.frauds * 100, 2) AS recall_pct,
    ROUND(
        (r.flagged - r.caught) / (t.n - t.frauds) * 100,
        2
    ) AS fpr_pct
FROM rules r
    JOIN totals t ON t.period = r.period;

CREATE OR REPLACE VIEW v_velocity_buckets AS
SELECT
    prior_tx_1h,
    sort_order,
    COUNT(*) AS n,
    ROUND(AVG(isFraud) * 100, 2) AS fraud_rate_pct
FROM (
        SELECT
            isFraud, CASE
                WHEN tx_cnt_1h = 0 THEN '0'
                WHEN tx_cnt_1h = 1 THEN '1'
                WHEN tx_cnt_1h <= 3 THEN '2-3'
                ELSE '4+'
            END AS prior_tx_1h, CASE
                WHEN tx_cnt_1h = 0 THEN 1
                WHEN tx_cnt_1h = 1 THEN 2
                WHEN tx_cnt_1h <= 3 THEN 3
                ELSE 4
            END AS sort_order
        FROM tx_scored
    ) x
GROUP BY
    prior_tx_1h,
    sort_order;

CREATE OR REPLACE VIEW v_device_buckets AS
SELECT
    device_bucket,
    sort_order,
    COUNT(*) AS n,
    ROUND(AVG(isFraud) * 100, 2) AS fraud_rate_pct
FROM (
        SELECT
            isFraud, CASE
                WHEN has_identity = 0 THEN 'No identity record'
                WHEN users_on_device IS NULL THEN 'Identity, no device info'
                WHEN users_on_device = 1 THEN '1 user'
                WHEN users_on_device <= 3 THEN '2-3 users'
                WHEN users_on_device <= 10 THEN '4-10 users'
                WHEN users_on_device <= 50 THEN '11-50 users'
                ELSE 'Over 50 users'
            END AS device_bucket, CASE
                WHEN has_identity = 0 THEN 1
                WHEN users_on_device IS NULL THEN 2
                WHEN users_on_device = 1 THEN 3
                WHEN users_on_device <= 3 THEN 4
                WHEN users_on_device <= 10 THEN 5
                WHEN users_on_device <= 50 THEN 6
                ELSE 7
            END AS sort_order
        FROM tx_scored
    ) x
GROUP BY
    device_bucket,
    sort_order;