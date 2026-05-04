from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from docpipe.exports import export_knowledge_pack
from docpipe.engines import list_engines
from docpipe.history import list_jobs
from docpipe.pipeline import convert_batch, export_rag_pack
from docpipe.templates import get_template, list_templates


st.set_page_config(page_title="DocPipe", page_icon="D", layout="wide")

st.title("DocPipe")
st.caption("Enterprise document conversion for Markdown, JSON, and RAG-ready chunks.")

with st.sidebar:
    st.header("Settings")
    templates = list_templates()
    workflow_template = st.selectbox(
        "Workflow template",
        [template.key for template in templates],
        index=0,
        format_func=lambda key: get_template(key).name,
    )
    selected_template = get_template(workflow_template)
    st.caption(selected_template.description)
    engine_names = ["auto", *[adapter.name for adapter in list_engines()]]
    engine = st.selectbox("Engine", engine_names, index=0)
    max_chunk_chars = st.slider(
        "Max chunk characters",
        min_value=500,
        max_value=3000,
        value=selected_template.max_chunk_chars,
    )
    max_retries = st.number_input("Retries per engine", min_value=0, max_value=3, value=1)
    output_dir = Path(st.text_input("Output folder", value="outputs")).expanduser()
    create_job_dir = st.checkbox("Create a timestamped job folder", value=True)
    write_export_pack = st.checkbox("Write knowledge-base export pack", value=True)
with st.expander("Engine registry", expanded=False):
    st.dataframe(
        [
            {
                "engine": adapter.name,
                "priority": adapter.priority,
                "extensions": ", ".join(sorted(adapter.extensions)) or "planned adapter",
                "description": adapter.description,
            }
            for adapter in list_engines()
        ],
        use_container_width=True,
    )

st.info("PDF files use the structure-aware route. Office and web/text files use the general conversion route.")

tab_convert, tab_history = st.tabs(["Convert", "Job history"])

with tab_convert:
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=[
            "pdf",
            "docx",
            "pptx",
            "xlsx",
            "xls",
            "csv",
            "html",
            "htm",
            "txt",
            "json",
            "xml",
            "md",
            "png",
            "jpg",
            "jpeg",
            "gif",
            "wav",
            "mp3",
            "m4a",
        ],
        accept_multiple_files=True,
    )

    if st.button("Convert", type="primary", disabled=not uploaded_files):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir)
            for uploaded_file in uploaded_files:
                target = input_dir / uploaded_file.name
                target.write_bytes(uploaded_file.getbuffer())

            with st.spinner("Converting documents..."):
                report = convert_batch(
                    input_dir,
                    output_dir=output_dir,
                    engine=engine,  # type: ignore[arg-type]
                    max_chunk_chars=max_chunk_chars,
                    create_job_dir=create_job_dir,
                    max_retries=int(max_retries),
                )
                actual_output = Path(report.output_dir)
                rag_path = export_rag_pack(report, actual_output)
                export_paths = (
                    export_knowledge_pack(
                        report, actual_output, workflow_template=workflow_template
                    )
                    if write_export_pack
                    else {}
                )

        st.success(f"Converted {report.succeeded}/{report.total} files.")
        review_required = sum(
            1
            for result in report.results
            if result.metrics and result.metrics.review_required
        )
        avg_score = (
            sum(result.metrics.quality_score for result in report.results if result.metrics)
            / max(sum(1 for result in report.results if result.metrics), 1)
        )
        metric_cols = st.columns(4)
        metric_cols[0].metric("Files", report.total)
        metric_cols[1].metric("Succeeded", report.succeeded)
        metric_cols[2].metric("Review needed", review_required)
        metric_cols[3].metric("Average score", f"{avg_score:.0f}")
        st.write(f"Job: `{report.job_id}`")
        st.write(f"Output folder: `{Path(report.output_dir).resolve()}`")
        st.write(f"RAG pack: `{rag_path.resolve()}`")
        if export_paths:
            st.write("Export pack:")
            for name, path in export_paths.items():
                st.write(f"- `{name}`: `{Path(path).resolve()}`")
            zip_path = Path(export_paths["zip"])
            if zip_path.exists():
                st.download_button(
                    "Download export ZIP",
                    data=zip_path.read_bytes(),
                    file_name=zip_path.name,
                    mime="application/zip",
                )
            review_path = Path(export_paths["review_checklist_md"])
            if review_path.exists():
                st.download_button(
                    "Download review checklist",
                    data=review_path.read_bytes(),
                    file_name=review_path.name,
                    mime="text/markdown",
                )
            handoff_path = Path(export_paths["handoff_guide"])
            if handoff_path.exists():
                st.download_button(
                    "Download handoff guide",
                    data=handoff_path.read_bytes(),
                    file_name=handoff_path.name,
                    mime="text/markdown",
                )

        rows = []
        for result in report.results:
            rows.append(
                {
                    "file": result.filename,
                    "status": result.status,
                    "engine": result.used_engine,
                    "score": result.metrics.quality_score if result.metrics else None,
                    "warnings": ", ".join(result.metrics.warnings) if result.metrics else "",
                    "review": result.metrics.review_required if result.metrics else True,
                    "chunks": result.metrics.chunks if result.metrics else 0,
                    "chars": result.metrics.chars if result.metrics else 0,
                    "tables": result.metrics.tables if result.metrics else 0,
                    "headings": result.metrics.headings if result.metrics else 0,
                    "attempts": result.attempts,
                    "error": result.error,
                }
            )
        st.dataframe(rows, use_container_width=True)

        review_rows = [row for row in rows if row["review"] or row["status"] == "failed"]
        if review_rows:
            st.warning("Some files need review before knowledge-base import.")
            st.dataframe(review_rows, use_container_width=True)

        successful = [result for result in report.results if result.status == "success"]
        if successful:
            st.subheader("Preview")
            selected = st.selectbox("Converted file", successful, format_func=lambda item: item.filename)
            col_source, col_markdown = st.columns(2)
            with col_source:
                st.caption("Source preview")
                st.text(selected.source_profile.text_preview or "Binary document preview is not available.")
            with col_markdown:
                st.caption("Converted Markdown")
                st.markdown(selected.markdown[:6000])
            st.caption("Chunks")
            st.dataframe([chunk.model_dump() for chunk in selected.chunks], use_container_width=True)

with tab_history:
    jobs = list_jobs(output_dir)
    if jobs:
        st.dataframe(jobs, use_container_width=True)
    else:
        st.write("No conversion jobs found yet.")

st.divider()
st.subheader("Why This Exists")
st.write(
    "DocPipe turns mixed enterprise documents into reviewable Markdown, JSON, and RAG chunks. "
    "It chooses a conversion route, exports clean content, and creates a report that an "
    "enterprise team can review before loading documents into an AI knowledge base."
)
