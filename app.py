from flask import Flask, render_template, request, redirect, jsonify, send_file
import sqlite3, datetime, os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from config import CLIENT

app = Flask(__name__)
DB = "doe_platform.db"

PIPELINE = ["New", "Attempted Contact", "Qualified", "Bond Written", "Closed", "Lost"]

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_name TEXT,
        phone TEXT,
        date TEXT,
        lead_source TEXT,
        keyword TEXT,
        city TEXT,
        jail TEXT,
        bond_amount REAL,
        status TEXT,
        closed TEXT,
        revenue REAL,
        notes TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_name TEXT,
        event_date TEXT,
        page TEXT,
        source TEXT,
        city TEXT,
        device TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS ai_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT,
        task_output TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

@app.route("/")
def home():
    init_db()
    return render_template("index.html", client=CLIENT)

@app.route("/lead", methods=["POST"])
def create_lead():
    init_db()
    d = request.form
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO leads
    (lead_name, phone, date, lead_source, keyword, city, jail, bond_amount, status, closed, revenue, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        d.get("lead_name", ""),
        d.get("phone", ""),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        d.get("lead_source", "Website"),
        d.get("keyword", ""),
        d.get("city", ""),
        d.get("jail", ""),
        float(d.get("bond_amount") or 0),
        "New",
        "No",
        0,
        d.get("notes", "")
    ))
    conn.commit()
    conn.close()
    return redirect("/thank-you")

@app.route("/track", methods=["POST"])
def track_event():
    init_db()
    d = request.get_json() or {}
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT INTO events (event_name, event_date, page, source, city, device)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        d.get("event_name", ""),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        d.get("page", ""),
        d.get("source", "direct"),
        d.get("city", ""),
        d.get("device", "")
    ))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html", client=CLIENT)

def get_dashboard_data():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT * FROM leads ORDER BY id DESC")
    leads = c.fetchall()

    c.execute("SELECT event_name, COUNT(*) FROM events GROUP BY event_name")
    event_counts = dict(c.fetchall())

    c.execute("SELECT city, COUNT(*) FROM leads WHERE city != '' GROUP BY city ORDER BY COUNT(*) DESC")
    cities = c.fetchall()

    c.execute("SELECT lead_source, COUNT(*) FROM leads GROUP BY lead_source ORDER BY COUNT(*) DESC")
    sources = c.fetchall()

    total_leads = len(leads)
    closed_bonds = len([l for l in leads if str(l[10]).lower() == "yes" or str(l[9]).lower() == "closed"])
    revenue = sum([(l[11] or 0) for l in leads])
    conversion_rate = round((closed_bonds / total_leads) * 100, 2) if total_leads else 0

    best_source = sources[0][0] if sources else "Not enough data"
    worst_source = sources[-1][0] if sources else "Not enough data"
    best_city = cities[0][0] if cities else "Not enough data"

    metrics = {
        "users": "GA4 connected",
        "sessions": "GA4 connected",
        "traffic_source": sources,
        "cities": cities,
        "devices": "GA4 connected",
        "conversions": sum([event_counts.get(e, 0) for e in CLIENT["primary_conversions"]]),
        "phone_calls": event_counts.get("phone_call_click", 0),
        "texts": event_counts.get("text_message_click", 0),
        "emails": event_counts.get("email_click", 0),
        "forms": event_counts.get("bail_form_submit", 0),
        "ai_intake": event_counts.get("ai_intake_submit", 0),
        "jail_searches": event_counts.get("jail_search_click", 0),
        "maps_clicks": event_counts.get("maps_click", 0),
        "reviews": event_counts.get("review_click", 0),
        "live_chat": event_counts.get("live_chat_click", 0),
        "revenue": revenue,
        "closed_bonds": closed_bonds,
        "conversion_rate": conversion_rate,
        "best_source": best_source,
        "worst_source": worst_source,
        "best_city": best_city,
        "total_leads": total_leads
    }

    conn.close()
    return leads, metrics

@app.route("/dashboard")
def dashboard():
    init_db()
    leads, metrics = get_dashboard_data()
    return render_template("dashboard.html", client=CLIENT, leads=leads, metrics=metrics)

@app.route("/crm")
def crm():
    init_db()
    leads, metrics = get_dashboard_data()
    return render_template("crm.html", client=CLIENT, leads=leads, pipeline=PIPELINE)

@app.route("/ai")
def ai():
    init_db()
    leads, metrics = get_dashboard_data()
    recommendations = [
        f"Best current city: {metrics['best_city']}",
        "Push call and text buttons higher on the homepage.",
        "Create city landing pages for Portsmouth, Suffolk, Norfolk, Chesapeake, Newport News, and Hampton.",
        "Post Google Business Profile updates 3 times per week while waiting for ranking movement.",
        "Ask closed bond clients for reviews immediately after successful release.",
        "Use phone_call_click and text_message_click as the main lead quality indicators.",
        "Track source quality before spending money on ads."
    ]
    posts = {
        "gbp_post": "Need bail help fast? Jiggaman Bonding is ready to help families move quickly when every minute matters. Call 757-698-0355.",
        "facebook_post": "When someone you love needs bail help, speed matters. Jiggaman Bonding is here for calls, texts, and fast response.",
        "faq": "Q: How fast can a bail bondsman help? A: Timing depends on the jail and bond status, but calling immediately gives the agent the best chance to move fast.",
        "blog_topic": "What to Do First When Someone Is Arrested in Hampton Roads"
    }
    return render_template("ai.html", client=CLIENT, recommendations=recommendations, posts=posts)

@app.route("/monthly-report")
def monthly_report():
    init_db()
    leads, metrics = get_dashboard_data()
    path = "doe_monthly_report.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path)
    story = [
        Paragraph(f"{CLIENT['business_name']} Monthly DOE Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph("Core Metrics", styles["Heading2"]),
        Paragraph(f"Total Leads: {metrics['total_leads']}", styles["BodyText"]),
        Paragraph(f"Phone Calls: {metrics['phone_calls']}", styles["BodyText"]),
        Paragraph(f"Texts: {metrics['texts']}", styles["BodyText"]),
        Paragraph(f"Emails: {metrics['emails']}", styles["BodyText"]),
        Paragraph(f"Forms: {metrics['forms']}", styles["BodyText"]),
        Paragraph(f"Revenue: ${metrics['revenue']}", styles["BodyText"]),
        Paragraph(f"Closed Bonds: {metrics['closed_bonds']}", styles["BodyText"]),
        Paragraph(f"Conversion Rate: {metrics['conversion_rate']}%", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("Recommendations", styles["Heading2"]),
        Paragraph("Focus on calls, texts, Google Maps clicks, Google reviews, and city-based local SEO content.", styles["BodyText"]),
    ]
    doc.build(story)
    return send_file(path, as_attachment=True)

@app.route("/api/metrics")
def api_metrics():
    init_db()
    leads, metrics = get_dashboard_data()
    return jsonify(metrics)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000, debug=True)
