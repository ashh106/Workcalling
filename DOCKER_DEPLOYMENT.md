# Docker Deployment

This project runs as a FastAPI service with a local SQLite database.

## Environment

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
DEFAULT_LLM_MODEL=gemini-3-flash-preview
SQLITE_DB_PATH=/app/data/workmind.db
DEBUG=True
```

## Start

```bash
docker-compose up -d
```

The API is exposed at `http://localhost:8000`.

## Data

By default, Compose mounts `./data` to `/app/data`. Put your SQLite database at `./data/workmind.db`, or set `SQLITE_DB_PATH` to the mounted file you want to use.

## Development

```bash
docker-compose --profile dev up -d dev
```

The development service exposes `http://localhost:8001` and mounts the project directory into the container.

## Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"healthy","service":"Virtual Assistant API"}
```
