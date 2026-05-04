from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from docpipe.exports import export_knowledge_pack
from docpipe.engines import list_engines
from docpipe.history import list_jobs
from docpipe.i18n import Language, t
from docpipe.pipeline import convert_batch, export_rag_pack
from docpipe.templates import get_template, list_templates, template_description, template_name


st.set_page_config(page_title="DocPipe", page_icon="D", layout="wide")

st.title("DocPipe")

with st.sidebar:
    language_label = st.selectbox("Language / 语言", ["zh-CN", "en"], index=0)
    language: Language = "zh-CN" if language_label == "zh-CN" else "en"
    st.header(t("settings", language))
    templates = list_templates()
    workflow_template = st.selectbox(
        t("workflow_template", language),
        [template.key for template in templates],
        index=0,
        format_func=lambda key: template_name(get_template(key), language),
    )
    selected_template = get_template(workflow_template)
    st.caption(template_description(selected_template, language))
    engine_names = ["auto", *[adapter.name for adapter in list_engines()]]
    engine = st.selectbox(t("engine", language), engine_names, index=0)
    max_chunk_chars = st.slider(
        t("max_chunk_chars", language),
        min_value=500,
        max_value=3000,
        value=selected_template.max_chunk_chars,
    )
    max_retries = st.number_input(t("max_retries", language), min_value=0, max_value=3, value=1)
    output_dir = Path(st.text_input(t("output_folder", language), value="outputs")).expanduser()
    create_job_dir = st.checkbox(t("create_job_dir", language), value=True)
    write_export_pack = st.checkbox(t("write_export_pack", language), value=True)

st.caption(t("app_caption", language))

with st.expander(t("engine_registry", language), expanded=False):
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

st.info(t("route_info", language))

tab_convert, tab_history = st.tabs([t("convert_tab", language), t("history_tab", language)])

with tab_convert:
    uploaded_files = st.file_uploader(
        t("upload_documents", language),
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

    if st.button(t("convert_button", language), type="primary", disabled=not uploaded_files):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir)
            for uploaded_file in uploaded_files:
                target = input_dir / uploaded_file.name
                target.write_bytes(uploaded_file.getbuffer())

            with st.spinner(t("spinner", language)):
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
                        report,
                        actual_output,
                        workflow_template=workflow_template,
                        language=language,
                    )
                    if write_export_pack
                    else {}
                )

        st.success(f"{t('converted', language)} {report.succeeded}/{report.total}")
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
        metric_cols[0].metric(t("files", language), report.total)
        metric_cols[1].metric(t("succeeded", language), report.succeeded)
        metric_cols[2].metric(t("review_needed", language), review_required)
        metric_cols[3].metric(t("average_score", language), f"{avg_score:.0f}")
        st.write(f"{t('job', language)}: `{report.job_id}`")
        st.write(f"{t('output_folder', language)}: `{Path(report.output_dir).resolve()}`")
        st.write(f"{t('rag_pack', language)}: `{rag_path.resolve()}`")
        if export_paths:
            st.write(f"{t('export_pack', language)}:")
            for name, path in export_paths.items():
                st.write(f"- `{name}`: `{Path(path).resolve()}`")
            zip_path = Path(export_paths["zip"])
            if zip_path.exists():
                st.download_button(
                    t("download_zip", language),
                    data=zip_path.read_bytes(),
                    file_name=zip_path.name,
                    mime="application/zip",
                )
            review_path = Path(export_paths["review_checklist_md"])
            if review_path.exists():
                st.download_button(
                    t("download_review", language),
                    data=review_path.read_bytes(),
                    file_name=review_path.name,
                    mime="text/markdown",
                )
            handoff_path = Path(export_paths["handoff_guide"])
            if handoff_path.exists():
                st.download_button(
                    t("download_handoff", language),
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
            st.warning(t("review_warning", language))
            st.dataframe(review_rows, use_container_width=True)

        successful = [result for result in report.results if result.status == "success"]
        if successful:
            st.subheader(t("preview", language))
            selected = st.selectbox(
                t("converted_file", language), successful, format_func=lambda item: item.filename
            )
            col_source, col_markdown = st.columns(2)
            with col_source:
                st.caption(t("source_preview", language))
                st.text(selected.source_profile.text_preview or t("binary_preview", language))
            with col_markdown:
                st.caption(t("markdown_preview", language))
                st.markdown(selected.markdown[:6000])
            st.caption(t("chunks", language))
            st.dataframe([chunk.model_dump() for chunk in selected.chunks], use_container_width=True)

with tab_history:
    jobs = list_jobs(output_dir)
    if jobs:
        st.dataframe(jobs, use_container_width=True)
    else:
        st.write(t("no_jobs", language))

st.divider()
st.subheader(t("why_title", language))
st.write(t("why_body", language))
