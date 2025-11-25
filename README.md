# Provent CRM Login (Backend + Frontend)

זהו פרויקט מינימלי למערכת לוגין אמיתית:

* Flask backend עם התחברות ל-MySQL
* טבלת users קיימת (לא צריך ליצור מהתחלה)
* מסלול התחברות: POST /api/auth/login
* אימות לפי email או username + סיסמה מוצפנת pbkdf2_sha256
* JWT token לחזרה לפרונט

## Environment variables (Render)

שים ב-Environment:

* DATABASE_URL או:
  * DB_HOST
  * DB_USER
  * DB_PASS
  * DB_NAME
* JWT_SECRET_KEY (למשל: Provent-JWT-Secret-2025)
* FRONTEND_ORIGIN = https://crm.pro-net.pro

### Start command (Render)

gunicorn app:app
