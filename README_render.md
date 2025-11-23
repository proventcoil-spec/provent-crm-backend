# PROVENT CRM Backend 23.11.26 (Render)

## התקנה מקומית

1. ודא שמותקן Python 3.11 לפחות.
2. פתח טרמינל בתיקייה של הפרויקט:

   ```bash
   cd backend23.11.26
   python3 -m venv venv
   source venv/bin/activate      # ב-Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. הרצת יצירת בסיס הנתונים המקומי (SQLite):

   ```bash
   flask --app app.py init-db
   ```

4. הפעלת השרת:

   ```bash
   flask --app app.py run --host=0.0.0.0 --port=5000
   ```

5. בדיקה:

   גלוש אל `http://localhost:5000/api/health` – צריך להחזיר JSON עם status ok.

## פריסה ב-Render

1. העלה את הקוד ל-GitHub (רצוי).
2. ב-Render צור שירות חדש מסוג **Web Service** ובחר את הריפו.
3. הגדר:
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:create_app --bind 0.0.0.0:10000`
4. משתני סביבה חשובים:
   - `SECRET_KEY` – מחרוזת ארוכה וסודית
   - `DATABASE_URL` – Render יוצר אוטומטית אם מחברים Postgres
   - `SMS_019_USERNAME`, `SMS_019_PASSWORD`, `SMS_019_API_KEY`, `SMS_019_SENDER`

## חיבור לפרונט

ב-JavaScript שבדפי ה-HTML יש להגדיר את כתובת ה-API, לדוגמה:

```js
const API_BASE = "https://provent-crm-backend.onrender.com";
```

ואז קריאות ל:
- `/api/login`
- `/api/events`
- `/api/clients`
- `/api/workers`
- `/api/leads`
- `/api/settings/...`
