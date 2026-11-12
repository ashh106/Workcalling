# Core Files Documentation

## Runtime

- `main.py`: FastAPI app, chat endpoints, system prompt injection, and tool-calling loop.
- `functioncalling.py`: Gemini function-calling loop, tool schema adapter, and available tool list.
- `router.py`: Maps tool-call names to local Python implementations.
- `tools.py`: Function schema exposed to the LLM. The only runtime tool is `execute_sql_query`.
- `LLMclient.py`: Gemini client construction.
- `config.py`: Environment and application settings.
- `utils.py`: Shared response formatting and validation helpers.
- `yaml_crud.py`: YAML table-description CRUD endpoints.

## Database

- `tool/database/connector/sqlitedb.py`: Executes SQL against the local SQLite database configured by `SQLITE_DB_PATH`.
- `tool/database/prompt/prompts.py`: Builds schema context from YAML table descriptions.
- `tool/database/tableDescription/*.yaml`: Local table metadata used in the SQL tool description.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | API metadata |
| GET | `/health` | Health check |
| POST | `/chat` | Multi-message assistant conversation |
| POST | `/chat/stream` | Multi-message conversation streamed as complete SSE events |
| POST | `/quick-query` | Single text query shortcut |
| GET | `/yaml/` | Read all YAML table descriptions |
| POST | `/yaml/` | Replace, add, or delete YAML table descriptions |

## Configuration

| Variable | Purpose |
| --- | --- |
| `GEMINI_API_KEY` | Gemini API key |
| `GOOGLE_API_KEY` | Optional fallback Gemini API key name |
| `DEFAULT_LLM_MODEL` | Gemini model name; defaults to `gemini-3-flash-preview` |
| `SQLITE_DB_PATH` | Local SQLite database path; defaults to `./data/workmind.db` |
| `DEBUG` | Enables debug mode |
| `HOST` | Server host |
| `PORT` | Server port |

## Removed Capabilities

The app no longer includes external warehouse connectors, messaging-platform bot endpoints, automatic reload/watch behavior, rendering tools, or inbound message sanitizing before validation.
