# DOE Platform v3

Professional agency-ready DOE Framework platform for local service businesses.

Default client: Jiggaman Bonding.

## v3 Adds
- Secure login
- Multi-client-ready config
- Agency dashboard
- Client dashboard
- CRM pipeline
- Lead detail fields
- Event tracking
- AI command center
- Report center
- Monthly PDF report
- Render deployment files
- GTM/GA4 tracking documentation

## Default Login
Username:
admin

Password:
change-me-now

Change this in `config.py` before selling to a client.

## Run locally
```bash
pip install -r requirements.txt
python app.py
```

## Render
Build:
```text
pip install -r requirements.txt
```

Start:
```text
gunicorn app:app
```

## Main Pages
- /
- /login
- /dashboard
- /crm
- /reports
- /ai
- /clients
