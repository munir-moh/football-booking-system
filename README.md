Football Pitch Booking System API

This is a RESTful API for booking a football pitch, with an integrated AI assistant that can answer customer questions using real, live data from the backend.

Customers can book slots without authentication, ask the AI assistant questions about pricing/availability/facilities, and the admin can view all bookings and confirm payments.


Features

--- Customer
- Book a football pitch for a specific date and time
- Each booking requires:
  - Name
  - Phone number
  - Date
  - Start time
  - Number of hours (minimum 1)
- Each session costs ₦10,000 per hour
- Unique booking reference is generated automatically
- Payment details are displayed (bank, account name, account number)
- Time conflict checking: overlapping bookings are not allowed
- Operating hours enforced: bookings must fall entirely within 07:00–23:00
- Lead time enforced: bookings must be made at least 1 hour before the requested start time (this also rules out booking in the past)

--- AI Assistant
- Chat-based assistant, available via the `/api/ai/chat` endpoint
- Answers questions about pricing, live availability, pitch facilities/policy, opening hours, and booking status by reference
- Uses OpenAI's tool use / function calling — the assistant can only answer using real data pulled from this backend (pricing config, the live bookings database, and a static pitch-info file). It does not guess or invent answers.
- Aware of the real current date, so it correctly resolves relative questions like "is it available tomorrow?"
- Rate-limited (6 requests per minute per IP) to control usage and cost
- Conversation history is automatically trimmed to the most recent messages to keep responses fast and predictable in cost

--- Admin
- View all bookings with history
- Confirm bookings manually after payment
- Protected by a password stored in an environment variable (not hardcoded in source)


Technologies Used
- Python 3
- Flask
- Flask-SQLAlchemy + SQLite (persistent storage)
- flask-cors (cross-origin requests from the frontend)
- Flask-Limiter (rate limiting)
- OpenAI SDK (AI assistant, tool use / function calling)
- python-dotenv (environment variable / secrets management)
- JSON for API responses


Project Structure
- `app.py` — main Flask app and all API routes
- `models.py` — SQLAlchemy `Booking` model
- `database.py` — database initialization
- `config.py` — configuration values, loaded from environment variables where sensitive
- `booking_logic.py` — shared booking rules: conflict checking, operating hours, and lead-time validation (used by both the booking route and the AI assistant, so they always agree)
- `pitch_info.py` — static pitch info (opening hours, facilities, discounts, policy) used by the AI assistant
- `ai_tools.py` — the individual "tools" the AI assistant can call (pricing info, pitch info, availability check, booking lookup by reference)
- `ai_tool_schemas.py` — descriptions of those tools in the format OpenAI's API expects
- `ai_service.py` — builds the system prompt, sends requests to OpenAI, and handles tool-calling round trips


Environment Variables

This project uses a `.env` file for secrets — never commit this file. Copy `.env.example` to `.env` and fill in real values:

```
OPENAI_API_KEY=your-openai-api-key-here
ADMIN_PASSWORD=your-admin-password-here
```

- `OPENAI_API_KEY` — required for the AI assistant to function. Without it, `/api/ai/chat` will return an error.
- `ADMIN_PASSWORD` — required for admin login (`/api/admin/bookings` and `/api/admin/confirm/<reference>`).

If deploying (e.g. to Render), set these same variables in your hosting platform's environment settings — `.env` files are local-only and are not deployed automatically.


Installation

1. Clone the repository.
2. Create a virtual environment:
```
python -m venv venv
```

3. Activate the virtual environment:

Windows:
```
venv\Scripts\activate
```

Mac/Linux:
```
source venv/bin/activate
```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Create your `.env` file (see Environment Variables above).

6. Run the server:
```
python app.py
```

The API will run on http://127.0.0.1:5000.


API Documentation

See `API_DOCS.md` for full endpoint details, request/response examples, and error responses — including the customer booking flow, admin endpoints, and the AI assistant endpoint.


Notes
- The database (`football_booking.db`) is a local SQLite file, sufficient for this project's current scale. If concurrent traffic grows significantly, migrating to a hosted database (e.g. PostgreSQL) would be the natural next step.
- Admin access is a single shared password, not individual user accounts — appropriate for a single-admin setup, not designed for multiple admins with separate permissions.
