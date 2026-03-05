# llm-api-client

Lightweight client environment for any OpenAI-compatible API server. Powered by [Flox](https://flox.dev).

Works with [vLLM](https://github.com/vllm-project/vllm), [llama.cpp](https://github.com/ggerganov/llama.cpp), [Ollama](https://ollama.com), [TGI](https://github.com/huggingface/text-generation-inference), [LMStudio](https://lmstudio.ai), [LocalAI](https://localai.io), OpenAI itself, and anything else that speaks the OpenAI protocol.

Provides an interactive chat REPL (`llm-chat`), a health/smoke/benchmark tool (`llm-test`), and example scripts -- everything needed to develop against an OpenAI-compatible server without installing dependencies globally.

## What's in the environment

| Component | Description |
|-----------|-------------|
| `llm-chat` | Interactive multi-turn chat REPL with streaming and markdown rendering |
| `llm-test` | Health check, smoke test, and benchmark tool with percentile metrics |
| `examples/` | Chat, streaming, and batch completion scripts |

## Quick start

```bash
cd ~/dev/llm-api-client
flox activate

# ── Verify connectivity ──────────────────────────────────────────────
llm-test

# ── Interactive chat ─────────────────────────────────────────────────
llm-chat

# ── Override model per-command ───────────────────────────────────────
LLM_MODEL=Mixtral-8x7B llm-chat

# ── Example scripts ──────────────────────────────────────────────────
python examples/chat.py "What is the capital of France?"
python examples/streaming.py "Explain quantum computing"
echo '["Hello", "What is 2+2?"]' | python examples/batch.py -

# ── Benchmark ────────────────────────────────────────────────────────
llm-test bench
llm-test bench -n 50 --concurrent 5
llm-test bench --prompt "Summarize the theory of relativity" --max-tokens 256
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_API_BASE` | `http://localhost:8000/v1` | API server endpoint |
| `LLM_API_KEY` | `sk-local-dev` | API key for authentication |
| `LLM_MODEL` | `Llama-3.1-8B-Instruct` | Model name for completions |
| `LLM_SYSTEM_PROMPT` | `You are a helpful assistant.` | Default system prompt for `llm-chat` |

The Flox `on-activate` hook maps `LLM_API_BASE` to `OPENAI_BASE_URL` and `LLM_API_KEY` to `OPENAI_API_KEY`, so the OpenAI Python SDK works automatically. All variables use `${VAR:-default}` fallbacks and can be overridden at activation time or per-command.

```bash
# Override at activation time (persists for session)
LLM_API_BASE=http://gpu-server:8000/v1 LLM_MODEL=Mixtral-8x7B flox activate

# Override per-command
LLM_MODEL=Mixtral-8x7B python examples/chat.py "Hello"
```

## Chat CLI

`llm-chat` is an interactive REPL that streams chat completions and renders output as markdown using [Rich](https://github.com/Textualize/rich). Conversation context is maintained across turns until cleared or the session ends.

### Commands

| Command | Description |
|---------|-------------|
| `/clear` | Clear conversation history and start fresh |
| `/model [name]` | Show current model, or switch to a different model |
| `/system [prompt]` | Show current system prompt, or set a new one |
| `/help` | Show available commands |
| `/quit` | Exit the chat (also: `/exit`, Ctrl+C, Ctrl+D) |

### Example session

```
$ llm-chat
llm-chat connected to http://localhost:8000/v1
Model: Llama-3.1-8B-Instruct
Type /help for commands, /quit to exit.

you> What is 2 + 2?

2 + 2 = 4.

you> And if you multiply that by 3?

4 multiplied by 3 is 12.

you> /model Mixtral-8x7B
Model set to Mixtral-8x7B

you> /quit
Bye!
```

## Test CLI

`llm-test` checks server connectivity, runs smoke tests, and benchmarks throughput against any OpenAI-compatible server.

### Usage

```bash
# Health check + smoke test (exit 0 on success, 1 on failure)
llm-test

# Benchmark with defaults (10 requests, concurrency 1)
llm-test bench

# Heavier load test
llm-test bench -n 50 --concurrent 5 --max-tokens 256

# Custom prompt
llm-test bench --prompt "Summarize the theory of relativity"
```

### What it tests

| Check | Description |
|-------|-------------|
| **Health** | Connects to server, lists available models, verifies `LLM_MODEL` exists |
| **stream_options probe** | Tests whether the server supports `stream_options: {include_usage: true}` for accurate token counts |
| **Smoke (non-streaming)** | Single completion, reports latency and token count |
| **Smoke (streaming)** | Streaming completion, reports TTFT and token count |
| **Benchmark** | Concurrent streaming requests with p50/p90/p99 percentiles, aggregate throughput |

### Metrics

| Metric | Definition |
|--------|------------|
| **TTFT** | Time to first token -- seconds from request start to first content chunk |
| **Latency** | Total request duration from start to final chunk |
| **ITL** | Inter-token latency -- average time between consecutive content chunks |
| **Tokens/sec** | Completion tokens divided by total latency (per-request and aggregate) |

### stream_options auto-detection

Before running smoke tests or benchmarks, `llm-test` sends a probe request with `stream_options: {"include_usage": true}`. If the server supports it (vLLM, OpenAI), subsequent requests include this option and report server-reported token counts. If the probe returns a `BadRequestError` (llama.cpp, Ollama, older servers), `llm-test` falls back to counting content chunks as an approximation. This happens automatically -- no configuration needed.

## Example scripts

| Script | Description |
|--------|-------------|
| `examples/chat.py` | Single chat completion (non-streaming), prints the response |
| `examples/streaming.py` | Streaming chat completion, prints tokens as they arrive |
| `examples/batch.py` | Batch completions from a JSON array, outputs one JSON line per response with usage stats |

`batch.py` reads a JSON array of prompt strings from a file or stdin:

```bash
python examples/batch.py prompts.json
echo '["Hello", "What is 2+2?"]' | python examples/batch.py -
```

## Supported backends

Any server that implements the OpenAI chat completions API:

- [vLLM](https://github.com/vllm-project/vllm)
- [llama.cpp](https://github.com/ggerganov/llama.cpp) (server mode)
- [Ollama](https://ollama.com)
- [TGI](https://github.com/huggingface/text-generation-inference)
- [LMStudio](https://lmstudio.ai)
- [LocalAI](https://localai.io)
- OpenAI itself

Works with any server implementing `/v1/chat/completions` and `/v1/models` because it uses the standard `openai` Python SDK.

## Flox environment details

### Installed packages

| Package | Purpose |
|---------|---------|
| `python312` | Python 3.12 interpreter |
| `uv` | Fast Python package installer (creates venv, installs pip packages) |

No native C libraries needed -- `openai` and `rich` are pure Python.

### Pip packages (installed in venv on first activation)

| Package | Purpose |
|---------|---------|
| `openai` | OpenAI Python SDK for chat completions, streaming, and model listing |
| `rich` | Terminal markdown rendering for `llm-chat` and table formatting for `llm-test` |

### Activation behavior

On `flox activate`:

1. Sets `LLM_API_BASE`, `LLM_API_KEY`, `LLM_MODEL`, and `LLM_SYSTEM_PROMPT` with fallback defaults
2. Maps `LLM_API_BASE` to `OPENAI_BASE_URL` and `LLM_API_KEY` to `OPENAI_API_KEY` so the OpenAI SDK works automatically
3. Creates a Python venv in `$FLOX_ENV_CACHE/venv` using `uv` (if it doesn't exist) and activates it
4. Installs pip packages on first activation (skips if `$VENV/.installed` marker exists)
5. Adds the project root and venv `bin/` to `PATH` so `llm-chat` and `llm-test` are available as commands

### Clean reinstall

To force a clean reinstall of pip packages:

```bash
rm -rf .flox/cache/venv
flox activate
```

## Troubleshooting

### Connection refused

The server is not running at `LLM_API_BASE` (default `http://localhost:8000/v1`). Verify it's reachable:

```bash
curl http://localhost:8000/v1/models
```

If on a different host or port:

```bash
export LLM_API_BASE=http://gpu-server:8000/v1
```

### Model not found

`llm-test` will warn if `LLM_MODEL` doesn't match any model on the server. Set it to match your server's model name:

```bash
export LLM_MODEL=my-model-name
# or per-command
LLM_MODEL=my-model-name llm-chat
```

### Authentication errors

Some servers require an API key. Set `LLM_API_KEY` to match your server's expected key:

```bash
export LLM_API_KEY=your-key-here
```

To use OpenAI's hosted API as the backend:

```bash
LLM_API_BASE=https://api.openai.com/v1 LLM_API_KEY=sk-... LLM_MODEL=gpt-4o llm-chat
```

### Pip packages missing or broken

If imports fail or packages are out of date, force a clean venv reinstall:

```bash
rm -rf .flox/cache/venv
flox activate
```

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

## Related documentation

- [OpenAI Python SDK](https://github.com/openai/openai-python) -- Client library used by all tools and examples
- [OpenAI API Reference -- Chat Completions](https://platform.openai.com/docs/api-reference/chat) -- The API endpoint this project targets
- [vLLM](https://github.com/vllm-project/vllm) -- Most common backend for this tool
- [Flox](https://flox.dev) -- Environment manager powering this project
- [Rich](https://github.com/Textualize/rich) -- Terminal rendering library used by `llm-chat` and `llm-test`
