from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db, init_db
from models import Booking
from config import ADMIN_PASSWORD, PRICE_PER_HOUR, MIN_HOURS
from booking_logic import is_time_conflict, is_within_operating_hours, is_within_lead_time, is_valid_start_time, format_time_12h
from datetime import datetime, timedelta
from ai_service import get_ai_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import random
import string
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:5173",
            "https://football-booking-system-rn.vercel.app"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "X-ADMIN-PASSWORD"]
    }
})

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],  
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///football_booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)


def generate_reference():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        ref = f"FP-{datetime.utcnow().strftime('%Y%m%d-%H%M')}-{code}"
        if not Booking.query.filter_by(reference=ref).first():
            return ref

@app.route("/api/book", methods=["POST"])
@limiter.limit("10 per minute;50 per day")
def book():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        name = data.get('name') or data.get('fullName')
        phone = data.get('phone') or data.get('phoneNumber')
        date_str = data.get('date')
        start_time_str = data.get('start_time') or data.get('startTime')

        duration = data.get('duration') or data.get('hours')

        if not all([name, phone, date_str, start_time_str, duration]):
            missing = []
            if not name: missing.append('name/fullName')
            if not phone: missing.append('phone/phoneNumber')
            if not date_str: missing.append('date')
            if not start_time_str: missing.append('start_time/startTime')
            if not duration: missing.append('duration/hours')
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        if isinstance(duration, str):
            hours = int(''.join(filter(str.isdigit, duration)))
        else:
            hours = int(duration)

    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400

    if hours < MIN_HOURS:
        return jsonify({"error": f"Minimum booking is {MIN_HOURS} hour(s)"}), 400

    try:
        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
    except ValueError as e:
        return jsonify({"error": f"Invalid date or time format: {str(e)}"}), 400

    is_valid, reason = is_valid_start_time(start_time)
    if not is_valid:
        return jsonify({"error": reason}), 400
    
    start_dt = datetime.combine(booking_date, start_time)
    end_dt = start_dt + timedelta(hours=hours)
    is_valid, reason = is_within_operating_hours(booking_date, start_time, end_dt)
    if not is_valid:
        return jsonify({"error": reason}), 400
    is_valid, reason = is_within_lead_time(start_dt)
    if not is_valid:
        return jsonify({"error": reason}), 400
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

    try:
        db.session.add(new_booking)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify({
        "success": True,
        "message": "Booking created successfully",
        "booking": {
            "name": name,
            "phone": phone,
            "date": date_str,
            "time": f"{format_time_12h(start_time)} - {format_time_12h(end_time)}",
            "hours": hours,
            "price": price,
            "reference": reference,
            "status": "Pending"
        },
        "payment_details": {
            "bank": "Access Bank",
            "account_name": "Elite Football Pitch",
            "account_number": "0123456789"
        }
    }), 201


@app.route("/api/admin/bookings", methods=["GET"])
@limiter.limit("3 per minute;15 per hour")
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
            "time": f"{format_time_12h(b.start_time)} - {format_time_12h(b.end_time)}",
            "hours": b.hours,
            "price": b.price,
            "reference": b.reference,
            "status": b.status
        })
    return jsonify(results)


@app.route("/api/admin/confirm/<reference>", methods=["POST"])
@limiter.limit("3 per minute;15 per hour")
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

@app.route("/api/admin/booking/<reference>", methods=["DELETE"])
@limiter.limit("3 per minute;15 per hour")
def delete_booking(reference):
    admin_pass = request.headers.get("X-ADMIN-PASSWORD")
    if admin_pass != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized access"}), 401

    booking = Booking.query.filter_by(reference=reference).first()
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    db.session.delete(booking)
    db.session.commit()

    return jsonify({"message": f"Booking {reference} deleted successfully"})

@app.route("/api/ai/chat", methods=["POST"])
@limiter.limit("6 per minute")
def ai_chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "A 'message' field is required."}), 400

    user_message = data["message"].strip() if isinstance(data["message"], str) else ""

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    if len(user_message) > 500:
        return jsonify({"error": "Message is too long. Please keep it under 500 characters."}), 400

    conversation_history = data.get("history", [])
    if not isinstance(conversation_history, list):
        conversation_history = []

    try:
        reply = get_ai_response(user_message, conversation_history)
        return jsonify({"reply": reply})
    except Exception as e:
        logger.error(f"AI chat failed: {e}")
        return jsonify({"error": "The AI assistant is currently unavailable. Please try again shortly."}), 500

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "running",
        "message": "Football Pitch Booking API",
        "endpoints": {
            "book": "/api/book (POST)",
            "view_bookings": "/api/admin/bookings (GET)",
            "confirm_booking": "/api/admin/confirm/<reference> (POST)"
        }
    })


if __name__ == "__main__":
    app.run(debug=True)
