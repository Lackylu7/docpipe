from docpipe.i18n import t


def test_chinese_translation_lookup():
    assert t("settings", "zh-CN") == "设置"
