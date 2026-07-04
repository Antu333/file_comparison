from fastapi import UploadFile, HTTPException, File

# Max file size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_TYPES = {
    "docx": [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ],
    "pdf": [
        "application/pdf",
    ],
    "csv": [
        "text/csv",
        "text/plain",
        "application/csv",
        "application/octet-stream",
    ],
    "excel": [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "application/octet-stream",
    ],
}

ALLOWED_EXTENSIONS = {
    "docx": {".docx"},
    "pdf": {".pdf"},
    "csv": {".csv"},
    "excel": {".xlsx", ".xls"},
}


async def _validate(upload: UploadFile, kind: str) -> UploadFile:
    filename = upload.filename or ""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS[kind]:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Invalid file type for '{filename}'. "
                f"Expected: {', '.join(ALLOWED_EXTENSIONS[kind])}"
            ),
        )

    if upload.content_type not in ALLOWED_TYPES[kind]:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported content-type '{upload.content_type}' for '{filename}'. "
                f"Expected one of: {', '.join(ALLOWED_TYPES[kind])}"
            ),
        )

    contents = await upload.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=(
                f"'{filename}' exceeds the 10 MB limit "
                f"({len(contents) / 1024 / 1024:.1f} MB uploaded)."
            ),
        )
    if len(contents) == 0:
        raise HTTPException(
            status_code=422,
            detail=f"'{filename}' is empty.",
        )

    await upload.seek(0)
    return upload


# ── Factory: returns a dependency bound to a specific form field name ─────────

def make_validator(kind: str, field_name: str):
    async def _dep(file: UploadFile = File(..., alias=field_name)):
        return await _validate(file, kind)
    # Give the inner function a unique name so FastAPI treats them as distinct
    _dep.__name__ = f"valid_{kind}_{field_name}"
    return _dep


# ── Pre-built dependency pairs for each format ────────────────────────────────

valid_docx_1 = make_validator("docx", "file1")
valid_docx_2 = make_validator("docx", "file2")

valid_pdf_1  = make_validator("pdf",  "file1")
valid_pdf_2  = make_validator("pdf",  "file2")

valid_csv_1  = make_validator("csv",  "file1")
valid_csv_2  = make_validator("csv",  "file2")

valid_excel_1 = make_validator("excel", "file1")
valid_excel_2 = make_validator("excel", "file2")