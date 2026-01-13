Football Booking API – Endpoints

Base URL:
https://football-booking-system.onrender.com

Customer Booking
Endpoint:

POST https://football-booking-system.onrender.com/api/book

Headers:
Content-Type: application/json

Payload Example:
{
  "name": "Ibrahim Musa",
  "phone": "08031234567",
  "date": "2026-01-25",
  "start_time": "15:00",
  "hours": 1
}

Success Response Example:
{
  "message": "Booking created successfully",
  "name": "Ibrahim Musa",
  "phone": "08031234567",
  "date": "2026-01-25",
  "time": "15:00 - 16:00",
  "hours": 1,
  "price": 10000,
  "reference": "FP-20260112-2239-DYXU",
  "payment_details": {
    "bank": "Access Bank",
    "account_name": "Elite Football Pitch",
    "account_number": "0123456789"
  },
  "status": "Pending"
}

Error Response Example (Time Conflict):
{
  "error": "Time slot already booked"
}


Admin – View All Bookings
Endpoint:

GET https://football-booking-system.onrender.com/api/admin/bookings

Headers:
X-ADMIN-PASSWORD: supersecret123

Payload: None

Success Response Example:
[
  {
    "name": "Ibrahim Musa",
    "phone": "08031234567",
    "date": "2026-01-25",
    "time": "15:00 - 16:00",
    "hours": 1,
    "price": 10000,
    "reference": "FP-20260112-2239-DYXU",
    "status": "Pending"
  }
]

Error Response Example (Unauthorized):
{
  "error": "Unauthorized: Invalid admin password"
}


Admin – Confirm Booking
Endpoint:

POST https://football-booking-system.onrender.com/api/admin/confirm/<REFERENCE>


Headers:
X-ADMIN-PASSWORD: supersecret123

Payload: None

Success Response Example:
{
  "message": "Booking FP-20260112-2239-DYXU confirmed",
  "status": "Confirmed"
}

Error Response Examples:

Wrong password:
{
  "error": "Unauthorized: Invalid admin password"
}


Invalid reference:
{
  "error": "Booking not found"
}