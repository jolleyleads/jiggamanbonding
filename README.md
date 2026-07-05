# DOE Platform v4

Next upgrade for the Jiggaman Bonding DOE Framework platform.

## v4 Adds
- Environment-based configuration
- Safer admin login using hashed password support
- Live GA4 integration structure
- GA4 service placeholder
- Multi-client configuration
- Cleaner dashboard metrics flow
- Setup notes for Google Analytics Data API
- Render environment variable guide

## Default URLs
Public site:
https://jiggamanbonding-1.onrender.com

Dashboard:
https://jiggamanbonding-dashboard.onrender.com

## Required Render Environment Variables

Set these in Render > Environment:

SECRET_KEY=change-this-to-any-long-random-text
ADMIN_USER=admin
ADMIN_PASSWORD=change-me-now
GA4_PROPERTY_ID=
GOOGLE_APPLICATION_CREDENTIALS_JSON=

## Important
GA4_PROPERTY_ID is not the same as your Measurement ID.

Measurement ID:
G-RXL701PE9T

Property ID is numeric and found in:
GA4 > Admin > Property Details > Property ID

## Run locally
```bash
pip install -r requirements.txt
python app.py
```

## Render
Build command:
```text
pip install -r requirements.txt
```

Start command:
```text
gunicorn app:app
```
