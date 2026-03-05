#!/usr/bin/env python3
"""Batch chat completions from a JSON array of prompts.

Usage:
  python examples/batch.py prompts.json
  echo '["Hello", "What is 2+2?"]' | python examples/batch.py -

Outputs one JSON line per prompt with the response and usage stats.
"""

import json
import os
import sys

from openai import OpenAI

LLM_API_BASE = os.environ.get("LLM_API_BASE", "http://localhost:8000/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "sk-local-dev")
LLM_MODEL = os.environ.get("LLM_MODEL", "Llama-3.1-8B-Instruct")


def main():
    if len(sys.argv) < 2:
        print("Usage: batch.py <prompts.json | ->", file=sys.stderr)
        sys.exit(1)

    source = sys.argv[1]
    if source == "-":
        prompts = json.load(sys.stdin)
    else:
        with open(source) as f:
            prompts = json.load(f)

    if not isinstance(prompts, list):
        print("Error: input must be a JSON array of strings", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(base_url=LLM_API_BASE, api_key=LLM_API_KEY)

    for prompt in prompts:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": str(prompt)}],
        )

        result = {
            "prompt": prompt,
            "response": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }
        print(json.dumps(result))


if __name__ == "__main__":
    main()
