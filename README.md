Football Pitch Booking System API

This is a simple RESTful API for booking a football pitch.  
Customers can book slots without authentication, and the admin can view all bookings and confirm payments.


Features

---Customer
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

---Admin
- View all bookings with history
- Confirm bookings manually after payment
- Protected with a hardcoded password (`admin123`)


Technologies Used
- Python 3
- Flask
- SQLite (for persistent storage)
- JSON for API responses

---

Installation

1. Clone the repository or copy the `app.py` file.
2. Create a virtual environment:
python -m venv venv

Activate the virtual environment:
Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Running the Server:
python app.py


The API will run on http://127.0.0.1:5000.