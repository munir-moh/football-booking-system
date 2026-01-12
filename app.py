# app.py
from flask import Flask, request, jsonify
from database import db, init_db
from models import Booking
from config import ADMIN_PASSWORD, PRICE_PER_HOUR, MIN_HOURS
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///football_booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

def generate_reference():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        ref = f"FP-{datetime.utcnow().strftime('%Y%m%d-%H%M')}-{code}"
        if not Booking.query.filter_by(reference=ref).first():
            return ref

def is_time_conflict(date, start_time, end_time):
    bookings = Booking.query.filter_by(date=date).all()
    for b in bookings:
        existing_start = datetime.combine(b.date, b.start_time)
        existing_end = datetime.combine(b.date, b.end_time)
        new_start = datetime.combine(date, start_time)
        new_end = datetime.combine(date, end_time)
        if new_start < existing_end and new_end > existing_start:
            return True
    return False


@app.route("/api/book", methods=["POST"])
def book():
    data = request.get_json()
    try:
        name = data['name']
        phone = data['phone']
        date_str = data['date']
        start_time_str = data['start_time']
        hours = int(data.get('hours', 1))
    except KeyError:
        return jsonify({"error": "Missing required fields"}), 400

    if hours < MIN_HOURS:
        return jsonify({"error": f"Minimum booking is {MIN_HOURS} hour(s)"}), 400

    try:
        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
    except ValueError:
        return jsonify({"error": "Invalid date or time format"}), 400

    start_dt = datetime.combine(booking_date, start_time)
    end_dt = start_dt + timedelta(hours=hours)
    end_time = end_dt.time()

    if is_time_conflict(booking_date, start_time, end_time):
        return jsonify({"error": "Time slot already booked"}), 400

    price = PRICE_PER_HOUR * hours

    reference = generate_reference()

    new_booking = Booking(
        name=name,
        phone=phone,
        date=booking_date,
        start_time=start_time,
        end_time=end_time,
        hours=hours,
        price=price,
        reference=reference,
        status="Pending"
    )
    db.session.add(new_booking)
    db.session.commit()

    return jsonify({
        "message": "Booking created successfully",
        "name": name,
        "phone": phone,
        "date": date_str,
        "time": f"{start_time_str} - {end_time.strftime('%H:%M')}",
        "hours": hours,
        "price": price,
        "reference": reference,
        "payment_details": {
            "bank": "Access Bank",
            "account_name": "Elite Football Pitch",
            "account_number": "0123456789"
        },
        "status": "Pending"
    })


@app.route("/api/admin/bookings", methods=["GET"])
def view_bookings():
    admin_pass = request.headers.get("X-ADMIN-PASSWORD")
    if admin_pass != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized access"}), 401

    bookings = Booking.query.order_by(Booking.date, Booking.start_time).all()
    results = []
    for b in bookings:
        results.append({
            "name": b.name,
            "phone": b.phone,
            "date": b.date.strftime("%Y-%m-%d"),
            "time": f"{b.start_time.strftime('%H:%M')} - {b.end_time.strftime('%H:%M')}",
            "hours": b.hours,
            "price": b.price,
            "reference": b.reference,
            "status": b.status
        })
    return jsonify(results)

@app.route("/api/admin/confirm/<reference>", methods=["POST"])
def confirm_booking(reference):
    admin_pass = request.headers.get("X-ADMIN-PASSWORD")
    if admin_pass != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized access"}), 401

    booking = Booking.query.filter_by(reference=reference).first()
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    booking.status = "Confirmed"
    db.session.commit()

    return jsonify({
        "message": f"Booking {reference} confirmed",
        "status": "Confirmed"
    })

@app.route("/ping")
def ping():
    return "pong"


if __name__ == "__main__":
    app.run(debug=True)
