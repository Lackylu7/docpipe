# Localization

DocPipe supports English and Simplified Chinese for the main Web UI, CLI demo output,
workflow template names, review checklist, handoff guide, and manifest metadata.

## Web UI

Open the Web app and choose `zh-CN` or `en` in the sidebar.

```powershell
python -m streamlit run src/docpipe/web.py
```

## CLI

Run the demo in Chinese:

```powershell
docpipe demo --language zh-CN
```

List templates in Chinese:

```powershell
docpipe templates --language zh-CN
```

Convert Chinese samples and write Chinese handoff files:

```powershell
docpipe convert .\samples-cn --workflow-template enterprise-policy --language zh-CN
```

## Included Chinese Samples

The `samples-cn/` folder includes starter Chinese documents for local testing:

- `企业制度.md`
- `客服FAQ.csv`
- `产品手册.txt`
