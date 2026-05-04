from docpipe.exports import export_knowledge_pack
from docpipe.models import BatchReport, Chunk, ConversionResult, QualityMetrics


def test_export_knowledge_pack_writes_expected_files(tmp_path):
    result = ConversionResult(
        source_path=str(tmp_path / "source.md"),
        requested_engine="auto",
        used_engine="markitdown",
        status="success",
        markdown="# Title",
        chunks=[Chunk(index=0, text="hello", chars=5, heading="Title")],
        metrics=QualityMetrics(
            chars=7,
            words=2,
            lines=1,
            headings=1,
            tables=0,
            chunks=1,
            empty=False,
            quality_score=100,
        ),
    )
    report = BatchReport(
        job_id="job-test",
        output_dir=str(tmp_path),
        total=1,
        succeeded=1,
        failed=0,
        results=[result],
    )

    paths = export_knowledge_pack(report, tmp_path)

    assert set(paths) == {
        "generic_jsonl",
        "dify_csv",
        "coze_csv",
        "fastgpt_jsonl",
        "ragflow_jsonl",
        "review_checklist_csv",
        "review_checklist_md",
        "handoff_guide",
        "manifest",
        "zip",
    }
    for path in paths.values():
        assert path

    assert (tmp_path / "exports" / "docpipe_export_pack.zip").exists()
    assert "DocPipe Handoff Guide" in (
        tmp_path / "exports" / "handoff_guide.md"
    ).read_text(encoding="utf-8")
    assert "No files require manual review." in (
        tmp_path / "exports" / "review_checklist.md"
    ).read_text(encoding="utf-8")


def test_export_knowledge_pack_writes_review_checklist(tmp_path):
    result = ConversionResult(
        source_path=str(tmp_path / "short.md"),
        requested_engine="auto",
        used_engine="markitdown",
        status="success",
        markdown="tiny",
        chunks=[Chunk(index=0, text="tiny", chars=4)],
        metrics=QualityMetrics(
            chars=4,
            words=1,
            lines=1,
            headings=0,
            tables=0,
            chunks=1,
            empty=False,
            quality_score=62,
            warnings=["very_short_output"],
            review_required=True,
        ),
    )
    report = BatchReport(
        job_id="job-review",
        output_dir=str(tmp_path),
        total=1,
        succeeded=1,
        failed=0,
        results=[result],
    )

    export_knowledge_pack(report, tmp_path)

    checklist = (tmp_path / "exports" / "review_checklist.md").read_text(encoding="utf-8")
    assert "short.md" in checklist
    assert "very_short_output" in checklist


def test_export_knowledge_pack_uses_workflow_template(tmp_path):
    result = ConversionResult(
        source_path=str(tmp_path / "policy.md"),
        requested_engine="auto",
        used_engine="markitdown",
        status="success",
        markdown="# Policy",
        chunks=[Chunk(index=0, text="policy", chars=6, heading="Policy")],
        metrics=QualityMetrics(
            chars=8,
            words=1,
            lines=1,
            headings=1,
            tables=0,
            chunks=1,
            empty=False,
            quality_score=100,
        ),
    )
    report = BatchReport(
        job_id="job-template",
        output_dir=str(tmp_path),
        total=1,
        succeeded=1,
        failed=0,
        results=[result],
    )

    export_knowledge_pack(report, tmp_path, workflow_template="enterprise-policy")

    handoff = (tmp_path / "exports" / "handoff_guide.md").read_text(encoding="utf-8")
    manifest = (tmp_path / "exports" / "manifest.json").read_text(encoding="utf-8")
    assert "Enterprise policy knowledge base" in handoff
    assert '"workflow_template": "enterprise-policy"' in manifest


def test_export_knowledge_pack_writes_chinese_handoff(tmp_path):
    result = ConversionResult(
        source_path=str(tmp_path / "policy.md"),
        requested_engine="auto",
        used_engine="markitdown",
        status="success",
        markdown="# Policy",
        chunks=[Chunk(index=0, text="policy", chars=6, heading="Policy")],
        metrics=QualityMetrics(
            chars=8,
            words=1,
            lines=1,
            headings=1,
            tables=0,
            chunks=1,
            empty=False,
            quality_score=100,
        ),
    )
    report = BatchReport(
        job_id="job-zh",
        output_dir=str(tmp_path),
        total=1,
        succeeded=1,
        failed=0,
        results=[result],
    )

    export_knowledge_pack(
        report, tmp_path, workflow_template="enterprise-policy", language="zh-CN"
    )

    handoff = (tmp_path / "exports" / "handoff_guide.md").read_text(encoding="utf-8")
    manifest = (tmp_path / "exports" / "manifest.json").read_text(encoding="utf-8")
    assert "DocPipe 交付指南" in handoff
    assert "企业制度知识库" in handoff
    assert '"language": "zh-CN"' in manifest
