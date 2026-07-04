from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException

from src.app.utils.dependencies import valid_csv_1, valid_csv_2
from src.app.schemas.models import (
    CsvSymmetricResponse,
    CsvAsymmetricResponse,
    SummaryResponse,
    CsvDictResponse,
)
from src.app.services.read_file import FileReader
from src.app.services.methods import CompareService

router = APIRouter(prefix="/csv", tags=["CSV"])


@router.post(
    "/compare/symmetric",
    response_model=CsvSymmetricResponse,
    summary="Compare two identically-structured CSV files",
    description=(
        "Upload two CSV files with the same columns. "
        "Returns a record-level diff of every changed cell."
    ),
)
async def compare_csv_symmetric(
    file1: UploadFile = Depends(valid_csv_1),
    file2: UploadFile = Depends(valid_csv_2),
):
    try:
        df1 = await FileReader.read_csv(file1)
        df2 = await FileReader.read_csv(file2)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read CSV files: {e}")

    try:
        differences = CompareService.csv_symmetric_report(df1, df2)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Comparison failed: {e}")

    return {"differences": differences}


@router.post(
    "/compare/asymmetric",
    response_model=CsvAsymmetricResponse,
    summary="Compare two CSV files with different structures",
    description=(
        "Upload two CSV files that may differ in shape. "
        "Provide the key column used to match rows between files."
    ),
)
async def compare_csv_asymmetric(
    file1: UploadFile = Depends(valid_csv_1),
    file2: UploadFile = Depends(valid_csv_2),
    key_column: str = Form(..., description="Column name used as a unique row key"),
):
    try:
        bytes1 = await file1.read()
        bytes2 = await file2.read()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read CSV files: {e}")

    try:
        result = CompareService.csv_asymmetric_report(bytes1, bytes2, key_column)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Comparison failed: {e}")

    return result


@router.post(
    "/summary",
    response_model=SummaryResponse,
    summary="AI-generated comparison summary for two CSV files",
    description="Upload two CSV files and receive a Gemini-generated comparison table.",
)
async def summarise_csv(
    file1: UploadFile = Depends(valid_csv_1),
    file2: UploadFile = Depends(valid_csv_2),
):
    try:
        df1 = await FileReader.read_csv(file1)
        df2 = await FileReader.read_csv(file2)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read CSV files: {e}")

    try:
        summary_text = CompareService.summary_for_csv_excel(
            df1.to_string(index=False),
            df2.to_string(index=False),
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {"summary": summary_text}


@router.post(
    "/dict",
    response_model=CsvDictResponse,
    summary="Return Gemini CSV diff as structured records",
    description=(
        "Upload two CSV files. Gemini will diff them and return a structured list "
        "of changed rows with sl_no, column_name, old_value, new_value."
    ),
)
async def csv_to_dict(
    file1: UploadFile = Depends(valid_csv_1),
    file2: UploadFile = Depends(valid_csv_2),
):
    try:
        df1 = await FileReader.read_csv(file1)
        df2 = await FileReader.read_csv(file2)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read CSV files: {e}")

    try:
        raw_csv, records = CompareService.csv_string_to_records(
            df1.to_string(index=False),
            df2.to_string(index=False),
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {"csv_text": raw_csv, "records": records}