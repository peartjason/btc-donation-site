from flask import Flask
from db import db, EmailLog  # Ensure EmailLog is defined in db.py
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("[*] Creating tables...")
    db.create_all()

    if not EmailLog.query.first():
        print("[*] Inserting sample email log...")
        sample = EmailLog(
            recipient='test@example.com',
            subject='Thank You for Your Donation!',
            body='<p>Test donation email receipt</p>'
        )
        db.session.add(sample)
        db.session.commit()

    print("[✓] EmailLog setup complete.")
