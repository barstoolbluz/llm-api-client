#!/usr/bin/env python3
"""Simple chat completion against an OpenAI-compatible API server."""

import os
import sys

from openai import OpenAI

LLM_API_BASE = os.environ.get("LLM_API_BASE", "http://localhost:8000/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "sk-local-dev")
LLM_MODEL = os.environ.get("LLM_MODEL", "Llama-3.1-8B-Instruct")

prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello!"

client = OpenAI(base_url=LLM_API_BASE, api_key=LLM_API_KEY)

response = client.chat.completions.create(
    model=LLM_MODEL,
    messages=[{"role": "user", "content": prompt}],
)

print(response.choices[0].message.content)
