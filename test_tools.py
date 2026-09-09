from app import app
from ai_tools import check_pitch_availability, get_booking_by_reference

with app.app_context():
    print(check_pitch_availability("2026-01-25", "15:00", 1))
    print(get_booking_by_reference("FP-20260112-2239-DYXU"))