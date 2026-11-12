# Database Module

The database module provides local SQLite query execution and schema prompt context for the assistant.

## Connector

`connector/sqlitedb.py` reads the SQLite file path from `SQLITE_DB_PATH`, defaulting to `./data/workmind.db`.

`run_query(sql_query, explanation)` returns:

- `explanation`
- `rows`
- `row_count`
- `columns`

Errors are returned through the common `utils.create_error_response()` shape.

## Prompt Context

`prompt/prompts.py` reads YAML files from `tableDescription/` and appends table metadata to the SQL tool description so the model can generate queries against local SQLite tables.
