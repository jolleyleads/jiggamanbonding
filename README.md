# DOE Framework Platform v2.0

Agency-grade local lead tracking platform for Jiggaman Bonding and future service-business clients.

## Includes
- Multi-client-ready Flask structure
- Jiggaman Bonding default client
- Login-ready admin dashboard structure
- Lead CRM pipeline
- SQLite database
- Event tracking endpoints
- GTM/GA4 event framework
- AI recommendation module placeholder
- Monthly PDF report generator
- Client onboarding config
- Render deployment files

## Default Client
Business: Jiggaman Bonding  
Phone: 757-698-0355  
Email: jiggamanbonding@gmail.com  
Website: https://jiggamanbonding-1.onrender.com  
GTM: GTM-T6KTLFGG  
GA4: G-RXL701PE9T  

## Run locally
```bash
pip install -r requirements.txt
python app.py
```

Open:
```text
http://127.0.0.1:10000
http://127.0.0.1:10000/dashboard
http://127.0.0.1:10000/crm
http://127.0.0.1:10000/ai
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
