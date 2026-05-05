from __future__ import annotations

import json
import random
import zlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SyntheticDatasetSummary:
    output_dir: str
    file_count: int
    categories: tuple[str, ...]


@dataclass(frozen=True)
class SyntheticCategory:
    key: str
    folder: str
    title: str
    owner: str
    topics: tuple[str, ...]


CATEGORIES: tuple[SyntheticCategory, ...] = (
    SyntheticCategory(
        key="policy",
        folder="01-policy",
        title="员工制度",
        owner="人力行政部",
        topics=("入职", "考勤", "报销", "审批", "信息安全"),
    ),
    SyntheticCategory(
        key="support",
        folder="02-support",
        title="客服知识库",
        owner="客户成功部",
        topics=("账号登录", "发票申请", "退款处理", "权限开通", "故障排查"),
    ),
    SyntheticCategory(
        key="product",
        folder="03-product",
        title="产品手册",
        owner="产品运营部",
        topics=("功能配置", "版本说明", "使用限制", "数据同步", "常见问题"),
    ),
    SyntheticCategory(
        key="sales",
        folder="04-sales",
        title="销售资料",
        owner="销售 enablement",
        topics=("客户画像", "竞品对比", "报价口径", "异议处理", "演示脚本"),
    ),
    SyntheticCategory(
        key="finance",
        folder="05-finance",
        title="财务资料",
        owner="财务部",
        topics=("付款流程", "预算科目", "月结说明", "合同回款", "费用分类"),
    ),
    SyntheticCategory(
        key="legal",
        folder="06-legal",
        title="合同条款",
        owner="法务部",
        topics=("保密条款", "服务范围", "违约责任", "数据处理", "续约终止"),
    ),
    SyntheticCategory(
        key="training",
        folder="07-training",
        title="培训资料",
        owner="培训发展部",
        topics=("新人训练", "岗位认证", "考试标准", "导师机制", "复盘记录"),
    ),
    SyntheticCategory(
        key="operations",
        folder="08-operations",
        title="运营SOP",
        owner="运营管理部",
        topics=("上线检查", "质量抽检", "告警处理", "交接流程", "复盘改进"),
    ),
)

EXTENSIONS = (".md", ".txt", ".csv", ".html", ".json")


def generate_synthetic_dataset(
    output_dir: Path,
    file_count: int = 80,
    seed: int = 7,
) -> SyntheticDatasetSummary:
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    for index in range(1, file_count + 1):
        category = CATEGORIES[(index - 1) % len(CATEGORIES)]
        extension = EXTENSIONS[(index - 1) % len(EXTENSIONS)]
        folder = output_dir / category.folder
        folder.mkdir(parents=True, exist_ok=True)
        topic = category.topics[(index - 1) % len(category.topics)]
        path = folder / f"{index:03d}-{category.key}-{_slug(topic)}{extension}"
        path.write_text(
            _render_file(index, category, topic, extension, rng),
            encoding="utf-8",
        )

    return SyntheticDatasetSummary(
        output_dir=str(output_dir),
        file_count=file_count,
        categories=tuple(category.key for category in CATEGORIES),
    )


def _render_file(
    index: int,
    category: SyntheticCategory,
    topic: str,
    extension: str,
    rng: random.Random,
) -> str:
    if extension == ".csv":
        return _render_csv(index, category, topic, rng)
    if extension == ".html":
        return _render_html(index, category, topic)
    if extension == ".json":
        return _render_json(index, category, topic)
    return _render_markdown(index, category, topic, plain_text=extension == ".txt")


def _render_markdown(
    index: int,
    category: SyntheticCategory,
    topic: str,
    plain_text: bool = False,
) -> str:
    heading = f"{category.title} - {topic} #{index:03d}"
    lines = [
        heading if plain_text else f"# {heading}",
        "",
        f"负责人：{category.owner}",
        f"适用范围：{topic}相关流程、问答、风险提醒和交付检查。",
        "",
        "## 背景",
        f"{topic}资料用于帮助企业团队在导入知识库前统一口径，减少重复沟通。",
        "该资料包含流程说明、注意事项、边界条件和人工复核建议。",
        "",
        "## 标准流程",
        "1. 收集来源文件并确认版本。",
        "2. 对照业务负责人给出的最新口径进行整理。",
        "3. 将可直接回答的问题写成清晰段落。",
        "4. 将需要人工判断的部分标记为复核项。",
        "",
        "## 质量检查表",
        "",
        "| 检查项 | 标准 | 负责人 |",
        "| --- | --- | --- |",
        f"| {topic}口径 | 与当前政策一致 | {category.owner} |",
        "| 表格信息 | 数字、日期、权限不遗漏 | 资料管理员 |",
        "| 导入前复核 | 低分和警告项必须处理 | AI项目负责人 |",
        "",
        "## 常见问题",
        f"问：{topic}相关内容是否可以直接导入？",
        "答：可以作为初始资料，但正式上线前必须抽样检查 Markdown、表格和切块边界。",
    ]
    if plain_text:
        return "\n".join(line.lstrip("# ").replace("|", " ") for line in lines)
    return "\n".join(lines)


def _render_csv(
    index: int,
    category: SyntheticCategory,
    topic: str,
    rng: random.Random,
) -> str:
    rows = ["question,answer,owner,priority"]
    for offset in range(1, 8):
        priority = rng.choice(("high", "medium", "low"))
        rows.append(
            f"{topic}问题{offset},"
            f"{category.title}{index:03d} 中关于 {topic} 的标准回答 {offset},"
            f"{category.owner},{priority}"
        )
    return "\n".join(rows)


def _render_html(index: int, category: SyntheticCategory, topic: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>{category.title} - {topic}</title></head>
<body>
  <h1>{category.title} - {topic} #{index:03d}</h1>
  <p>负责人：{category.owner}</p>
  <h2>适用场景</h2>
  <p>{topic}资料适合导入企业知识库，用于内部问答、客服辅助和交付检查。</p>
  <h2>复核重点</h2>
  <ul>
    <li>确认标题层级完整。</li>
    <li>确认表格和列表没有丢失。</li>
    <li>确认过期信息已经移除。</li>
  </ul>
</body>
</html>
"""


def _render_json(index: int, category: SyntheticCategory, topic: str) -> str:
    payload = {
        "id": f"{category.key}-{index:03d}",
        "title": f"{category.title} - {topic}",
        "owner": category.owner,
        "topic": topic,
        "sections": [
            {"heading": "目标", "body": f"整理 {topic} 资料并生成可复核知识库内容。"},
            {"heading": "风险", "body": "导入前需要检查日期、数字、表格和审批口径。"},
            {"heading": "验收", "body": "抽样问答能够定位到正确来源文件和标题路径。"},
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _slug(value: str) -> str:
    slug = "".join(char if char.isascii() and char.isalnum() else "-" for char in value).strip("-")
    return slug or f"topic-{zlib.crc32(value.encode('utf-8')) % 10000:04d}"
