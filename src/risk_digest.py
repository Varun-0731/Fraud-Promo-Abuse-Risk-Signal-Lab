import json
import os
import re
import sys
import time

from dotenv import find_dotenv, load_dotenv
from openai import AuthenticationError, NotFoundError, OpenAI, PermissionDeniedError

from risk_metrics import METRICS, RISK_METRICS, add_flags, daily_metrics

load_dotenv(find_dotenv(usecwd=True))

PROMPT = """You are a Trust and Safety analytics assistant writing a daily risk note for an analyst.
Write exactly 3 sentences in plain English, with no quotation marks, no bullet points and no preamble.
Sentence 1: name the risk metric with the largest absolute z_score, give its value and its 14-day baseline and its z_score, and say whether it is above or below baseline.
Sentence 2: give the other two risk metrics with their values and baselines, and say whether each is within the normal range. A z_score between -2 and 2 is normal.
Sentence 3: say whether the day needs analyst attention. It does if any risk metric has an absolute z_score of 3 or more, otherwise it does not.
The risk metrics are fraud_rate_pct, tier_flag_rate_pct and avg_forest_score.
transactions and avg_amount are context only, so mention them only if their absolute z_score is 2 or more.
Use only numbers that appear in the data, copied exactly. Do not invent causes.
Data:
{data}
"""


def build_payload(m, day):
    row = m.loc[day]
    prior = m.loc[day - 14 : day - 1]
    items = []
    for c in METRICS:
        items.append(
            {
                "metric": c,
                "value": round(float(row[c]), 3),
                "baseline_14d_avg": round(float(prior[c].mean()), 3),
                "z_score": round(float(row[f"{c}_z"]), 2),
            }
        )
    return {"day": int(day), "anomaly": bool(row["anomaly"]), "metrics": items}


def allowed_numbers(payload):
    nums = {float(payload["day"]), 14.0}
    nums.update(float(i) for i in range(6))
    for item in payload["metrics"]:
        for key in ("value", "baseline_14d_avg", "z_score"):
            nums.add(abs(float(item[key])))
    return nums


def numbers_ok(text, payload):
    allowed = allowed_numbers(payload)
    found = re.findall(r"\d+(?:\.\d+)?", text)
    return all(any(abs(float(f) - a) < 0.0005 for a in allowed) for f in found)


def clean(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()


def fallback(payload):
    hits = [
        i
        for i in payload["metrics"]
        if i["metric"] in RISK_METRICS and abs(i["z_score"]) >= 3
    ]
    if not hits:
        return f"Day {payload['day']}: no risk metric moved 3 or more standard deviations from its 14-day baseline."
    parts = [
        f"{i['metric']} was {i['value']} against a baseline of {i['baseline_14d_avg']} (z {i['z_score']})"
        for i in hits
    ]
    return f"Day {payload['day']}: " + "; ".join(parts) + "."


def generate(client, model, prompt, attempts=3):
    for i in range(attempts):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2000,
            )
            content = resp.choices[0].message.content
            if content:
                cleaned = clean(content)
                if cleaned:
                    return cleaned
            print(f"attempt {i + 1} returned an empty reply", flush=True)
        except (AuthenticationError, NotFoundError, PermissionDeniedError):
            raise
        except Exception as e:
            print(f"attempt {i + 1} failed: {type(e).__name__}", flush=True)
        time.sleep(2**i * 2)
    return None


def summarise(payload):
    api_key = os.getenv("NVIDIA_API_KEY")
    model = os.getenv("NVIDIA_MODEL")
    if not api_key or not model:
        return fallback(
            payload
        ), "template fallback, NVIDIA_API_KEY or NVIDIA_MODEL missing in .env"
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
        timeout=30,
        max_retries=0,
    )
    prompt = PROMPT.format(data=json.dumps(payload, indent=2))
    print("calling NVIDIA NIM...", flush=True)
    for _ in range(2):
        text = generate(client, model, prompt)
        if text is None:
            return fallback(
                payload
            ), "template fallback, NVIDIA service unavailable or empty replies"
        if numbers_ok(text, payload):
            return text, "nvidia nim, numbers verified"
    return fallback(payload), "template fallback, model numbers did not match the data"


def main():
    m = add_flags(daily_metrics())
    if len(sys.argv) > 1:
        day = int(sys.argv[1])
    else:
        flagged = m.index[m["anomaly"]]
        day = int(flagged[-1]) if len(flagged) else int(m.index[-1])
    payload = build_payload(m, day)
    summary, source = summarise(payload)
    print(json.dumps(payload, indent=2))
    print()
    print(summary)
    print()
    print("source:", source)


if __name__ == "__main__":
    main()
