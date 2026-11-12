# YAML Editing

YAML table descriptions live in `tool/database/tableDescription/`.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/yaml/` | Return all YAML files and parsed contents |
| POST | `/yaml/` | Replace, add, or delete YAML files in bulk |

## Bulk Update Payload

```json
{
  "files": {
    "loan.yaml": {
      "table_id": "loan",
      "dataset_id": "local",
      "table_description": "SQLite table containing loan application data",
      "headers": {
        "application_key": "Unique ID of the specific loan application",
        "loan_amount": "Principal loan amount granted"
      }
    },
    "obsolete.yaml": null
  }
}
```

Passing `null` deletes the named YAML file when it exists. YAML updates are written immediately; the server is not restarted automatically.
