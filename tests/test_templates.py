from docpipe.templates import get_template, list_templates, template_name


def test_templates_include_commercial_workflows():
    keys = {template.key for template in list_templates()}

    assert {
        "general",
        "enterprise-policy",
        "support-faq",
        "product-manual",
        "sales-enablement",
        "legal-contract",
        "finance-report",
        "training-onboarding",
        "operations-sop",
    } <= keys


def test_get_template_rejects_unknown_key():
    try:
        get_template("missing")
    except ValueError as exc:
        assert "Unknown workflow template" in str(exc)
    else:
        raise AssertionError("Expected missing template to raise ValueError")


def test_template_has_chinese_display_name():
    template = get_template("enterprise-policy")

    assert template_name(template, "zh-CN") == "企业制度知识库"


def test_commercial_templates_have_actionable_guidance():
    for template in list_templates():
        assert template.max_chunk_chars >= 500
        assert len(template.review_focus) >= 3
        assert len(template.handoff_steps) >= 4
        assert len(template.zh_review_focus) == len(template.review_focus)
        assert len(template.zh_handoff_steps) == len(template.handoff_steps)
