#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

VENV_PY="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$VENV_PY" ]]; then
  echo "Error: virtual environment not found at .venv/."
  echo "Create it first, then install deps: python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt"
  exit 1
fi

cleanup() {
  if [[ -n "${MOCK_PID:-}" ]] && kill -0 "$MOCK_PID" 2>/dev/null; then
    kill "$MOCK_PID" 2>/dev/null || true
  fi
  if [[ -n "${OLLAMA_PID:-}" ]] && kill -0 "$OLLAMA_PID" 2>/dev/null; then
    kill "$OLLAMA_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

is_port_busy() {
  local port="$1"
  lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
}

echo "[1/4] Checking Ollama..."
if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "Ollama already running on :11434"
else
  if ! command -v ollama >/dev/null 2>&1; then
    echo "Error: 'ollama' command not found. Install Ollama first."
    exit 1
  fi

  echo "Starting Ollama in background..."
  ollama serve >/tmp/ollama-agent.log 2>&1 &
  OLLAMA_PID=$!

  for _ in {1..30}; do
    if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
      echo "Ollama is ready."
      break
    fi
    sleep 1
  done

  if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "Error: Ollama did not become ready. Check /tmp/ollama-agent.log"
    exit 1
  fi
fi

echo "[2/4] Ensuring model llama3:latest is available..."
if ! ollama list | grep -q "^llama3:latest"; then
  echo "Model not found locally. Pulling llama3:latest..."
  ollama pull llama3:latest
fi

echo "[3/4] Starting mock shipping provider on :8001..."
if is_port_busy 8001; then
  echo "Port 8001 is already in use. Stop existing process or change port."
  exit 1
fi
"$VENV_PY" -m uvicorn scripts.mock_shipping_provider:app --host 127.0.0.1 --port 8001 >/tmp/mock-shipping.log 2>&1 &
MOCK_PID=$!

for _ in {1..20}; do
  if curl -fsS http://127.0.0.1:8001/docs >/dev/null 2>&1; then
    echo "Mock shipping provider is ready."
    break
  fi
  sleep 1
done

if ! curl -fsS http://127.0.0.1:8001/docs >/dev/null 2>&1; then
  echo "Error: mock shipping provider failed to start. Check /tmp/mock-shipping.log"
  exit 1
fi

echo "[4/4] Starting delivery status agent on :8000..."
if is_port_busy 8000; then
  echo "Port 8000 is already in use. Stop existing process or run with a different port."
  exit 1
fi
exec "$VENV_PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
