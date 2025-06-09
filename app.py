from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mail import Mail, Message
from db import EmailLog, Donation, db
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_default_secret")

# Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your_email@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your_password')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# Send email helper function
def send_confirmation_email(to, subject, html_body):
    msg = Message(subject, recipients=[to], html=html_body)
    mail.send(msg)

# Route to send test email (optional testing)
@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.json
    msg = Message("Thank You for Your Donation!",
                  recipients=[data['email']])
    msg.html = render_template("email_receipt.html", name=data['name'], amount=data['amount'], method=data['method'])
    mail.send(msg)

    # Optional: Log sent email to database
    email_log = EmailLog(
        recipient=data['email'],
        subject="Thank You for Your Donation!",
        body=msg.html
    )
    db.session.add(email_log)
    db.session.commit()

    return jsonify({"status": "sent"})

# Admin route to view all email logs
@app.route('/admin/emails')
def admin_emails():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    search = request.args.get('search', '')
    emails = EmailLog.query.filter(
        (EmailLog.recipient.like(f'%{search}%')) | 
        (EmailLog.subject.like(f'%{search}%'))
    ).order_by(EmailLog.timestamp.desc()).all()
    return render_template('admin_emails.html', emails=emails, search=search)

# Admin route to resend a specific email
@app.route('/admin/resend/<int:email_id>')
def resend_email(email_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    email = EmailLog.query.get_or_404(email_id)
    msg = Message(email.subject, recipients=[email.recipient], html=email.body)
    mail.send(msg)
    flash('Email resent successfully.', 'success')
    return redirect(url_for('admin_emails'))
