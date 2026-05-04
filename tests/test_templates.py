from docpipe.templates import get_template, list_templates


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
