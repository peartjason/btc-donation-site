from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class EmailLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    tx_id = db.Column(db.String(120), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

