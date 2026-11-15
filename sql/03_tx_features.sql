USE fraud_lab;

DROP TABLE IF EXISTS tx_features;

CREATE TABLE tx_features AS
SELECT x.*, ROUND(
        x.TransactionAmt / NULLIF(x.prior_avg_amt, 0), 3
    ) AS amt_ratio
FROM (
        SELECT
            TransactionID, user_key, TransactionDT, TransactionAmt, isFraud, ROW_NUMBER() OVER w AS tx_seq, COUNT(*) OVER (
                w RANGE BETWEEN 3600 PRECEDING
                AND 1 PRECEDING
            ) AS tx_cnt_1h, COUNT(*) OVER (
                w RANGE BETWEEN 86400 PRECEDING
                AND 1 PRECEDING
            ) AS tx_cnt_24h, COUNT(*) OVER (
                w RANGE BETWEEN 604800 PRECEDING
                AND 1 PRECEDING
            ) AS tx_cnt_7d, AVG(TransactionAmt) OVER (
                w ROWS BETWEEN UNBOUNDED PRECEDING
                AND 1 PRECEDING
            ) AS prior_avg_amt, TransactionDT - LAG(TransactionDT) OVER w AS secs_since_prev
        FROM transactions
        WINDOW w AS (
                PARTITION BY
                    user_key
                ORDER BY TransactionDT
            )
    ) x;

ALTER TABLE tx_features ADD PRIMARY KEY (TransactionID);