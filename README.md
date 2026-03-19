# chitchat_api

FastAPI **hybrid chatbot** API with 2 modes (chitchat + document QA):

- **Chat** (chitchat): generates a conversational reply using a Hugging Face seq2seq model.
- **QA** (document question answering): uses Haystack + Elasticsearch to answer by extracting text from files in `context/`.

The API exposes a single endpoint: `GET /chat`.

---

## Impact

What this project is useful for:

- Turn a folder of Thai text files (`context/`) into a searchable Q&A assistant (extractive QA) that can answer questions with short, grounded snippets.
- Provide a simple “one endpoint” API that is easy to integrate into other apps (web, LINE bot, internal tools).
- Make QA experiments reproducible with CLI + batch runner (you can measure answer latency and iterate on settings like `top_k` / `QA_THRESHOLD`).
- Demonstrate a practical hybrid chatbot pattern: route between chitchat and document QA, depending on the user intent.

---

## Requirements

- Windows/macOS/Linux
- Python 3.10+ (recommended: 3.11)
- (For QA mode) Docker Desktop **or** a running Elasticsearch 7.x instance

---

## Quick start (local run)

### 1) Create & activate a virtualenv

```powershell
cd d:\chitchat\chitchat_api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

Chat-only:

```powershell
python -m pip install -r requirements.txt
```

Enable QA:

```powershell
python -m pip install -r requirements-qa.txt
```

> Notes
> - First run may download models from Hugging Face.
> - `farm-haystack` (1.x) requires a compatible `transformers` version (pinned in `requirements-qa.txt`).

### 3) Start Elasticsearch (QA mode)

Using Docker (recommended):

```powershell
docker compose up -d elasticsearch
```

Verify:

- Open `http://127.0.0.1:9200` (should return JSON)

### 4) Run the API

```powershell
$env:ELASTICSEARCH_HOST='127.0.0.1'
$env:ELASTICSEARCH_PORT='9200'
$env:ELASTICSEARCH_INDEX='once'

python -m uvicorn bot_api:app --host 127.0.0.1 --port 3001
```

You should see `preparing qa model ok` when QA is enabled.

---

## Docker (optional)

This repo contains a `docker-compose.yml` that starts:

- `elasticsearch` on `9200`
- `web` (API) on `3000`

```powershell
docker compose up --build
```

> Note: the compose file contains `runtime: nvidia` for the API container. If you are not using NVIDIA Container Toolkit / GPU support, you may prefer running the API locally and only Elasticsearch in Docker.

---

## API usage

### Endpoint

`GET /chat`

Query params:

- `line` (**required**): user message
- `mode` (optional): `chat` | `qa` | `auto`
  - `chat`: force chitchat
  - `qa`: force document QA
  - `auto`: let the classifier decide (default)
- `reset` (optional): `true` to clear server-side chat history
- `ret_tk` (optional, QA): retriever `top_k` (default: 3)
- `red_tk` (optional, QA): reader `top_k` (default: 1)

Response:

- Plain text answer
- Returns `ไม่พบคำตอบ` if QA cannot find a confident answer

### Examples

In PowerShell, `curl` is often an alias for `Invoke-WebRequest`. Prefer `curl.exe`:

```powershell
curl.exe -G "http://127.0.0.1:3001/chat" --data-urlencode "line=สวัสดี" --data-urlencode "mode=chat"
curl.exe -G "http://127.0.0.1:3001/chat" --data-urlencode "line=กระทรวงพาณิชย์ ให้ข้อมูลเกี่ยวกับอะไร" --data-urlencode "mode=qa" --data-urlencode "reset=true"
```

---

## CLI chat (interactive)

A simple interactive client that lets you type continuously (like a chat app):

```powershell
python .\scripts\chat_cli.py --base-url http://127.0.0.1:3001 --reset-on-start
```

Inside the CLI:

- `/mode qa` – document QA
- `/mode chat` – chitchat
- `/mode auto` – classifier decides
- `/reset` – clear history
- `/exit` – quit

### Example session

```text
Connected to http://127.0.0.1:3001 (mode=qa)
Type your message. Use /help for commands.
> ก.ล.ต. เกี่ยวข้องกับอะไรบ้าง
การออกและการเสนอขายหลักทรัพย์, หนังสือชี้ชวน, งบการเงิน
> กองทุนรวมคืออะไร
กองทุนรวมคือ ...
> /mode chat
(ok) mode=chat
> สวัสดี
สวัสดี
> /exit
bye
```

---

## Batch run (generate results CSV)

Runs `small_bot_test.csv` against your running API and writes `id,answer,time`:

```powershell
python .\scripts\run_small_bot_test.py --input .\small_bot_test.csv --output .\small_bot_result.csv --base-url http://127.0.0.1:3001
```

---

## Configuration

Environment variables:

- `DISABLE_QA` = `1|true|yes` to disable QA imports and force chat
- `ELASTICSEARCH_HOST` (default: `127.0.0.1`)
- `ELASTICSEARCH_PORT` (default: `9200`)
- `ELASTICSEARCH_INDEX` (default: `once`)
- `QA_RETRIEVER` = `bm25` (default) or `embedding`
- `QA_THRESHOLD` (default: `0.10`)
- `QA_USE_GPU` = `1|true|yes` to allow GPU for the reader if CUDA is available

---

## Troubleshooting

### Port already in use

If `3000`/`3001` is busy, pick another port:

```powershell
python -m uvicorn bot_api:app --host 127.0.0.1 --port 3002
```

### QA disabled: Elasticsearch connection failed

- Ensure Elasticsearch is running at `http://127.0.0.1:9200`
- Ensure you set:
  - `ELASTICSEARCH_HOST=127.0.0.1`
  - `ELASTICSEARCH_PORT=9200`

### PowerShell `curl` issues

Use `curl.exe` explicitly (PowerShell aliases `curl` to `Invoke-WebRequest`).
