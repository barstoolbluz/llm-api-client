# llm-api-client

Lightweight client environment for any OpenAI-compatible API server. Powered by [Flox](https://flox.dev).

Works with vLLM, llama.cpp, Ollama, TGI, LMStudio, and anything else that speaks the OpenAI protocol.

## Quick start

```bash
flox activate

# Verify server connectivity
llm-test

# Interactive chat
llm-chat

# One-shot examples
python examples/chat.py "What is the capital of France?"
python examples/streaming.py "Explain quantum computing"
echo '["Hello", "What is 2+2?"]' | python examples/batch.py -
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `LLM_API_BASE` | `http://localhost:8000/v1` | API server endpoint |
| `LLM_API_KEY` | `sk-local-dev` | API key for authentication |
| `LLM_MODEL` | `Llama-3.1-8B-Instruct` | Model name for completions |
| `LLM_SYSTEM_PROMPT` | `You are a helpful assistant.` | Default system prompt for `llm-chat` |

Override at activation time:

```bash
LLM_API_BASE=http://gpu-server:8000/v1 LLM_MODEL=Mixtral-8x7B flox activate
```

## Tools

### `llm-test` — health check, smoke test, benchmark

```bash
llm-test                                    # health + smoke (pass/fail, exit 0/1)
llm-test bench                              # benchmark (10 requests, concurrency 1)
llm-test bench -n 50 --concurrent 5         # heavier load test
llm-test bench --prompt "..." --max-tokens 256
```

- **Health check** — calls `models.list()`, reports available models, checks if `LLM_MODEL` exists
- **Smoke test** — non-streaming + streaming completion, reports latency and TTFT
- **Benchmark** — concurrent streaming requests with p50/p90/p99 for TTFT, latency, and inter-token latency (ITL); aggregate throughput. Uses `stream_options` for accurate token counts when the server supports it, falls back to chunk counting otherwise

### `llm-chat` — interactive REPL

Uses streaming API and renders responses as markdown.

| Command | Description |
|---|---|
| `/clear` | Clear conversation history |
| `/model [name]` | Show or change the model |
| `/system [prompt]` | Show or change the system prompt |
| `/help` | Show available commands |
| `/quit`, `/exit` | Exit |

## Example scripts

- **`examples/chat.py`** — Single chat completion, prints the response.
- **`examples/streaming.py`** — Streaming chat completion, prints tokens as they arrive.
- **`examples/batch.py`** — Reads a JSON array of prompts from a file or stdin, outputs one JSON line per response with usage stats.

## Supported backends

Any server that implements the OpenAI chat completions API:

- [vLLM](https://github.com/vllm-project/vllm)
- [llama.cpp](https://github.com/ggerganov/llama.cpp) (server mode)
- [Ollama](https://ollama.com)
- [TGI](https://github.com/huggingface/text-generation-inference)
- [LMStudio](https://lmstudio.ai)
- [LocalAI](https://localai.io)
- OpenAI itself

## File structure

```
llm-api-client/
  .flox/
    env.json                 # Flox environment metadata
    env/manifest.toml        # Flox environment (python312, uv, env vars, venv)
  llm-chat                   # Interactive chat REPL
  llm-test                   # Health check, smoke test, benchmark
  examples/
    chat.py                  # Simple chat completion
    streaming.py             # Streaming example
    batch.py                 # Batch completions from JSON
  FLOX.md                    # Flox reference documentation
  README.md
```
