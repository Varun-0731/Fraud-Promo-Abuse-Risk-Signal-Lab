import os

import pandas as pd
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

load_dotenv(find_dotenv(usecwd=True))

url = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:3306/{os.getenv('DB_NAME')}"
)
engine = create_engine(url)

METRICS = [
    "transactions",
    "fraud_rate_pct",
    "tier_flag_rate_pct",
    "avg_amount",
    "avg_forest_score",
]

RISK_METRICS = ["fraud_rate_pct", "tier_flag_rate_pct", "avg_forest_score"]


def daily_metrics():
    df = pd.read_sql(
        "SELECT TransactionDT, TransactionAmt, isFraud, tier_flag, forest_score FROM tx_scored",
        engine,
    )
    df["day"] = df["TransactionDT"] // 86400
    g = df.groupby("day")
    out = pd.DataFrame(
        {
            "transactions": g.size(),
            "fraud_rate_pct": g["isFraud"].mean() * 100,
            "tier_flag_rate_pct": g["tier_flag"].mean() * 100,
            "avg_amount": g["TransactionAmt"].mean(),
            "avg_forest_score": g["forest_score"].mean(),
        }
    )
    return out.round(3)


def add_flags(metrics, window=14, threshold=3.0):
    for c in METRICS:
        base = metrics[c].shift(1).rolling(window)
        metrics[f"{c}_z"] = ((metrics[c] - base.mean()) / base.std()).round(2)
    z_cols = [f"{c}_z" for c in RISK_METRICS]
    metrics["anomaly"] = metrics[z_cols].abs().max(axis=1) >= threshold
    return metrics


if __name__ == "__main__":
    m = add_flags(daily_metrics())
    print(m.tail(10).to_string())
    print(int(m["anomaly"].sum()), "anomalous days out of", len(m))
