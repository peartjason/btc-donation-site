from flask import Flask, request, render_template, redirect, url_for
from flask_talisman import Talisman
import sqlite3
import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)
Talisman(app)

DB_PATH = "donations.db"
THANK_YOU_LINK = "/thank-you"

# Ensure DB exists
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id TEXT,
            amount TEXT,
            currency TEXT,
            created_at TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Email (optional setup)
def send_email(to_email, subject, body):
    try:
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = to_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())
    except Exception as e:
        print(f"Email error: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Received Webhook:", data)

    payment_id = data.get("payment_id")
    amount = data.get("price_amount")
    currency = data.get("price_currency")
    email = data.get("order_description", "")  # optionally passed as description

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO donations (payment_id, amount, currency, created_at, email) VALUES (?, ?, ?, ?, ?)",
              (payment_id, amount, currency, datetime.utcnow().isoformat(), email))
    conn.commit()
    conn.close()

    # Optional: email receipt
    if email:
        send_email(email, "Thank you for your donation!", f"We received {amount} {currency}. Thank you!")

    return json.dumps({"status": "success"}), 200

@app.route("/admin")
def admin_dashboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT payment_id, amount, currency, created_at, email FROM donations ORDER BY created_at DESC")
    donations = c.fetchall()
    conn.close()
    return render_template("admin.html", donations=donations)

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
