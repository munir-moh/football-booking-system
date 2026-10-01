from config import MIN_HOURS

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
    "minimum_booking_hours": MIN_HOURS,
    "minimum_advance_booking_hours": 1,
    "start_time_rule": "Bookings can start on the hour or half-hour.",
    "discounts": "No discounts are currently available. Standard rate applies to all bookings.",
    "payment_method": (
        "Customers complete payment through Paystack checkout during the booking flow."
    ),
    "confirmation_policy": (
        "A customer booking is confirmed after Paystack reports a successful payment "
        "through its webhook or payment verification."
    ),
    "cancellation_policy": (
        "Customer self-service cancellations are not available in the app. Contact "
        "the pitch directly to request a cancellation."
    )
}
