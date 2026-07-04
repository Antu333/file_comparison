import uuid

from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse

from src.app.utils.dependencies import valid_excel_1, valid_excel_2
from src.app.schemas.models import SummaryResponse
from src.app.services.read_file import FileReader
from src.app.services.methods import CompareService
from src.app.core.config import get_settings

settings = get_settings()


router = APIRouter(prefix="/excel", tags=["Excel"])


@router.post(
    "/compare",
    summary="Compare two Excel files",
    description=(
        "Upload two .xlsx files. Returns a downloadable Excel workbook "
        "with old/new sub-columns for every changed cell."
    ),
    response_class=FileResponse,
)
async def compare_excel(
    file1: UploadFile = Depends(valid_excel_1),
    file2: UploadFile = Depends(valid_excel_2),
    merge_on_column: str = Form(
        default="sl no",
        description="Column name used as the merge key (e.g. 'sl no', 'id')",
    ),
):
    try:
        bytes1 = await file1.read()
        bytes2 = await file2.read()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read Excel files: {e}")

    output_path = str(settings.OUTPUTS_DIR / f"diff_{uuid.uuid4().hex}.xlsx")

    try:
        result_path = CompareService.excel_report(bytes1, bytes2, output_path, merge_on_column)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel comparison failed: {e}")

    return FileResponse(
        path=result_path,
        filename="comparison_result.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.post(
    "/summary",
    response_model=SummaryResponse,
    summary="AI-generated comparison summary for two Excel files",
    description="Upload two .xlsx files and receive a Gemini-generated comparison table.",
)
async def summarise_excel(
    file1: UploadFile = Depends(valid_excel_1),
    file2: UploadFile = Depends(valid_excel_2),
):
    try:
        df1 = await FileReader.read_excel(file1)
        df2 = await FileReader.read_excel(file2)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read Excel files: {e}")

    try:
        summary_text = CompareService.summary_for_csv_excel(
            df1.to_string(index=False),
            df2.to_string(index=False),
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {"summary": summary_text}