# app.py (Place this in C:\Users\Jason Peart\btc_payment_site)

from flask import Flask, request, render_template, redirect, url_for
import os
import requests
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from flask_talisman import Talisman

# Load environment variables
load_dotenv()

app = Flask(__name__)
Talisman(app)

# Config from .env
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")
BTC_WALLET_ADDRESS = os.getenv("BTC_WALLET_ADDRESS")
NOWPAYMENTS_TEST_MODE = os.getenv("NOWPAYMENTS_TEST_MODE", "true").lower() == "true"
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/donorbox-webhook", methods=["POST"])
def donorbox_webhook():
    try:
        data = request.json
        amount = data.get("amount", "0")
        donor_email = data.get("donor", {}).get("email", "unknown")

        # Create payout via NOWPayments
        headers = {
            "x-api-key": NOWPAYMENTS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "amount": amount,
            "currency": "usd",
            "payee_address": BTC_WALLET_ADDRESS,
            "payout_currency": "btc",
            "is_fee_paid_by_user": True,
            "test_mode": NOWPAYMENTS_TEST_MODE
        }
        payout_res = requests.post("https://api.nowpayments.io/v1/payout", headers=headers, json=payload)
        payout_res.raise_for_status()

        notify_email(f"BTC Donation Sent", f"Donor: {donor_email}\nAmount: ${amount}\nStatus: Success")
        return {"status": "success"}, 200

    except Exception as e:
        notify_email("Donation Processing Failed", str(e))
        return {"status": "error", "message": str(e)}, 500

def notify_email(subject, body):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        with open("email_errors.log", "a") as log:
            log.write(f"Failed to send email: {e}\n")

@app.route("/admin")
def admin():
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
