CREATE DATABASE IF NOT EXISTS fraud_lab CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE fraud_lab;

CREATE TABLE IF NOT EXISTS transactions (
    TransactionID INT PRIMARY KEY,
    isFraud TINYINT NOT NULL,
    TransactionDT INT NOT NULL,
    TransactionAmt DECIMAL(12, 2) NOT NULL,
    ProductCD CHAR(1),
    card1 INT,
    card2 SMALLINT,
    card3 SMALLINT,
    card4 VARCHAR(20),
    card5 SMALLINT,
    card6 VARCHAR(20),
    addr1 SMALLINT,
    addr2 SMALLINT,
    dist1 FLOAT,
    P_emaildomain VARCHAR(50),
    R_emaildomain VARCHAR(50),
    C1 FLOAT,
    C2 FLOAT,
    C5 FLOAT,
    C13 FLOAT,
    D1 FLOAT,
    D15 FLOAT
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS identity (
    TransactionID INT PRIMARY KEY,
    DeviceType VARCHAR(20),
    DeviceInfo VARCHAR(100),
    id_30 VARCHAR(50),
    id_31 VARCHAR(50),
    id_33 VARCHAR(20)
) ENGINE = InnoDB;

CREATE INDEX idx_tx_time ON transactions (TransactionDT);

CREATE INDEX idx_tx_card ON transactions (card1, card2, addr1);

CREATE INDEX idx_id_device ON identity (DeviceInfo);