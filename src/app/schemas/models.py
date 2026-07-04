from pydantic import BaseModel
from typing import Any


# ── Shared ────────────────────────────────────────────────────────────────────

class DiffResponse(BaseModel):
    similarity_score: float
    new_lines: list[str]
    deleted_lines: list[str]


class SummaryResponse(BaseModel):
    summary: str


# ── CSV / Excel ───────────────────────────────────────────────────────────────

class CsvDiffRow(BaseModel):
    sl_no: str
    column_name: str
    old_value: str
    new_value: str


class CsvSymmetricResponse(BaseModel):
    differences: Any          # pandas DataFrame.compare() output serialised as records


class CsvAsymmetricResponse(BaseModel):
    added: list[Any]
    removed: list[Any]
    changed: list[Any]
    columns_added: list[str]
    columns_removed: list[str]
    columns_renamed: list[str]


class CsvDictResponse(BaseModel):
    csv_text: str
    records: list[CsvDiffRow]


# ── Excel file response is a FileResponse (no schema needed) ──────────────────