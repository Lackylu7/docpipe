# Deployment Guide

DocPipe is designed for local-first enterprise use. Start with a private desktop or
server deployment before exposing it to a network.

## Windows Local App

Use Python 3.12.

```powershell
scripts\run_web.ps1
```

The script creates `.venv`, installs DocPipe, and starts the Streamlit UI.

## Docker

```powershell
docker compose up --build
```

Open:

```text
http://127.0.0.1:8501
```

`outputs/` and `data/` are mounted so conversion jobs remain on the host machine.

## Enterprise Notes

- Keep deployments private by default.
- Avoid uploading confidential documents to third-party services.
- Review `conversion_report.md` before importing converted chunks into a knowledge base.
- Back up `outputs/` if the reports become part of customer delivery evidence.

## Hardening Before External Access

- Add authentication in front of Streamlit.
- Put the app behind a reverse proxy with TLS.
- Restrict upload size and accepted extensions.
- Add per-user output folders.
- Centralize logs.
- Scan uploaded files before processing in shared environments.
