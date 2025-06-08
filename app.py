import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, jsonify
from flask_talisman import Talisman
from datetime import datetime
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
Talisman(app)

DB_PATH = 'donations.db'
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")
BTC_WALLET = os.getenv("BTC_WALLET")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

# Create or update database
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                amount_usd REAL,
                amount_btc REAL,
                payment_method TEXT,
                txn_id TEXT,
                created_at TEXT
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_btc_invoice', methods=['POST'])
def create_btc_invoice():
    data = request.json
    usd_amount = data.get('amount')

    payload = {
        "price_amount": usd_amount,
        "price_currency": "usd",
        "pay_currency": "btc",
        "ipn_callback_url": "https://btc-donation-site.onrender.com/webhook",
        "order_description": "BTC Donation",
        "is_fixed_rate": True,
        "payout_address": BTC_WALLET
    }

    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }

    r = requests.post("https://api.nowpayments.io/v1/invoice", json=payload, headers=headers)
    return jsonify(r.json())

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    payment_status = data.get("payment_status")
    pay_amount = float(data.get("pay_amount", 0))
    price_amount = float(data.get("price_amount", 0))
    txn_id = data.get("payment_id")
    method = "btc" if data.get("pay_currency") == "btc" else "card"

    if payment_status in ("finished", "confirmed"):
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO donations (name, email, amount_usd, amount_btc, payment_method, txn_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get("buyer_name") or "BTC Donor",
                data.get("order_id") or "N/A",
                price_amount,
                pay_amount if method == "btc" else None,
                method,
                txn_id,
                datetime.utcnow().isoformat()
            ))
            conn.commit()

        if method == "card":
            send_email(data.get("order_id"), price_amount)

    return jsonify({"status": "ok"})

def send_email(email, amount):
    msg = EmailMessage()
    msg['Subject'] = 'Thank You for Your Donation!'
    msg['From'] = SMTP_USER
    msg['To'] = email
    msg.set_content(f'Thank you for donating ${amount:.2f}. Your support is appreciated!')

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@app.route('/admin')
def admin():
    method_filter = request.args.get('method', 'all')
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        if method_filter == 'all':
            c.execute("SELECT * FROM donations ORDER BY created_at DESC")
        else:
            c.execute("SELECT * FROM donations WHERE payment_method=? ORDER BY created_at DESC", (method_filter,))
        donations = c.fetchall()
    return render_template('admin.html', donations=donations)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
