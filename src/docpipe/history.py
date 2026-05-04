from __future__ import annotations

import json
from pathlib import Path


def list_jobs(output_root: Path) -> list[dict[str, object]]:
    if not output_root.exists():
        return []
    reports = sorted(
        output_root.glob("job-*/conversion_report.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    jobs: list[dict[str, object]] = []
    for report_path in reports:
        try:
            payload = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        jobs.append(
            {
                "job_id": payload.get("job_id", report_path.parent.name),
                "created_at": payload.get("created_at"),
                "total": payload.get("total", 0),
                "succeeded": payload.get("succeeded", 0),
                "failed": payload.get("failed", 0),
                "output_dir": str(report_path.parent.resolve()),
                "report_path": str(report_path.resolve()),
            }
        )
    return jobs


def load_job(report_path: Path) -> dict[str, object]:
    return json.loads(report_path.read_text(encoding="utf-8"))
