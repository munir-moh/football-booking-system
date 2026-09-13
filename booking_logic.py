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
    """
    Checks a booking's start/end against the pitch's opening and
    closing hours (defined in pitch_info.py).

    Returns (True, None) if it's within hours.
    Returns (False, reason) if it starts too early, ends too late,
    or rolls over into the next calendar day (which also happens
    to close a data bug where midnight-crossing bookings corrupt
    the stored end_time).
    """
    opening_time = datetime.strptime(PITCH_INFO["opening_time"], "%H:%M").time()
    closing_time = datetime.strptime(PITCH_INFO["closing_time"], "%H:%M").time()

    if start_time < opening_time:
        return False, f"The pitch opens at {PITCH_INFO['opening_time']}. Please choose a later start time."

    if end_dt.date() != booking_date or end_dt.time() > closing_time:
        return False, f"The pitch closes at {PITCH_INFO['closing_time']}. Please choose an earlier start time or a shorter duration."

    return True, None

def is_within_lead_time(start_dt):
    """
    Enforces the minimum lead time stated in pitch_info.py's booking
    policy: a booking's start time must be at least MIN_LEAD_HOURS
    from right now.

    Returns (True, None) if it's far enough in advance.
    Returns (False, reason) if it's too soon or already in the past.
    """
    MIN_LEAD_HOURS = 1
    earliest_allowed = datetime.now() + timedelta(hours=MIN_LEAD_HOURS)

    if start_dt < earliest_allowed:
        return False, f"Bookings must be made at least {MIN_LEAD_HOURS} hour(s) before the desired start time."

    return True, None