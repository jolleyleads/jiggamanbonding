import os
import json

def get_ga4_summary(property_id):
    """
    Live GA4 reporting connector.

    This is built to fail safely if credentials are not connected yet.
    Once Google service account credentials and GA4 Property ID are added,
    this function can return live users, sessions, cities, devices,
    traffic sources, and event counts.
    """

    if not property_id:
        return {
            "connected": False,
            "message": "GA4 Property ID missing. Add GA4_PROPERTY_ID in Render environment variables.",
            "users": "Not connected",
            "sessions": "Not connected",
            "cities": [],
            "devices": [],
            "traffic_sources": [],
            "top_pages": []
        }

    creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")

    if not creds_json:
        return {
            "connected": False,
            "message": "Google credentials missing. Add GOOGLE_APPLICATION_CREDENTIALS_JSON in Render environment variables.",
            "users": "Not connected",
            "sessions": "Not connected",
            "cities": [],
            "devices": [],
            "traffic_sources": [],
            "top_pages": []
        }

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
        from google.oauth2 import service_account

        credentials_info = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        client = BetaAnalyticsDataClient(credentials=credentials)

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[
                Dimension(name="sessionDefaultChannelGroup"),
                Dimension(name="city"),
                Dimension(name="deviceCategory")
            ],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="sessions"),
                Metric(name="eventCount")
            ],
            date_ranges=[DateRange(start_date="30daysAgo", end_date="today")]
        )

        response = client.run_report(request)

        users = 0
        sessions = 0
        traffic_sources = {}
        cities = {}
        devices = {}

        for row in response.rows:
            channel = row.dimension_values[0].value
            city = row.dimension_values[1].value
            device = row.dimension_values[2].value

            active_users = int(row.metric_values[0].value)
            session_count = int(row.metric_values[1].value)

            users += active_users
            sessions += session_count

            traffic_sources[channel] = traffic_sources.get(channel, 0) + session_count
            cities[city] = cities.get(city, 0) + session_count
            devices[device] = devices.get(device, 0) + session_count

        return {
            "connected": True,
            "message": "GA4 connected.",
            "users": users,
            "sessions": sessions,
            "traffic_sources": sorted(traffic_sources.items(), key=lambda x: x[1], reverse=True),
            "cities": sorted(cities.items(), key=lambda x: x[1], reverse=True),
            "devices": sorted(devices.items(), key=lambda x: x[1], reverse=True),
            "top_pages": []
        }

    except Exception as e:
        return {
            "connected": False,
            "message": f"GA4 connection error: {str(e)}",
            "users": "Connection error",
            "sessions": "Connection error",
            "cities": [],
            "devices": [],
            "traffic_sources": [],
            "top_pages": []
        }
