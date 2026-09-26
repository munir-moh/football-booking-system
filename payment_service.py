import requests
from config import PAYSTACK_SECRET_KEY

PAYSTACK_BASE_URL = "https://api.paystack.co"


def initialize_transaction(email, amount_naira, reference, callback_url, metadata=None):
    url = f"{PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "amount": int(amount_naira * 100),
        "reference": reference,
        "callback_url": callback_url,
    }
    if metadata:
        payload["metadata"] = metadata

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()

        if response.status_code == 200 and data.get("status"):
            return {
                "success": True,
                "authorization_url": data["data"]["authorization_url"],
                "reference": data["data"]["reference"],
            }
        else:
            return {"success": False, "error": data.get("message", "Failed to initialize payment.")}

    except requests.RequestException as e:
        return {"success": False, "error": f"Could not reach Paystack: {str(e)}"}


def verify_transaction(reference):
    url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        if response.status_code == 200 and data.get("status"):
            return {
                "success": True,
                "status": data["data"]["status"],
                "amount_naira": data["data"]["amount"] / 100,
                "reference": data["data"]["reference"],
                "metadata": data["data"].get("metadata") or {},
            }
        else:
            return {"success": False, "error": data.get("message", "Could not verify transaction.")}

    except requests.RequestException as e:
        return {"success": False, "error": f"Could not reach Paystack: {str(e)}"}