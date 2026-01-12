from database import db
from datetime import datetime

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    reference = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default="Pending")  # Pending / Confirmed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
