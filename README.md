# Workmind

**Workmind** is an agentic AI data analyst assistant that turns natural-language questions into tool-backed actions. It combines a **FastAPI** backend, **Gemini function calling** (via the `google-genai` SDK), a local **SQLite** database, **YAML-based schema metadata**, and an **Electron + React** desktop frontend.

The system is intentionally **local-first**: data stays on your machine, queries run against a local SQLite file, and table descriptions are human-readable YAML. No cloud data warehouse, no external dashboards — just a conversational interface over your own data.

---

## Features

| Category | Capability |
| --- | --- |
| **Chat** | Multi-turn conversational API with system-prompt injection |
| **LLM Tool Loop** | Gemini function calling with up to 20 tool turns per request |
| **Database** | Local SQLite query execution with structured row/column responses |
| **Schema Awareness** | YAML table descriptions enrich the SQL tool prompt for better query generation |
| **Browser Automation** | `execute_browser_task` tool for web-based actions |
| **Email** | AgentMail integration — list inboxes, threads, messages; send and reply |
| **Research** | Happenstance research tool for information gathering |
| **Voice** | Speech-to-text and text-to-speech via Sarvam AI (STT: Saaras v3, TTS: Bulbul v3) |
| **Streaming** | Server-Sent Events for real-time assistant/tool/done/error updates |
| **WebSocket** | Real-time chat with tool execution hints displayed in the UI |
| **Frontend** | Electron + React + TypeScript desktop app with 3D animated blob, sidebar, voice input |
| **Deployment** | Docker and Docker Compose with health checks, dev profile with hot reload |
| **Metadata CRUD** | REST endpoints to read, create, update, and delete YAML table descriptions |

---

## Project Structure

```text
.
├── main.py                              # FastAPI app — all HTTP, SSE, WebSocket, and voice endpoints
├── functioncalling.py                   # Gemini function-calling loop and content conversion
├── tools.py                             # Tool schema definitions exposed to Gemini
├── router.py                            # Central tool-call dispatcher (function registry)
├── config.py                            # Environment / config loading (ConfigurationManager)
├── prompt.py                            # System prompts (data_analyst, sql_expert)
├── LLMclient.py                         # Gemini client helpers
├── utils.py                             # Response formatting, validation, error helpers
├── yaml_crud.py                         # YAML metadata CRUD endpoints
├── voice_processor.py                   # Sarvam AI speech-to-text and text-to-speech
├── csv_to_sqlite.py                     # Utility to load CSV files into SQLite
│
├── tool/
│   ├── database/
│   │   ├── connector/sqlitedb.py        # SQLite connector — run_query()
│   │   ├── prompt/prompts.py            # YAML-to-prompt builder for SQL tool
│   │   └── tableDescription/            # YAML metadata files
│   │       ├── loan.yaml
│   │       ├── mobile_sales_data.yaml
│   │       └── retail_sales_dataset.yaml
│   ├── browser/automation.py            # Browser automation tool
│   ├── agentmail/mail.py                # AgentMail email operations
│   └── happenstance/research.py         # Happenstance research tool
│
├── ui-electron/                         # Electron + React + TypeScript frontend
│   ├── main.js                          # Electron main process
│   ├── preload.cjs                      # Electron preload script
│   ├── package.json                     # Node dependencies (React 19, Three.js, Lucide, Tailwind v4)
│   └── src/
│       ├── App.tsx                      # Main React app — chat UI, sidebar, voice controls
│       ├── components/Blob.tsx          # Three.js animated 3D blob visual
│       └── services/
│           ├── ChatService.ts           # HTTP/WebSocket chat communication
│           └── VoiceService.ts          # Frontend voice input/output service
│
├── tests/
│   ├── conftest.py                      # Pytest fixtures
│   └── test_functioncalling.py          # Function-calling loop tests
├── test_client.py                       # Standalone HTTP client test
├── test_server.py                       # Server startup test
├── test_ws.py                           # WebSocket client test
│
├── data/
│   └── workmind.db                      # Local SQLite database (~9.3 MB)
├── mobile_sales_data.csv                # Source CSV — mobile/laptop sales (~9 MB)
├── retail_sales_dataset.csv             # Source CSV — retail transactions (~50 KB)
│
├── Dockerfile                           # Python 3.11 slim container
├── docker-compose.yml                   # Production + dev profile services
├── requirements.txt                     # Python dependencies
├── .gitignore
├── .dockerignore
├── CORE_FILES_DOCUMENTATION.md
├── DOCKER_DEPLOYMENT.md
└── YAML_EDITING_DOCUMENTATION.md
```

