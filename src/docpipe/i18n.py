from __future__ import annotations

from typing import Literal


Language = Literal["en", "zh-CN"]


TEXT: dict[str, dict[str, str]] = {
    "app_caption": {
        "en": "Enterprise document conversion for Markdown, JSON, and RAG-ready chunks.",
        "zh-CN": "企业文档转 Markdown、JSON 和知识库切块的本地工具。",
    },
    "settings": {"en": "Settings", "zh-CN": "设置"},
    "language": {"en": "Language", "zh-CN": "语言"},
    "workflow_template": {"en": "Workflow template", "zh-CN": "工作流模板"},
    "engine": {"en": "Engine", "zh-CN": "解析引擎"},
    "max_chunk_chars": {"en": "Max chunk characters", "zh-CN": "每个切块最大字符数"},
    "max_retries": {"en": "Retries per engine", "zh-CN": "每个引擎重试次数"},
    "output_folder": {"en": "Output folder", "zh-CN": "输出目录"},
    "create_job_dir": {"en": "Create a timestamped job folder", "zh-CN": "创建带时间戳的任务目录"},
    "write_export_pack": {"en": "Write knowledge-base export pack", "zh-CN": "生成知识库导出包"},
    "engine_registry": {"en": "Engine registry", "zh-CN": "引擎注册表"},
    "route_info": {
        "en": "PDF files use the structure-aware route. Office and web/text files use the general conversion route.",
        "zh-CN": "PDF 默认走结构化解析路线；Office 和网页/文本文件默认走通用转换路线。",
    },
    "convert_tab": {"en": "Convert", "zh-CN": "转换"},
    "history_tab": {"en": "Job history", "zh-CN": "任务历史"},
    "upload_documents": {"en": "Upload documents", "zh-CN": "上传文档"},
    "convert_button": {"en": "Convert", "zh-CN": "开始转换"},
    "spinner": {"en": "Converting documents...", "zh-CN": "正在转换文档..."},
    "converted": {"en": "Converted", "zh-CN": "已转换"},
    "files": {"en": "Files", "zh-CN": "文件数"},
    "succeeded": {"en": "Succeeded", "zh-CN": "成功"},
    "review_needed": {"en": "Review needed", "zh-CN": "需复核"},
    "average_score": {"en": "Average score", "zh-CN": "平均分"},
    "job": {"en": "Job", "zh-CN": "任务"},
    "rag_pack": {"en": "RAG pack", "zh-CN": "RAG 切块包"},
    "export_pack": {"en": "Export pack", "zh-CN": "导出包"},
    "download_zip": {"en": "Download export ZIP", "zh-CN": "下载导出 ZIP"},
    "download_review": {"en": "Download review checklist", "zh-CN": "下载复核清单"},
    "download_handoff": {"en": "Download handoff guide", "zh-CN": "下载交付指南"},
    "review_warning": {
        "en": "Some files need review before knowledge-base import.",
        "zh-CN": "部分文件在导入知识库前需要人工复核。",
    },
    "preview": {"en": "Preview", "zh-CN": "预览"},
    "converted_file": {"en": "Converted file", "zh-CN": "已转换文件"},
    "source_preview": {"en": "Source preview", "zh-CN": "源文件预览"},
    "markdown_preview": {"en": "Converted Markdown", "zh-CN": "转换后的 Markdown"},
    "binary_preview": {
        "en": "Binary document preview is not available.",
        "zh-CN": "暂不支持二进制文档源文件预览。",
    },
    "chunks": {"en": "Chunks", "zh-CN": "切块"},
    "no_jobs": {"en": "No conversion jobs found yet.", "zh-CN": "还没有转换任务。"},
    "why_title": {"en": "Why This Exists", "zh-CN": "为什么需要 DocPipe"},
    "why_body": {
        "en": "DocPipe turns mixed enterprise documents into reviewable Markdown, JSON, and RAG chunks. It chooses a conversion route, exports clean content, and creates a report that an enterprise team can review before loading documents into an AI knowledge base.",
        "zh-CN": "DocPipe 把企业里的混乱文档整理成可复核的 Markdown、JSON 和 RAG 切块。它会选择合适的转换路线，生成干净内容和报告，让团队在导入 AI 知识库前先检查质量。",
    },
}


def t(key: str, language: Language) -> str:
    values = TEXT[key]
    return values.get(language) or values["en"]
