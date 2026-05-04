import json

from docpipe.history import list_jobs


def test_list_jobs_reads_conversion_reports(tmp_path):
    job_dir = tmp_path / "job-20260101-000000"
    job_dir.mkdir()
    (job_dir / "conversion_report.json").write_text(
        json.dumps(
            {
                "job_id": "job-20260101-000000",
                "created_at": "2026-01-01T00:00:00Z",
                "total": 2,
                "succeeded": 1,
                "failed": 1,
                "results": [],
            }
        ),
        encoding="utf-8",
    )

    jobs = list_jobs(tmp_path)

    assert len(jobs) == 1
    assert jobs[0]["job_id"] == "job-20260101-000000"
    assert jobs[0]["total"] == 2
