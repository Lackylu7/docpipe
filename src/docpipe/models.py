from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


EngineName = Literal["auto", "markitdown", "docling"]
ResolvedEngineName = Literal["markitdown", "docling"]


class Chunk(BaseModel):
    index: int
    text: str
    chars: int
    heading: str | None = None


class QualityMetrics(BaseModel):
    chars: int
    words: int
    lines: int
    headings: int
    tables: int
    chunks: int
    empty: bool
    quality_score: int
    warnings: list[str] = Field(default_factory=list)
    review_required: bool = False


class ConversionResult(BaseModel):
    source_path: str
    output_markdown_path: str | None = None
    output_json_path: str | None = None
    requested_engine: EngineName
    used_engine: ResolvedEngineName | None = None
    status: Literal["success", "failed"]
    error: str | None = None
    markdown: str = ""
    chunks: list[Chunk] = Field(default_factory=list)
    metrics: QualityMetrics | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def filename(self) -> str:
        return Path(self.source_path).name


class BatchReport(BaseModel):
    job_id: str
    output_dir: str
    total: int
    succeeded: int
    failed: int
    results: list[ConversionResult]
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
