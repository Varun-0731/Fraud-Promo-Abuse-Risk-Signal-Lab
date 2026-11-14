import os
import time
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(usecwd=True))

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=30,
    max_retries=0,
)

SKIP = (
    "vision",
    "guard",
    "safety",
    "reward",
    "embed",
    "retriever",
    "rerank",
    "-vl",
    "parse",
    "clip",
    "nemoguard",
    "content-safety",
    "topic-control",
    "whisper",
    "tts",
    "asr",
    "flux",
    "diffusion",
    "cosmos",
    "audio",
    "speech",
)
FAMILIES = (
    "llama",
    "nemotron",
    "mistral",
    "mixtral",
    "qwen",
    "gpt-oss",
    "deepseek",
    "gemma",
    "phi",
    "granite",
    "kimi",
    "glm",
)

names = [m.id for m in client.models.list()]
print(len(names), "models visible to this key")

candidates = [
    n
    for n in names
    if any(f in n.lower() for f in FAMILIES) and not any(s in n.lower() for s in SKIP)
]
candidates.sort(
    key=lambda n: (("llama" not in n.lower() and "nemotron" not in n.lower()), n)
)
print(len(candidates), "candidate text models")

working = []
for name in candidates[:15]:
    start = time.time()
    try:
        client.chat.completions.create(
            model=name,
            messages=[{"role": "user", "content": "Reply with the word ok"}],
            max_tokens=10,
        )
        print("OK  ", round(time.time() - start, 1), "s", name, flush=True)
        working.append(name)
    except Exception as e:
        print("FAIL", name, type(e).__name__, flush=True)

print()
print("working:", working)
