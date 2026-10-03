from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.ai_core.gemini_generator import (
    GeminiConfigurationError,
    GeminiDocumentGenerator,
    GeminiGenerationError,
)
from backend.schemas import DocumentRequest, ExportRequest, GenerateResponse
from backend.services.document_formatter import export_document

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
def generate_document(request: DocumentRequest) -> GenerateResponse:
    try:
        generator = GeminiDocumentGenerator()
        content = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
            language=request.language,
        )
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except GeminiGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return GenerateResponse(
        document_type=request.document_type,
        language=request.language,
        content=content,
    )


@router.post("/export")
def export_generated_document(request: ExportRequest) -> Response:
    try:
        data, media_type, extension = export_document(
            file_format=request.format,
            content=request.content,
            doc_type=request.document_type,
            terms=request.terms,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document export failed: {exc}",
        ) from exc

    filename = f"LegalEase_{request.document_type.strip().replace(' ', '_')}{extension}"

    return Response(
        content=data,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )
