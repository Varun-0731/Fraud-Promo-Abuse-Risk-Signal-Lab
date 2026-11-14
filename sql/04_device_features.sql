USE fraud_lab;

SET SQL_SAFE_UPDATES = 0;

DROP TABLE IF EXISTS device_stats;

CREATE TABLE device_stats AS
SELECT
    i.DeviceInfo,
    COUNT(DISTINCT t.user_key) AS users_on_device,
    COUNT(*) AS tx_on_device
FROM identity i
    JOIN transactions t ON t.TransactionID = i.TransactionID
WHERE
    i.DeviceInfo IS NOT NULL
GROUP BY
    i.DeviceInfo;

ALTER TABLE device_stats ADD PRIMARY KEY (DeviceInfo);

ALTER TABLE tx_features
ADD COLUMN has_identity TINYINT,
ADD COLUMN users_on_device INT;

UPDATE tx_features f
LEFT JOIN identity i ON i.TransactionID = f.TransactionID
LEFT JOIN device_stats d ON d.DeviceInfo = i.DeviceInfo
SET
    f.has_identity = IF(i.TransactionID IS NULL, 0, 1),
    f.users_on_device = d.users_on_device;