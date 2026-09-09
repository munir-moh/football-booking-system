from datetime import datetime, timedelta
from models import Booking
from booking_logic import is_time_conflict
from pitch_info import PITCH_INFO
from config import PRICE_PER_HOUR, MIN_HOURS


def get_pitch_info():
    """Returns general pitch info: hours, facilities, discounts, policy."""
    return PITCH_INFO


def get_pricing_info():
    """Returns price per hour and minimum booking duration."""
    return {
        "price_per_hour": PRICE_PER_HOUR,
        "currency": "NGN",
        "minimum_booking_hours": MIN_HOURS
    }


def check_pitch_availability(date, start_time, hours):
    """
    Checks if the pitch is free for a given date/time/duration.
    date: "YYYY-MM-DD", start_time: "HH:MM" (24hr), hours: int
    """
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
    """Looks up a booking's status by its reference code."""
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