---

## Requirements

- **Python 3.11+**
- **Node.js 18+** (for the Electron frontend)
- A Gemini API key (`GEMINI_API_KEY` or `GOOGLE_API_KEY`)
- Local SQLite database file (included at `data/workmind.db`)

### Python Dependencies

```text
fastapi
google-genai
pydantic
python-dotenv
PyYAML
uvicorn
agentmail
pytest
```

### Frontend Dependencies

React 19, Three.js, `@react-three/fiber`, `@react-three/drei`, Lucide React, Tailwind CSS v4, Electron 41, Vite 8, TypeScript 6.

---

## Configuration

Create a `.env` file in the project root:

```env
# Required — at least one of these
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_API_KEY=                          # Optional fallback

# LLM settings
DEFAULT_LLM_MODEL=gemini-3-flash-preview
MAX_TOKENS=4000
TEMPERATURE=0.7

# Database
SQLITE_DB_PATH=./data/workmind.db

# Server
HOST=127.0.0.1
PORT=8000
DEBUG=True

# Optional tool credentials
SARVAM_API_KEY=                          # Sarvam AI for voice STT/TTS
AGENTMAIL_API_KEY=                       # AgentMail for email tools
AGENTMAIL_INBOX_ID=                      # Default inbox ID
HAPPENSTANCE_API_KEY=                    # Happenstance for research tool
```

---

## Quick Start

### Backend

```bash
# Create virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS/Linux

pip install -r requirements.txt

# (Optional) Load CSV data into SQLite
python csv_to_sqlite.py

# Start the API server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend (Electron Desktop App)

```bash
cd ui-electron
npm install
npm start                        # Starts Vite dev server + Electron
```

The frontend connects to `http://localhost:8000` for the backend API and `ws://localhost:8000/ws/chat` for WebSocket communication.

### Verify

- **API docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **Frontend**: Electron window opens automatically on `npm start`

---

## Docker

```bash
# Production
docker-compose up -d

# Development (with hot reload on port 8001)
docker-compose --profile dev up -d dev
```

The compose file mounts `./data` into the container at `/app/data` so the SQLite database persists outside the image. Health checks run every 30 seconds against `/health`.

---

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | API metadata and endpoint documentation |
| `GET` | `/health` | Health check (`{"status": "healthy"}`) |
| `POST` | `/chat` | Multi-turn conversation with tool execution |
| `POST` | `/chat/stream` | SSE stream of assistant messages, tool calls, tool results, done, and error events |
| `POST` | `/quick-query` | Single text query shortcut |
| `WebSocket` | `/ws/chat` | Real-time chat with tool execution hints |
| `POST` | `/voice/stt` | Upload audio → text (Sarvam AI Saaras v3) |
| `POST` | `/voice/tts` | Text → audio WAV response (Sarvam AI Bulbul v3) |
| `GET` | `/yaml/` | Read all table-description YAML files |
| `POST` | `/yaml/` | Create, update, or delete YAML files in bulk |

---

## Chat Example

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Which product category generated the highest total sales?"
      }
    ]
  }'
```

### Streaming Chat

```bash
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Show the top 5 brands by revenue"
      }
    ]
  }'
```

SSE event names: `assistant_message`, `tool_call`, `tool_result`, `done`, `error`.

---

## Registered Tools

Tool calls are handled in a Gemini multi-turn loop (up to 20 turns). Gemini requests tools, the server executes them through `router.py`, sends function responses back, and repeats until a final assistant message is produced.

| Category | Tool | Purpose |
| --- | --- | --- |
| **Database** | `execute_sql_query` | Run SQLite queries and return structured results |
| **Browser** | `execute_browser_task` | Automate browser-based tasks |
| **Email** | `agentmail_list_inboxes` | List available email inboxes |
| | `agentmail_list_threads` | List email threads in an inbox |
| | `agentmail_list_messages` | List messages in a thread |
| | `agentmail_search_messages` | Search messages by query |
| | `agentmail_get_message` | Get a specific message |
| | `agentmail_send_message` | Send a new email |
| | `agentmail_reply_to_message` | Reply to an existing message |
| **Research** | `happenstance_research` | Conduct research on a topic |

---

## Table Metadata (YAML)

YAML files in `tool/database/tableDescription/` describe the tables available to the assistant. These are loaded into the SQL tool prompt so Gemini can write better, schema-aware SQLite queries.

```yaml
# Example: loan.yaml
table_id: loan
dataset_id: local
table_description: SQLite table containing loan application data.
headers:
  application_key: Unique ID of the loan application
  Loan_Amount: Principal loan amount granted
  industry: Industry classification of borrower or company
