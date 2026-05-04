from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from docpipe.exports import export_knowledge_pack
from docpipe.pipeline import convert_batch, export_rag_pack


st.set_page_config(page_title="DocPipe", page_icon="D", layout="wide")

st.title("DocPipe")
st.caption("Enterprise document conversion for Markdown, JSON, and RAG-ready chunks.")

with st.sidebar:
    st.header("Settings")
    engine = st.selectbox("Engine", ["auto", "markitdown", "docling"], index=0)
    max_chunk_chars = st.slider("Max chunk characters", min_value=500, max_value=3000, value=1400)
    output_dir = Path(st.text_input("Output folder", value="outputs")).expanduser()
    create_job_dir = st.checkbox("Create a timestamped job folder", value=True)
    write_export_pack = st.checkbox("Write knowledge-base export pack", value=True)
    st.info("PDF files default to Docling. Office and web/text files default to MarkItDown.")

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
            )
            actual_output = Path(report.output_dir)
            rag_path = export_rag_pack(report, actual_output)
            export_paths = export_knowledge_pack(report, actual_output) if write_export_pack else {}

    st.success(f"Converted {report.succeeded}/{report.total} files.")
    st.write(f"Job: `{report.job_id}`")
    st.write(f"Output folder: `{Path(report.output_dir).resolve()}`")
    st.write(f"RAG pack: `{rag_path.resolve()}`")
    if export_paths:
        st.write("Export pack:")
        for name, path in export_paths.items():
            st.write(f"- `{name}`: `{Path(path).resolve()}`")

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
                "error": result.error,
            }
        )
    st.dataframe(rows, use_container_width=True)

    successful = [result for result in report.results if result.status == "success"]
    if successful:
        st.subheader("Preview")
        selected = st.selectbox("Converted file", successful, format_func=lambda item: item.filename)
        st.markdown(selected.markdown[:6000])

st.divider()
st.subheader("Why This Exists")
st.write(
    "MarkItDown is fast and broad. Docling is stronger for structure-heavy PDFs. "
    "DocPipe chooses between them, exports clean content, and creates a report that "
    "an enterprise team can review before loading documents into an AI knowledge base."
)
