from flask import Flask, render_template, request, redirect, jsonify, send_file, session, url_for
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, datetime, os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from config import SECRET_KEY, ADMIN_USER, ADMIN_PASSWORD, CLIENTS
from services.ga4_service import get_ga4_summary

app = Flask(__name__)
app.secret_key = SECRET_KEY

DB = "doe_platform_v4.db"
DEFAULT_CLIENT_ID = "jiggaman"

PIPELINE = ["New", "Attempted Contact", "Qualified", "Bond Written", "Closed", "Lost"]

def current_client():
    client_id = session.get("client_id", DEFAULT_CLIENT_ID)
    return CLIENTS.get(client_id, CLIENTS[DEFAULT_CLIENT_ID])

def password_ok(raw_password):
    stored = ADMIN_PASSWORD
    if stored.startswith("pbkdf2:") or stored.startswith("scrypt:"):
        return check_password_hash(stored, raw_password)
    return raw_password == stored

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT,
        lead_name TEXT,
        phone TEXT,
        email TEXT,
        date TEXT,
        lead_source TEXT,
        keyword TEXT,
        city TEXT,
        jail TEXT,
        bond_amount REAL,
        defendant_name TEXT,
        indemnitor_name TEXT,
        status TEXT,
        closed TEXT,
        revenue REAL,
        notes TEXT,
        last_followup TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT,
        event_name TEXT,
        event_date TEXT,
        page TEXT,
        source TEXT,
        city TEXT,
        device TEXT
    )
    """)

    conn.commit()
    conn.close()

def db_rows(query, params=()):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def db_exec(query, params=()):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

@app.route("/")
def public_site():
    init_db()
    client = CLIENTS[DEFAULT_CLIENT_ID]
    return render_template("public_site.html", client=client)

@app.route("/login", methods=["GET", "POST"])
def login():
    init_db()
    error = None
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USER and password_ok(request.form.get("password", "")):
            session["logged_in"] = True
            session["client_id"] = DEFAULT_CLIENT_ID
            return redirect("/dashboard")
        error = "Invalid login."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/lead", methods=["POST"])
def create_lead():
    init_db()
    client = CLIENTS[DEFAULT_CLIENT_ID]
    d = request.form

    db_exec("""
    INSERT INTO leads
    (client_id, lead_name, phone, email, date, lead_source, keyword, city, jail, bond_amount,
     defendant_name, indemnitor_name, status, closed, revenue, notes, last_followup)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        client["client_id"],
        d.get("lead_name", ""),
        d.get("phone", ""),
        d.get("email", ""),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        d.get("lead_source", "Website"),
        d.get("keyword", ""),
        d.get("city", ""),
        d.get("jail", ""),
        float(d.get("bond_amount") or 0),
        d.get("defendant_name", ""),
        d.get("indemnitor_name", ""),
        "New",
        "No",
        0,
        d.get("notes", ""),
        ""
    ))
    return redirect("/thank-you")

