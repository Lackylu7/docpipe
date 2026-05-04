from docpipe.templates import get_template, list_templates, template_name


def test_templates_include_commercial_workflows():
    keys = {template.key for template in list_templates()}

    assert {"general", "enterprise-policy", "support-faq", "product-manual"} <= keys


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
