from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowTemplate:
    key: str
    name: str
    zh_name: str
    description: str
    zh_description: str
    max_chunk_chars: int
    review_focus: tuple[str, ...]
    zh_review_focus: tuple[str, ...]
    handoff_steps: tuple[str, ...]
    zh_handoff_steps: tuple[str, ...]


TEMPLATES: dict[str, WorkflowTemplate] = {
    "general": WorkflowTemplate(
        key="general",
        name="General knowledge base",
        zh_name="通用知识库",
        description="Balanced defaults for mixed company documents.",
        zh_description="适合混合型企业文档的均衡默认配置。",
        max_chunk_chars=1400,
        review_focus=(
            "Review files with low quality scores or conversion warnings.",
            "Confirm headings and chunk boundaries before import.",
            "Spot-check the generated Markdown against the original files.",
        ),
        zh_review_focus=(
            "优先检查低质量分或带转换警告的文件。",
            "导入前确认标题层级和切块边界是否合理。",
            "抽查生成的 Markdown 是否和原文件内容一致。",
        ),
        handoff_steps=(
            "Open conversion_report.md and confirm the success rate.",
            "Open review_checklist.md and resolve flagged files.",
            "Import the vendor starter file that matches the target knowledge-base system.",
            "Run a small retrieval test before importing a larger document folder.",
        ),
        zh_handoff_steps=(
            "打开 conversion_report.md，确认整体转换成功率。",
            "打开 review_checklist.md，处理被标记的文件。",
            "根据目标知识库系统选择对应的导入文件。",
            "正式批量导入前，先做一轮小范围问答检索测试。",
        ),
    ),
    "enterprise-policy": WorkflowTemplate(
        key="enterprise-policy",
        name="Enterprise policy knowledge base",
        zh_name="企业制度知识库",
        description="Best for HR policies, internal rules, SOPs, and compliance manuals.",
        zh_description="适合 HR 制度、内部规章、SOP 和合规手册。",
        max_chunk_chars=1100,
        review_focus=(
            "Confirm every policy section keeps its heading path.",
            "Review short chunks because policy exceptions often live in small paragraphs.",
            "Check dates, approval owners, and compliance wording before import.",
        ),
        zh_review_focus=(
            "确认每个制度章节都保留了正确的标题路径。",
            "重点检查短切块，因为制度例外和审批条件常写在短段落里。",
            "导入前核对日期、负责人和合规表述。",
        ),
        handoff_steps=(
            "Group source files by department or policy area before a full run.",
            "Review flagged short chunks and merge source sections when needed.",
            "Import chunks with heading_path metadata enabled in the target RAG system.",
            "Ask domain owners to test questions about eligibility, exceptions, and approval flow.",
        ),
        zh_handoff_steps=(
            "正式处理前，先按部门或制度类型整理源文件。",
            "检查被标记的短切块，必要时合并源文件章节。",
            "导入时保留 heading_path 元数据，方便回答时定位制度章节。",
            "让业务负责人测试资格、例外情况和审批流程相关问题。",
        ),
    ),
    "support-faq": WorkflowTemplate(
        key="support-faq",
        name="Support FAQ knowledge base",
        zh_name="客服 FAQ 知识库",
        description="Best for ticket answers, help-center pages, troubleshooting notes, and FAQs.",
        zh_description="适合工单答案、帮助中心页面、故障排查说明和 FAQ。",
        max_chunk_chars=900,
        review_focus=(
            "Check that each question-answer pair stays together.",
            "Review repeated lines from exported ticket systems.",
            "Remove obsolete answers before importing into a customer-facing assistant.",
        ),
        zh_review_focus=(
            "确认每组问题和答案没有被切散。",
            "检查从工单系统导出的重复行。",
            "导入面向客户的助手前，移除过期答案。",
        ),
        handoff_steps=(
            "Clean duplicate ticket exports before batch conversion.",
            "Review the checklist for repeated or tiny chunks.",
            "Import FAQ chunks with filename and heading metadata.",
            "Test customer questions that contain vague wording, typos, or product aliases.",
        ),
        zh_handoff_steps=(
            "批量转换前先清理重复工单和过期回答。",
            "重点检查复核清单里的重复切块和过短切块。",
            "导入 FAQ 时保留文件名和标题元数据。",
            "用含糊表述、错别字和产品别名来测试客服问答效果。",
        ),
    ),
    "product-manual": WorkflowTemplate(
        key="product-manual",
        name="Product manual knowledge base",
        zh_name="产品手册知识库",
        description="Best for manuals, release notes, onboarding guides, and training material.",
        zh_description="适合产品手册、版本说明、入门指南和培训资料。",
        max_chunk_chars=1600,
        review_focus=(
            "Check tables, numbered procedures, and warnings against the source.",
            "Confirm long sections are split around task boundaries.",
            "Review image-heavy or scan-heavy files before import.",
        ),
        zh_review_focus=(
            "对照原文件检查表格、编号步骤和警示说明。",
            "确认长章节按任务边界合理拆分。",
            "重点复核图片多或扫描件较多的文件。",
        ),
        handoff_steps=(
            "Run a small sample from each product line first.",
            "Inspect table-heavy files in review_checklist.md.",
            "Import with source filename metadata so answers can cite manuals.",
            "Test procedural questions that require step order and safety notes.",
        ),
        zh_handoff_steps=(
            "每条产品线先抽取一小批样本试跑。",
            "优先检查 review_checklist.md 中表格较多的文件。",
            "导入时保留源文件名，方便回答引用具体手册。",
            "测试需要步骤顺序和安全提示的操作类问题。",
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


def template_name(template: WorkflowTemplate, language: str = "en") -> str:
    return template.zh_name if language == "zh-CN" else template.name


def template_description(template: WorkflowTemplate, language: str = "en") -> str:
    return template.zh_description if language == "zh-CN" else template.description


def template_review_focus(template: WorkflowTemplate, language: str = "en") -> tuple[str, ...]:
    return template.zh_review_focus if language == "zh-CN" else template.review_focus


def template_handoff_steps(template: WorkflowTemplate, language: str = "en") -> tuple[str, ...]:
    return template.zh_handoff_steps if language == "zh-CN" else template.handoff_steps
