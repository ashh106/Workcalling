# Tool Modules

The tool package contains the local database integration used by the assistant.

## Structure

```text
tool/
├── database/
│   ├── connector/
│   │   └── sqlitedb.py
│   ├── prompt/
│   │   └── prompts.py
│   └── tableDescription/
│       └── loan.yaml
└── licence.txt
```

## SQLite Connector

`tool.database.connector.sqlitedb` executes SQL against the database configured by `SQLITE_DB_PATH`.

The main public function is:

```python
run_query(sql_query: str, explanation: str)
```

It returns a standardized success/error response with columns, rows, row count, and the provided explanation.
