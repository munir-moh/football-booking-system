from datetime import datetime, timedelta
from models import Booking
from pitch_info import PITCH_INFO


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


def is_within_operating_hours(booking_date, start_time, end_dt):
    opening_time = datetime.strptime(PITCH_INFO["opening_time"], "%H:%M").time()
    closing_time = datetime.strptime(PITCH_INFO["closing_time"], "%H:%M").time()

    if start_time < opening_time:
        return False, f"The pitch opens at {PITCH_INFO['opening_time']}. Please choose a later start time."

    if end_dt.date() != booking_date or end_dt.time() > closing_time:
        return False, f"The pitch closes at {PITCH_INFO['closing_time']}. Please choose an earlier start time or a shorter duration."

    return True, None

def is_within_lead_time(start_dt):
    MIN_LEAD_HOURS = 1
    earliest_allowed = datetime.now() + timedelta(hours=MIN_LEAD_HOURS)

    if start_dt < earliest_allowed:
        return False, f"Bookings must be made at least {MIN_LEAD_HOURS} hour(s) before the desired start time."

    return True, None

def is_valid_start_time(start_time):
    if start_time.minute not in (0, 30):
        return False, "Bookings can only start on the hour or half-hour (e.g. 10:00 or 10:30)."
    return True, None