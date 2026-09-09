from datetime import datetime
from models import Booking


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