@app.route("/track", methods=["POST"])
def track_event():
    init_db()
    client = CLIENTS[DEFAULT_CLIENT_ID]
    d = request.get_json() or {}

    db_exec("""
    INSERT INTO events (client_id, event_name, event_date, page, source, city, device)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        client["client_id"],
        d.get("event_name", ""),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        d.get("page", ""),
        d.get("source", "direct"),
        d.get("city", ""),
        d.get("device", "")
    ))

    return jsonify({"ok": True})

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html", client=CLIENTS[DEFAULT_CLIENT_ID])

def local_metrics(client_id):
    leads = db_rows("SELECT * FROM leads WHERE client_id=? ORDER BY id DESC", (client_id,))
    event_counts = dict(db_rows("SELECT event_name, COUNT(*) FROM events WHERE client_id=? GROUP BY event_name", (client_id,)))
    sources = db_rows("SELECT lead_source, COUNT(*) FROM leads WHERE client_id=? GROUP BY lead_source ORDER BY COUNT(*) DESC", (client_id,))
    cities = db_rows("SELECT city, COUNT(*) FROM leads WHERE client_id=? AND city != '' GROUP BY city ORDER BY COUNT(*) DESC", (client_id,))

    total_leads = len(leads)
    closed_bonds = len([l for l in leads if str(l[14]).lower() == "yes" or str(l[13]).lower() == "closed"])
    revenue = sum([(l[15] or 0) for l in leads])
    conversion_rate = round((closed_bonds / total_leads) * 100, 2) if total_leads else 0

    client = CLIENTS[client_id]
    conversions = sum([event_counts.get(e, 0) for e in client["primary_conversions"]])

    return leads, {
        "total_leads": total_leads,
        "conversions": conversions,
        "phone_calls": event_counts.get("phone_call_click", 0),
        "texts": event_counts.get("text_message_click", 0),
        "emails": event_counts.get("email_click", 0),
        "forms": event_counts.get("bail_form_submit", 0),
        "ai_intake": event_counts.get("ai_intake_submit", 0),
        "jail_searches": event_counts.get("jail_search_click", 0),
        "maps_clicks": event_counts.get("maps_click", 0),
        "reviews": event_counts.get("review_click", 0),
        "live_chat": event_counts.get("live_chat_click", 0),
        "closed_bonds": closed_bonds,
        "revenue": revenue,
        "conversion_rate": conversion_rate,
        "best_source": sources[0][0] if sources else "Not enough data",
        "worst_source": sources[-1][0] if sources else "Not enough data",
        "best_city": cities[0][0] if cities else "Not enough data",
        "lead_sources": sources,
        "lead_cities": cities
    }

def combined_metrics(client):
    leads, local = local_metrics(client["client_id"])
    ga4 = get_ga4_summary(client.get("ga4_property_id", ""))

    local["users"] = ga4.get("users", "Not connected")
    local["sessions"] = ga4.get("sessions", "Not connected")
    local["traffic_sources"] = ga4.get("traffic_sources", [])
    local["cities"] = ga4.get("cities", local.get("lead_cities", []))
    local["devices"] = ga4.get("devices", [])
    local["ga4_connected"] = ga4.get("connected", False)
    local["ga4_message"] = ga4.get("message", "")

    return leads, local

@app.route("/dashboard")
@login_required
def dashboard():
    init_db()
    client = current_client()
    leads, metrics = combined_metrics(client)
    return render_template("dashboard.html", client=client, leads=leads, metrics=metrics)

@app.route("/crm")
@login_required
def crm():
    init_db()
    client = current_client()
    leads, metrics = combined_metrics(client)
    return render_template("crm.html", client=client, leads=leads, metrics=metrics, pipeline=PIPELINE)

@app.route("/lead/<int:lead_id>/update", methods=["POST"])
@login_required
def update_lead(lead_id):
    d = request.form
    db_exec("""
    UPDATE leads SET status=?, closed=?, revenue=?, notes=?, last_followup=?
    WHERE id=?
    """, (
        d.get("status", "New"),
        d.get("closed", "No"),
        float(d.get("revenue") or 0),
        d.get("notes", ""),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        lead_id
    ))
    return redirect("/crm")

@app.route("/ai")
@login_required
def ai():
    client = current_client()
    leads, metrics = combined_metrics(client)

    recommendations = [
        f"GA4 Status: {metrics['ga4_message']}",
        f"Best source: {metrics['best_source']}",
        f"Best city: {metrics['best_city']}",
        "Push call and text buttons above the fold.",
        "Create location pages for each city target.",
        "Ask every closed client for a Google review.",
        "Use calls, texts, forms, and AI intake as primary lead KPIs."
    ]

    posts = {
        "gbp": f"Need bail help fast? {client['business_name']} helps families move quickly. Call {client['phone']}.",
        "facebook": f"When someone you love needs help, quick communication matters. {client['business_name']} is ready by call or text.",
        "faq": "Q: What should I have ready before calling? A: Name, jail, city, bond amount, and the best callback number.",
        "blog": "What to Do First After an Arrest in Hampton Roads",
        "review_response": "Thank you for trusting us during a stressful situation. We appreciate the opportunity to help."
    }

    return render_template("ai.html", client=client, metrics=metrics, recommendations=recommendations, posts=posts)

@app.route("/reports")
@login_required
def reports():
    client = current_client()
    leads, metrics = combined_metrics(client)
    return render_template("reports.html", client=client, metrics=metrics)

@app.route("/clients")
@login_required
def clients():
    return render_template("clients.html", clients=CLIENTS, active=current_client())

@app.route("/monthly-report")
@login_required
def monthly_report():
    client = current_client()
    leads, metrics = combined_metrics(client)
    path = "doe_platform_v4_monthly_report.pdf"

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path)
    story = [
        Paragraph(f"{client['business_name']} Monthly DOE Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph("Performance Summary", styles["Heading2"]),
        Paragraph(f"GA4 Status: {metrics['ga4_message']}", styles["BodyText"]),
        Paragraph(f"Users: {metrics['users']}", styles["BodyText"]),
        Paragraph(f"Sessions: {metrics['sessions']}", styles["BodyText"]),
        Paragraph(f"Total Leads: {metrics['total_leads']}", styles["BodyText"]),
        Paragraph(f"Phone Calls: {metrics['phone_calls']}", styles["BodyText"]),
        Paragraph(f"Texts: {metrics['texts']}", styles["BodyText"]),
        Paragraph(f"Emails: {metrics['emails']}", styles["BodyText"]),
        Paragraph(f"Forms: {metrics['forms']}", styles["BodyText"]),
        Paragraph(f"AI Intake: {metrics['ai_intake']}", styles["BodyText"]),
        Paragraph(f"Maps Clicks: {metrics['maps_clicks']}", styles["BodyText"]),
        Paragraph(f"Reviews: {metrics['reviews']}", styles["BodyText"]),
        Paragraph(f"Revenue: ${metrics['revenue']}", styles["BodyText"]),
        Paragraph(f"Closed Bonds: {metrics['closed_bonds']}", styles["BodyText"]),
        Paragraph(f"Conversion Rate: {metrics['conversion_rate']}%", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("Recommendations", styles["Heading2"]),
        Paragraph("Focus on calls, texts, bail forms, Google reviews, Google Maps clicks, and city-based SEO pages.", styles["BodyText"])
    ]
    doc.build(story)
    return send_file(path, as_attachment=True)

@app.route("/api/metrics")
@login_required
def api_metrics():
    client = current_client()
    leads, metrics = combined_metrics(client)
    return jsonify(metrics)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000, debug=True)
