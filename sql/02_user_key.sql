USE fraud_lab;

SET SQL_SAFE_UPDATES = 0;

ALTER TABLE transactions ADD COLUMN user_key VARCHAR(40);

UPDATE transactions
SET
    user_key = CONCAT_WS(
        '_',
        card1,
        IFNULL(card2, -1),
        IFNULL(addr1, -1)
    );

CREATE INDEX idx_tx_user_time ON transactions (user_key, TransactionDT);