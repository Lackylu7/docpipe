from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowTemplate:
    key: str
    name: str
    description: str
    max_chunk_chars: int
    review_focus: tuple[str, ...]
    handoff_steps: tuple[str, ...]


TEMPLATES: dict[str, WorkflowTemplate] = {
    "general": WorkflowTemplate(
        key="general",
        name="General knowledge base",
        description="Balanced defaults for mixed company documents.",
        max_chunk_chars=1400,
        review_focus=(
            "Review files with low quality scores or conversion warnings.",
            "Confirm headings and chunk boundaries before import.",
            "Spot-check the generated Markdown against the original files.",
        ),
        handoff_steps=(
            "Open conversion_report.md and confirm the success rate.",
            "Open review_checklist.md and resolve flagged files.",
            "Import the vendor starter file that matches the target knowledge-base system.",
            "Run a small retrieval test before importing a larger document folder.",
        ),
    ),
    "enterprise-policy": WorkflowTemplate(
        key="enterprise-policy",
        name="Enterprise policy knowledge base",
        description="Best for HR policies, internal rules, SOPs, and compliance manuals.",
        max_chunk_chars=1100,
        review_focus=(
            "Confirm every policy section keeps its heading path.",
            "Review short chunks because policy exceptions often live in small paragraphs.",
            "Check dates, approval owners, and compliance wording before import.",
        ),
        handoff_steps=(
            "Group source files by department or policy area before a full run.",
            "Review flagged short chunks and merge source sections when needed.",
            "Import chunks with heading_path metadata enabled in the target RAG system.",
            "Ask domain owners to test questions about eligibility, exceptions, and approval flow.",
        ),
    ),
    "support-faq": WorkflowTemplate(
        key="support-faq",
        name="Support FAQ knowledge base",
        description="Best for ticket answers, help-center pages, troubleshooting notes, and FAQs.",
        max_chunk_chars=900,
        review_focus=(
            "Check that each question-answer pair stays together.",
            "Review repeated lines from exported ticket systems.",
            "Remove obsolete answers before importing into a customer-facing assistant.",
        ),
        handoff_steps=(
            "Clean duplicate ticket exports before batch conversion.",
            "Review the checklist for repeated or tiny chunks.",
            "Import FAQ chunks with filename and heading metadata.",
            "Test customer questions that contain vague wording, typos, or product aliases.",
        ),
    ),
    "product-manual": WorkflowTemplate(
        key="product-manual",
        name="Product manual knowledge base",
        description="Best for manuals, release notes, onboarding guides, and training material.",
        max_chunk_chars=1600,
        review_focus=(
            "Check tables, numbered procedures, and warnings against the source.",
            "Confirm long sections are split around task boundaries.",
            "Review image-heavy or scan-heavy files before import.",
        ),
        handoff_steps=(
            "Run a small sample from each product line first.",
            "Inspect table-heavy files in review_checklist.md.",
            "Import with source filename metadata so answers can cite manuals.",
            "Test procedural questions that require step order and safety notes.",
        ),
    ),
}


def list_templates() -> list[WorkflowTemplate]:
    return list(TEMPLATES.values())


def get_template(key: str) -> WorkflowTemplate:
    try:
        return TEMPLATES[key]
    except KeyError as exc:
        known = ", ".join(TEMPLATES)
        raise ValueError(f"Unknown workflow template '{key}'. Choose one of: {known}.") from exc
