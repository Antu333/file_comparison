from fastapi import APIRouter, Depends, UploadFile, HTTPException

from src.app.utils.dependencies import valid_pdf_1, valid_pdf_2
from src.app.schemas.models import DiffResponse, SummaryResponse
from src.app.services.read_file import FileReader
from src.app.services.methods import CompareService

router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.post(
    "/compare",
    response_model=DiffResponse,
    summary="Compare two PDF files",
    description="Upload two PDF files and receive a similarity score plus line-level diff.",
)
async def compare_pdf(
    file1: UploadFile = Depends(valid_pdf_1),
    file2: UploadFile = Depends(valid_pdf_2),
):
    try:
        content1 = await FileReader.extract_text_from_pdf(file1)
        content2 = await FileReader.extract_text_from_pdf(file2)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read PDF files: {e}")

    return CompareService.text_report(content1, content2)


@router.post(
    "/summary",
    response_model=SummaryResponse,
    summary="Summarise differences between two PDF files",
    description="Upload two PDF files and receive an AI-generated summary of their differences.",
)
async def summarise_pdf(
    file1: UploadFile = Depends(valid_pdf_1),
    file2: UploadFile = Depends(valid_pdf_2),
):
    try:
        content1 = await FileReader.extract_text_from_pdf(file1)
        content2 = await FileReader.extract_text_from_pdf(file2)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to read PDF files: {e}")

    try:
        summary_text = CompareService.summary_for_text(content1, content2)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {"summary": summary_text}