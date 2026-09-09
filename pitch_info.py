# pitch_info.py
#
# Static information about the football pitch itself.
# This is NOT booking data (that lives in the database via models.py).
# This is descriptive info the AI assistant can read when customers
# ask general questions like opening hours, facilities, or policy.
#
# Edit the values below to match your real pitch. Later, if this
# needs to change per-pitch or per-day, this can be moved into the
# database without changing how the AI calls it.

PITCH_INFO = {
    "name": "Elite Football Pitch",
    "opening_time": "07:00",
    "closing_time": "23:00",
    "facilities": [
        "Floodlights for night games",
        "Changing rooms",
        "Free parking",
        "Drinking water station"
    ],
    "discounts": "No discounts are currently available. Standard rate applies to all bookings.",
    "booking_policy": (
        "Bookings must be made at least 1 hour before the desired start time. "
        "Cancellations are not currently supported through the app — contact the "
        "pitch directly for cancellation requests. Payment must be completed "
        "within 24 hours of booking, or the slot may be released."
    ),
    "minimum_booking_hours": 1
}