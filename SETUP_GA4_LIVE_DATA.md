# Connect Live GA4 Data

## Step 1
Find your GA4 Property ID.

Go to:
GA4 > Admin > Property Details > Property ID

This is numeric. It is NOT your Measurement ID.

Measurement ID:
G-RXL701PE9T

Property ID:
Usually a number like 123456789.

## Step 2
Create a Google Cloud Service Account.

Enable:
Google Analytics Data API

## Step 3
Download service account JSON.

## Step 4
In GA4 Admin > Property Access Management:
Add the service account email as Viewer.

## Step 5
In Render > Dashboard Web Service > Environment, add:

GA4_PROPERTY_ID=your_numeric_property_id

GOOGLE_APPLICATION_CREDENTIALS_JSON=paste_entire_service_account_json_here

SECRET_KEY=make-this-long-and-random
ADMIN_USER=admin
ADMIN_PASSWORD=your-secure-password

## Step 6
Redeploy Render.

## Result
Dashboard will begin showing:
- Users
- Sessions
- Traffic sources
- Cities
- Devices
