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
        "manifest",
    }
    for path in paths.values():
        assert path
