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
    "sales-enablement": WorkflowTemplate(
        key="sales-enablement",
        name="Sales enablement knowledge base",
        zh_name="销售赋能知识库",
        description="Best for sales playbooks, pitch decks, battlecards, pricing notes, and objection handling.",
        zh_description="适合销售手册、演示话术、竞品卡片、报价口径和客户异议处理。",
        max_chunk_chars=1000,
        review_focus=(
            "Check that pricing, discount, and competitor claims are current.",
            "Keep objection-handling answers close to the matching customer scenario.",
            "Review confidential customer names before sharing the export pack.",
        ),
        zh_review_focus=(
            "检查报价、折扣和竞品说法是否仍然有效。",
            "确认异议处理答案和对应客户场景没有被切散。",
            "对外交付前复核客户名称、合同金额等敏感信息。",
        ),
        handoff_steps=(
            "Group source files by product line, customer segment, or sales stage.",
            "Review battlecard and pricing chunks with the sales owner.",
            "Import filename and heading metadata so sales answers can cite the source.",
            "Test questions about competitor comparisons, objections, and pricing boundaries.",
        ),
        zh_handoff_steps=(
            "按产品线、客户类型或销售阶段整理源文件。",
            "让销售负责人复核竞品卡片和报价相关切块。",
            "导入时保留文件名和标题元数据，方便回答引用来源。",
            "测试竞品对比、异议处理和报价边界相关问题。",
        ),
    ),
    "legal-contract": WorkflowTemplate(
        key="legal-contract",
        name="Legal and contract knowledge base",
        zh_name="法务合同知识库",
        description="Best for contract templates, legal clauses, procurement terms, and risk review notes.",
        zh_description="适合合同模板、法务条款、采购条款、风险评审说明和审批口径。",
        max_chunk_chars=900,
        review_focus=(
            "Review dates, party names, liability caps, and termination clauses manually.",
            "Keep clause headings and numbering visible in each chunk.",
            "Flag anything that should remain legal advice rather than automated guidance.",
        ),
        zh_review_focus=(
            "人工复核日期、主体名称、责任上限和终止条款。",
            "确认条款标题和编号在切块中仍然清晰。",
            "标记必须由法务人工判断、不能自动回答的内容。",
        ),
        handoff_steps=(
            "Separate public templates from customer-specific signed contracts.",
            "Review the checklist with a legal owner before import.",
            "Add retrieval tests for liability, renewal, termination, and data-processing terms.",
            "Document which answers require legal escalation.",
        ),
        zh_handoff_steps=(
            "将通用模板和客户专属已签合同分开处理。",
            "导入前让法务负责人复核检查清单。",
            "补充责任、续约、终止、数据处理条款相关检索测试。",
            "明确哪些问题必须升级给法务人工处理。",
        ),
    ),
    "finance-report": WorkflowTemplate(
        key="finance-report",
        name="Finance and audit knowledge base",
        zh_name="财务审计知识库",
        description="Best for reimbursement rules, audit notes, budget reports, invoice SOPs, and finance FAQs.",
        zh_description="适合报销制度、审计说明、预算报告、发票SOP和财务常见问题。",
        max_chunk_chars=1000,
        review_focus=(
            "Check table-heavy files against the original source.",
            "Review all dates, amounts, tax rates, and account codes.",
            "Separate policy guidance from confidential financial statements.",
        ),
        zh_review_focus=(
            "重点对照原文件检查表格密集型资料。",
            "复核日期、金额、税率和科目代码。",
            "区分可问答的制度口径和不应外发的财务报表。",
        ),
        handoff_steps=(
            "Run a small table-heavy sample before a large folder.",
            "Ask finance owners to review low-score chunks and table warnings.",
            "Import only the approved guidance pack into customer-facing systems.",
            "Test reimbursement, invoice, and approval-limit questions.",
        ),
        zh_handoff_steps=(
            "大批量处理前先跑一小批表格密集样本。",
            "让财务负责人复核低分切块和表格警告。",
            "只把已批准的制度口径包导入面向用户的系统。",
            "测试报销、发票和审批额度相关问题。",
        ),
    ),
    "training-onboarding": WorkflowTemplate(
        key="training-onboarding",
        name="Training and onboarding knowledge base",
        zh_name="培训入职知识库",
        description="Best for onboarding guides, training scripts, certification material, and internal courses.",
        zh_description="适合新人入职、培训课件、岗位认证资料、内部课程和考试标准。",
        max_chunk_chars=1300,
        review_focus=(
            "Keep lesson objectives, steps, and assessment criteria together.",
            "Review outdated screenshots or references to older tools.",
            "Check whether training tasks should be split into smaller retrieval units.",
        ),
        zh_review_focus=(
            "确认课程目标、操作步骤和考核标准没有被拆散。",
            "复核过期截图、旧系统名称和旧流程。",
            "检查培训任务是否需要拆成更小的检索单元。",
        ),
        handoff_steps=(
            "Group materials by role, course, or learning path.",
            "Review procedural chunks with trainers or team leads.",
            "Import with heading metadata so answers can point to the right module.",
            "Test role-specific onboarding and certification questions.",
        ),
        zh_handoff_steps=(
            "按岗位、课程或学习路径整理资料。",
            "让培训负责人或团队主管复核流程类切块。",
            "导入时保留标题路径，方便回答定位到具体模块。",
            "测试岗位入职和认证考试相关问题。",
        ),
    ),
    "operations-sop": WorkflowTemplate(
        key="operations-sop",
        name="Operations SOP knowledge base",
        zh_name="运营SOP知识库",
        description="Best for daily operation procedures, incident playbooks, QA checklists, and handover notes.",
        zh_description="适合日常运营流程、故障预案、质检清单、交接说明和复盘资料。",
        max_chunk_chars=1050,
        review_focus=(
            "Keep trigger conditions, action steps, and escalation owners in the same chunk.",
            "Review incident procedures for outdated contacts or tools.",
            "Check handover notes for duplicated or temporary information.",
        ),
        zh_review_focus=(
            "确认触发条件、处理步骤和升级负责人尽量保留在同一切块。",
            "复核故障流程里的联系人、群组和工具是否过期。",
            "检查交接资料中的重复内容和临时信息。",
        ),
        handoff_steps=(
            "Group SOPs by operational scenario or escalation level.",
            "Review failed and low-score files with the operations owner.",
            "Import chunks with filename and heading_path metadata.",
            "Test incident, handover, escalation, and quality-check questions.",
        ),
        zh_handoff_steps=(
            "按运营场景或升级级别整理SOP。",
            "让运营负责人复核失败文件和低分文件。",
            "导入时保留文件名和 heading_path 元数据。",
            "测试故障、交接、升级和质检相关问题。",
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
