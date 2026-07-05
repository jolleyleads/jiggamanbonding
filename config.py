import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-this")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me-now")

GA4_PROPERTY_ID = os.getenv("GA4_PROPERTY_ID", "")

CLIENTS = {
    "jiggaman": {
        "client_id": "jiggaman",
        "business_name": "Jiggaman Bonding",
        "industry": "Bail Bonds",
        "phone": "757-698-0355",
        "phone_raw": "7576980355",
        "email": "jiggamanbonding@gmail.com",
        "public_website": "https://jiggamanbonding-1.onrender.com",
        "dashboard_url": "https://jiggamanbonding-dashboard.onrender.com",
        "gtm_id": "GTM-T6KTLFGG",
        "ga4_measurement_id": "G-RXL701PE9T",
        "ga4_property_id": GA4_PROPERTY_ID,
        "cities": ["Portsmouth", "Suffolk", "Norfolk", "Chesapeake", "Newport News", "Hampton"],
        "primary_conversions": [
            "phone_call_click",
            "text_message_click",
            "email_click",
            "bail_form_submit",
            "ai_intake_submit"
        ],
        "secondary_actions": [
            "jail_search_click",
            "maps_click",
            "review_click",
            "live_chat_click"
        ]
    }
}
