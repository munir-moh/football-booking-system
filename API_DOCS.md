Football Booking API – Endpoints

Base URL:
https://football-booking-system.onrender.com


---

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

Notes:
- "name" can also be sent as "fullName".
- "phone" can also be sent as "phoneNumber".
- "start_time" can also be sent as "startTime".
- "hours" can also be sent as "duration".
- The pitch is open from 07:00 to 23:00. Bookings must fit entirely within these hours.
- Bookings must be made at least 1 hour before the requested start time. This also rules out any date/time in the past.

Success Response Example (201):
{
  "success": true,
  "message": "Booking created successfully",
  "booking": {
    "name": "Ibrahim Musa",
    "phone": "08031234567",
    "date": "2026-01-25",
    "time": "15:00 - 16:00",
    "hours": 1,
    "price": 10000,
    "reference": "FP-20260112-2239-DYXU",
    "status": "Pending"
  },
  "payment_details": {
    "bank": "Access Bank",
    "account_name": "Elite Football Pitch",
    "account_number": "0123456789"
  }
}

Error Response Examples:

Missing fields (400):
{
  "error": "Missing required fields: name/fullName, phone/phoneNumber"
}

Invalid date/time/duration format (400):
{
  "error": "Invalid date or time format: <details>"
}

Below minimum duration (400):
{
  "error": "Minimum booking is 1 hour(s)"
}

Outside operating hours (400):
{
  "error": "The pitch opens at 07:00. Please choose a later start time."
}
or
{
  "error": "The pitch closes at 23:00. Please choose an earlier start time or a shorter duration."
}

Too soon / in the past (400):
{
  "error": "Bookings must be made at least 1 hour(s) before the desired start time."
}

Time conflict with an existing booking (400):
{
  "error": "Time slot already booked"
}

Database error (500):
{
  "error": "Database error: <details>"
}


---

Admin – View All Bookings

Endpoint:
GET https://football-booking-system.onrender.com/api/admin/bookings

Headers:
X-ADMIN-PASSWORD: <your admin password>

Payload: None

Success Response Example (200):
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

Error Response Example (Unauthorized, 401):
{
  "error": "Unauthorized access"
}


---

Admin – Confirm Booking

Endpoint:
POST https://football-booking-system.onrender.com/api/admin/confirm/<REFERENCE>

Headers:
X-ADMIN-PASSWORD: <your admin password>

Payload: None

Success Response Example (200):
{
  "message": "Booking FP-20260112-2239-DYXU confirmed",
  "status": "Confirmed"
}

Error Response Examples:

Wrong password (401):
{
  "error": "Unauthorized access"
}

Invalid reference (404):
{
  "error": "Booking not found"
}


---

AI Assistant – Chat

Endpoint:
POST https://football-booking-system.onrender.com/api/ai/chat

Headers:
Content-Type: application/json

Payload Example:
{
  "message": "Is the pitch available tomorrow at 5pm for 2 hours?",
  "history": [
    { "role": "user", "content": "How much does the pitch cost per hour?" },
    { "role": "assistant", "content": "The pitch costs ₦10,000 per hour." }
  ]
}

Notes:
- "message" is required, must be a non-empty string, and must be 500 characters or fewer.
- "history" is optional. It should be a list of { "role": "user" | "assistant", "content": "..." } objects representing prior turns in the same conversation. If omitted, the conversation starts fresh.
- Only the most recent messages in "history" are actually used (older messages are trimmed) to keep responses fast and costs predictable — the assistant may "forget" details from very early in a long conversation.
- The assistant only answers using real data from the backend (pricing, live availability, pitch info, booking status by reference). It does not guess and cannot create, modify, or cancel bookings.
- This endpoint is rate-limited to 6 requests per minute per IP address.

Success Response Example (200):
{
  "reply": "Yes, the pitch is available tomorrow at 5:00 PM for 2 hours. The total price would be ₦20,000."
}

Error Response Examples:

Missing message (400):
{
  "error": "A 'message' field is required."
}

Empty message (400):
{
  "error": "Message cannot be empty."
}

Message too long (400):
{
  "error": "Message is too long. Please keep it under 500 characters."
}

Rate limit exceeded (429):
(returned automatically by the rate limiter; no custom JSON body)

Assistant unavailable, e.g. OpenAI request failed (500):
{
  "error": "The AI assistant is currently unavailable. Please try again shortly."
}


---

Health Check

Endpoint:
GET https://football-booking-system.onrender.com/

Success Response Example (200):
{
  "status": "running",
  "message": "Football Pitch Booking API",
  "endpoints": {
    "book": "/api/book (POST)",
    "view_bookings": "/api/admin/bookings (GET)",
    "confirm_booking": "/api/admin/confirm/<reference> (POST)"
  }
}
