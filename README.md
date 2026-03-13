# Single-Agent Delivery Status Assistant (Ollama)

A Python FastAPI implementation of the workflow you described:

1. Query submission and evaluation
2. Knowledge source selection:
   - Order management database (SQLite)
   - Shipping provider API (real-time, with mock provider included)
   - Optional web context for local conditions
3. Data integration and LLM synthesis through `ollama3:latest`
4. Actionable output generation

## Project Structure

- `app/main.py` - FastAPI app entrypoint
- `app/workflow.py` - single-agent orchestration logic
- `app/services/order_db.py` - order database setup + lookup
- `app/services/shipping_api.py` - shipping provider integration
- `app/services/web_context.py` - optional weather/logistics context
- `app/services/llm_ollama.py` - Ollama `/api/chat` integration
- `scripts/mock_shipping_provider.py` - local mock shipping API

## Prerequisites

- Python 3.11+
- Ollama installed and running
- Model pulled in Ollama:

```bash
ollama pull ollama3:latest
```

## Setup

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

## One-Terminal Run (Recommended)

From the project directory:

```bash
./run_agent.sh
```

This single command will:

1. Ensure Ollama is running
2. Ensure `ollama3:latest` is present (pulls it if missing)
3. Start the mock shipping API on `127.0.0.1:8001`
4. Start the delivery-status assistant on `127.0.0.1:8000`

Stop everything with `Ctrl+C`.

## Run

Terminal 1 (mock shipping provider):

```bash
uvicorn scripts.mock_shipping_provider:app --host 0.0.0.0 --port 8001 --reload
```

Terminal 2 (delivery status assistant):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Test with your prompt

```bash
curl -X POST http://localhost:8000/delivery-status \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ORDER-1001",
    "query": "Can you tell me the delivery status of my order?"
  }'
```

Example integrated response:

"Your package is currently in transit and expected to arrive tomorrow evening. The live tracking from UPS indicates it is at the regional distribution center."

## Notes

- If the shipping provider API is down, the app uses safe fallback tracking data.
- If Ollama is unavailable, the app returns a deterministic fallback response.
- Toggle optional web context with `ENABLE_WEB_CONTEXT=true|false`.