```

### Included Datasets

| Dataset | Table Name | Description | Size |
| --- | --- | --- | --- |
| Mobile Sales | `mobile_sales_data` | Product, brand, price, inventory/dispatch dates, quantity, customer location, device specs | ~9 MB |
| Retail Sales | `retail_sales_dataset` | Transaction ID, date, customer demographics, product category, quantity, pricing | ~50 KB |
| Loan Originations | `loan` | Application data — salary, loan amount, tenure, interest rate, DTI, risk score, industry | via YAML |

### Loading CSV Data

```bash
python csv_to_sqlite.py
```

This recreates the SQLite tables from the included CSV files (`mobile_sales_data.csv`, `retail_sales_dataset.csv`).

### YAML CRUD API

```bash
# Read all table descriptions
curl http://localhost:8000/yaml/

# Update or create a YAML file
curl -X POST http://localhost:8000/yaml/ \
  -H "Content-Type: application/json" \
  -d '{
    "files": {
      "loan.yaml": {
        "table_id": "loan",
        "dataset_id": "local",
        "table_description": "Loan application data.",
        "headers": {
          "application_key": "Unique loan application ID",
          "Loan_Amount": "Principal loan amount"
        }
      }
    }
  }'

# Delete a YAML file (pass null)
curl -X POST http://localhost:8000/yaml/ \
  -H "Content-Type: application/json" \
  -d '{"files": {"old_table.yaml": null}}'
```

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────┐
│  Electron + React Frontend (ui-electron/)                        │
│  ┌─────────┐  ┌──────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │ Chat UI │  │ 3D Blob  │  │ Voice Input │  │ Tool Hints   │  │
│  └────┬────┘  └──────────┘  └──────┬──────┘  └──────────────┘  │
│       │ HTTP / WebSocket            │ /voice/stt, /voice/tts    │
└───────┼─────────────────────────────┼───────────────────────────┘
        │                             │
┌───────▼─────────────────────────────▼───────────────────────────┐
│  FastAPI Backend (main.py)                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  /chat  │  /chat/stream  │  /ws/chat  │  /quick-query   │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                          │
│  ┌────────────────────▼─────────────────────────────────────┐   │
│  │  Gemini Function-Calling Loop (functioncalling.py)        │   │
│  │  System Prompt (prompt.py) + Tool Schemas (tools.py)      │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                          │
│  ┌────────────────────▼─────────────────────────────────────┐   │
│  │  Tool Router (router.py)                                  │   │
│  │  ┌──────────┐ ┌─────────┐ ┌───────────┐ ┌────────────┐  │   │
│  │  │ SQLite   │ │ Browser │ │ AgentMail │ │Happenstance│  │   │
│  │  │ Database │ │  Auto   │ │   Email   │ │  Research  │  │   │
│  │  └──────────┘ └─────────┘ └───────────┘ └────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  YAML Metadata Layer (tool/database/tableDescription/)    │   │
│  │  Schema-aware prompting for better SQL generation         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SQLite Database (data/workmind.db)                       │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Testing

```bash
# Unit tests
pytest tests/

# Standalone test scripts
python test_client.py          # HTTP chat test
python test_server.py          # Server startup test
python test_ws.py              # WebSocket test
```

---

## Removed Capabilities

The following older features were removed from the project:

- Google BigQuery query and upload code
- Slack bot integration and `/slack/events`
- Watchdog / restart-on-YAML-update behavior
- Chart, graph, and image generation tools
- Tool-output image simplification and inbound message sanitizing

---

## Troubleshooting

| Problem | Solution |
| --- | --- |
| `Missing required environment variables: GEMINI_API_KEY or GOOGLE_API_KEY` | Add Gemini credentials to `.env` |
| `SQLite database not found` | Run `python csv_to_sqlite.py` or update `SQLITE_DB_PATH` |
| `/chat` fails on LLM calls | Verify `GEMINI_API_KEY` and `DEFAULT_LLM_MODEL` are valid |
| SQL returns no rows | Check that table names and columns in SQLite match the YAML metadata |
| Voice endpoints return errors | Ensure `SARVAM_API_KEY` is set in `.env` |
| Electron app can't connect | Start the backend first (`uvicorn main:app`) on port 8000 |
| AgentMail tools fail | Set `AGENTMAIL_API_KEY` in `.env` |

---

## License

See `tool/licence.txt` for tool-specific licensing information.
