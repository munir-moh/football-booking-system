from datetime import datetime, timedelta
from models import Booking
from booking_logic import is_time_conflict, is_within_operating_hours
from pitch_info import PITCH_INFO
from config import PRICE_PER_HOUR, MIN_HOURS


def get_pitch_info():
    return PITCH_INFO


def get_pricing_info():
    return {
        "price_per_hour": PRICE_PER_HOUR,
        "currency": "NGN",
        "minimum_booking_hours": MIN_HOURS
    }


def check_pitch_availability(date, start_time, hours):
    try:
        booking_date = datetime.strptime(date, "%Y-%m-%d").date()
        start = datetime.strptime(start_time, "%H:%M").time()
        hours = int(hours)
    except (ValueError, TypeError):
        return {"available": False, "error": "Invalid date, time, or hours format."}

    if hours < MIN_HOURS:
        return {"available": False, "error": f"Minimum booking is {MIN_HOURS} hour(s)."}

    start_dt = datetime.combine(booking_date, start)
    end_dt = start_dt + timedelta(hours=hours)
    is_valid, reason = is_within_operating_hours(booking_date, start, end_dt)
    if not is_valid:
        return {"available": False, "error": reason}
    end_time = end_dt.time()

    if is_time_conflict(booking_date, start, end_time):
        return {"available": False, "reason": "That time slot overlaps with an existing booking."}

    return {
        "available": True,
        "date": date,
        "start_time": start_time,
        "end_time": end_time.strftime("%H:%M"),
        "hours": hours,
        "price": PRICE_PER_HOUR * hours
    }


def get_booking_by_reference(reference):
    booking = Booking.query.filter_by(reference=reference).first()
    if not booking:
        return {"found": False, "error": "No booking found with that reference."}

    return {
        "found": True,
        "date": booking.date.strftime("%Y-%m-%d"),
        "time": f"{booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}",
        "hours": booking.hours,
        "price": booking.price,
        "status": booking.status
    }