import os
from flask import Flask, request, jsonify, render_template
import requests
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# Environment variables
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")
NOWPAYMENTS_TEST_MODE = os.getenv("NOWPAYMENTS_TEST_MODE", "true").lower() == "true"
BTC_WALLET_ADDRESS = os.getenv("BTC_WALLET_ADDRESS")

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
    data = request.json
    amount_usd = float(data.get("amount", 0))
    donor_name = data.get("donor", {}).get("name", "Anonymous")

    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "price_amount": amount_usd,
        "price_currency": "usd",
        "pay_currency": "btc",
        "payout_address": BTC_WALLET_ADDRESS,
        "is_fee_paid_by_user": True,
        "ipn_callback_url": "",
        "is_test": NOWPAYMENTS_TEST_MODE
    }

    response = requests.post("https://api.nowpayments.io/v1/payout", headers=headers, json=payload)
    result = response.json()

    if response.status_code == 200:
        btc_amount = result.get("pay_amount")
        notify_email(donor_name, amount_usd, btc_amount)
        return jsonify({
            "status": "BTC Sent (Test Mode)" if NOWPAYMENTS_TEST_MODE else "BTC Sent",
            "details": result
        }), 200
    else:
        return jsonify({"error": "NOWPayments failed", "details": result}), 400

def notify_email(name, usd, btc):
    try:
        msg = MIMEText(f"""New donation received:

Donor: {name}
Amount: ${usd}
BTC Sent: {btc}
""")
        msg["Subject"] = "New BTC Donation"
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Email notification failed: {e}")

@app.route("/admin")
def admin_dashboard():
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
