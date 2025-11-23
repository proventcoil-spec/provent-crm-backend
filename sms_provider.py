import os
import requests
from flask import current_app

def send_sms_019(phone: str, text: str) -> bool:
    """שליחת SMS דרך 019.
    חשוב: צריך לעדכן כאן את ה-URL והפרמטרים לפי המסמך הרשמי של 019.
    כרגע זה מבוסס על דוגמה גנרית.
    """
    phone = phone.replace("-", "").replace(" ", "")
    if phone.startswith("0"):
        phone = "972" + phone[1:]

    cfg = current_app.config
    username = cfg.get("SMS_019_USERNAME")
    password = cfg.get("SMS_019_PASSWORD")
    api_key  = cfg.get("SMS_019_API_KEY")
    sender   = cfg.get("SMS_019_SENDER", "PROVENT")

    if not (username and password and api_key):
        current_app.logger.warning("019 SMS not configured - skipping real send")
        return False

    url = "https://019sms.example.com/api/send"  # להחליף ב-URL האמיתי של 019
    payload = {
        "username": username,
        "password": password,
        "api_key": api_key,
        "from": sender,
        "to": phone,
        "text": text,
    }

    try:
        resp = requests.post(url, data=payload, timeout=10)
        current_app.logger.info("019 SMS response: %s", resp.text)
        return resp.ok
    except Exception as e:
        current_app.logger.error("019 SMS error: %s", e)
        return False
