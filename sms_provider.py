# sms_provider.py
import os
import requests

API_URL = os.getenv("SMS_019_API_URL", "https://019sms.co.il/api")
USERNAME = os.getenv("SMS_019_USERNAME")
PASSWORD = os.getenv("SMS_019_PASSWORD")
SENDER   = os.getenv("SMS_019_SENDER", "provent")


def send_sms(phone: str, text: str) -> bool:
    """
    פונקציה מרכזית לשליחת SMS דרך 019.
    מחזירה True אם ההודעה נשלחה בהצלחה, אחרת False.
    """

    # אם אין הגדרות – לא ננסה לשלוח
    if not USERNAME or not PASSWORD:
        print("[SMS] Missing username/password env vars")
        return False

    if not phone or not text:
        print("[SMS] Missing phone or text")
        return False

    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "source": SENDER,
        "destinations": [
            {
                "phone": phone
            }
        ],
        "message": text,
        # אם יש שדות נוספים שחייבים לפי הדוקומנטציה – מוסיפים פה
        # למשל: "encoding": "UTF-8"
    }

    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
        print("[SMS] status:", resp.status_code, resp.text)

        if resp.status_code == 200:
            # אפשר לבדוק גם קוד חזרה בגוף התשובה אם 019 מחזירים
            return True

        return False
    except Exception as e:
        print("[SMS] error:", e)
        return False
