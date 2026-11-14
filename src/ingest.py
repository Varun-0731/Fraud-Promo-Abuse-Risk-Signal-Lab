import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

url = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:3306/{os.getenv('DB_NAME')}"
)
engine = create_engine(url)

TX_COLS = [
    "TransactionID",
    "isFraud",
    "TransactionDT",
    "TransactionAmt",
    "ProductCD",
    "card1",
    "card2",
    "card3",
    "card4",
    "card5",
    "card6",
    "addr1",
    "addr2",
    "dist1",
    "P_emaildomain",
    "R_emaildomain",
    "C1",
    "C2",
    "C5",
    "C13",
    "D1",
    "D15",
]
ID_COLS = ["TransactionID", "DeviceType", "DeviceInfo", "id_30", "id_31", "id_33"]


def load(csv_path, table, cols, chunk=50000):
    total = 0
    for part in pd.read_csv(csv_path, usecols=cols, chunksize=chunk):
        part.to_sql(
            table,
            engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=2000,
        )
        total += len(part)
        print(f"{table}: {total} rows loaded")


if __name__ == "__main__":
    load("data/train_transaction.csv", "transactions", TX_COLS)
    load("data/train_identity.csv", "identity", ID_COLS)
