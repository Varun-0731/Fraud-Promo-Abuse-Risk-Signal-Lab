import os

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(usecwd=True))

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=60,
    max_retries=0,
)

models = [
    os.getenv("NVIDIA_MODEL"),
    "nvidia/nemotron-3.5-bolt-e4b",
]
variants = {
    "plain": {},
    "thinking_off": {
        "extra_body": {"chat_template_kwargs": {"enable_thinking": False}}
    },
}
prompt = "Write one sentence about fraud monitoring."

for model in dict.fromkeys(models):
    for label, extra in variants.items():
        print("=" * 60)
        print("model:", model, "| variant:", label)
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                **extra,
            )
            choice = resp.choices[0]
            data = choice.message.model_dump()
            print("finish_reason:", choice.finish_reason)
            print("content:", repr(choice.message.content)[:300])
            for k, v in data.items():
                if k != "content" and v:
                    print("extra field", k, ":", repr(v)[:200])
            print("completion_tokens:", resp.usage.completion_tokens)
        except Exception as e:
            print("error:", type(e).__name__, str(e)[:200])
