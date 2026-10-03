from typing import Literal

from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    parties: str = Field(..., min_length=2, max_length=3000)
    terms: str = Field(..., min_length=2, max_length=10000)
    effective_date: str = Field(..., min_length=2, max_length=100)
    language: str = Field(default="English", min_length=2, max_length=60)

    @field_validator("document_type", "parties", "terms", "effective_date", "language")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty.")
        return value


class GenerateResponse(BaseModel):
    document_type: str
    language: str
    content: str


class ExportRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    content: str = Field(..., min_length=1, max_length=1000000)
    terms: str = Field(default="", max_length=10000)
    format: Literal["txt", "docx", "pdf"]
