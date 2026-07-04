from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from src.app.utils.dependencies import valid_docx_1, valid_docx_2
from src.app.schemas.models import DiffResponse, SummaryResponse
from src.app.services.read_file import FileReader
from src.app.services.methods import CompareService

router = APIRouter(prefix="/docx", tags=["DOCX"])


@router.post(
    "/compare",
    response_model=DiffResponse,
    summary="Compare two DOCX files",
    description="Upload two .docx files and receive a similarity score plus line-level diff.",
)
async def compare_docx(
    file1: UploadFile = Depends(valid_docx_1),
    file2: UploadFile = Depends(valid_docx_2),
):
    try:
        content1 = await FileReader.get_text(file1)
        content2 = await FileReader.get_text(file2)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read DOCX files: {e}")

    return CompareService.text_report(content1, content2)


@router.post(
    "/summary",
    response_model=SummaryResponse,
    summary="Summarise differences between two DOCX files",
    description="Upload two .docx files and receive an AI-generated summary of their differences.",
)
async def summarise_docx(
    file1: UploadFile = Depends(valid_docx_1),
    file2: UploadFile = Depends(valid_docx_2),
):
    try:
        content1 = await FileReader.get_text(file1)
        content2 = await FileReader.get_text(file2)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read DOCX files: {e}")

    try:
        summary_text = CompareService.summary_for_text(content1, content2)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {"summary": summary_text}