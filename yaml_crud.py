from pathlib import Path
import logging
from typing import List, Dict, Any

import yaml
from fastapi import APIRouter, HTTPException, FastAPI
from pydantic import BaseModel

import utils

logger = logging.getLogger(__name__)

# Default directory containing YAML files relative to project root
YAML_DIR = Path(__file__).resolve().parent / "tool" / "database" / "tableDescription"
YAML_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------
# Pydantic models
# -------------------------------

class AllYamlFilesPayload(BaseModel):
    """Payload model for sending/receiving all YAML files in bulk.

    The *files* field maps a filename (including extension) to its YAML
    content represented as an arbitrary JSON-serialisable object.
    """

    files: Dict[str, Any]


# -------------------------------
# Helper functions
# -------------------------------

def _safe_filename(filename: str) -> str:
    """Ensure the filename ends with .yaml and contains no path traversal."""
    name = filename if filename.endswith(".yaml") else f"{filename}.yaml"
    # Basic traversal protection
    if ".." in Path(name).parts:
        raise HTTPException(status_code=400, detail="Invalid filename: path traversal detected")
    return name


def _file_path(filename: str) -> Path:
    return YAML_DIR / _safe_filename(filename)


def _write_yaml_file(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
    logger.info(f"YAML file written: {path}")


def _read_yaml_file(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# -------------------------------
# FastAPI router
# -------------------------------

yaml_router = APIRouter(prefix="/yaml", tags=["YAML CRUD"])


@yaml_router.get("/", summary="Get all YAML files")
def get_all_yaml_files() -> Dict[str, Any]:
    """Return **all** YAML filenames **and** their parsed contents."""
    files_dict = {p.name: _read_yaml_file(p) for p in YAML_DIR.glob("*.yaml")}
    return utils.create_success_response({"files": files_dict})


@yaml_router.post("/", summary="Replace all YAML files")
def replace_all_yaml_files(payload: AllYamlFilesPayload):
    """Overwrite *all* YAML files with the provided mapping.

    Any existing YAML file that is **not** present in the incoming mapping is
    left untouched. To delete a file, pass an explicit `null` for its content
    (e.g.  "obsolete.yaml": null).
    """
    processed: List[str] = []
    for filename, content in payload.files.items():
        if content is None:
            # Interpret null as a delete command when file exists
            path = _file_path(filename)
            if path.exists():
                path.unlink()
                logger.info(f"YAML file deleted via bulk payload: {path}")
            continue

        path = _file_path(filename)
        _write_yaml_file(path, content)
        processed.append(path.name)

    return utils.create_success_response({"processed": processed})


# -------------------------------
# Public API for main.py to invoke
# -------------------------------

def register_yaml_crud(app: FastAPI):
    """Include the YAML CRUD router on the given FastAPI app."""
    app.include_router(yaml_router) 
