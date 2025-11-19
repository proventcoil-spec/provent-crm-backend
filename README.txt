
Provent CRM Backend
====================

זהו שרת Backend בסיסי ל-Provent CRM, כתוב ב-Node.js + Express + MySQL.

קבצים:
- index.js  – קובץ השרת הראשי (Express)
- db.js     – חיבור למסד הנתונים (MySQL + mysql2/promise)
- package.json – תלותים וסקריפט הפעלה
- .env.example – דוגמה להגדרות Environment (DB + JWT)

דרישות:
- Node.js מותקן (מומלץ גרסה 18+)
- מסד נתונים MySQL עם טבלת users

טבלת users (SQL לדוגמה):
-------------------------
יצירת טבלה:

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('owner','admin','team_manager','employee','client') NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

יצירת משתמש מנהל (שלומי) בסיסי:

INSERT INTO users (username, password, role, full_name, phone)
VALUES ('shlomi', '1234', 'owner', 'שלומי פרץ', '0512121493');

(בהמשך מומלץ להצפין סיסמאות, זה כרגע לצורך בדיקות בלבד.)

איך מריצים על המחשב:
--------------------

1. פתח טרמינל בתיקייה של הפרויקט:

   cd provent-crm-backend

2. התקן תלותים:

   npm install

3. צור קובץ .env (לפי .env.example):

   העתיקו את .env.example לקובץ בשם .env
   ועדכן:
   - DB_HOST – ה-Host של ה-MySQL מ-Hostinger
   - DB_USER – u894002499_provicrm
   - DB_PASSWORD – הסיסמה שקבעת למסד
   - DB_NAME – u894002499_provicrm
   - JWT_SECRET – מחרוזת סודית כלשהי

4. הפעלת השרת:

   npm start

   אם הכול תקין, תראה בטרמינל:
   Provent CRM backend listening on port 10000

5. בדיקה בדפדפן / Postman:

   א. בדיקה שהשרת חי:

   GET http://localhost:10000/

   יחזיר:
   { "status": "ok", "message": "Provent CRM backend is running" }

   ב. בדיקת לוגין:

   POST http://localhost:10000/api/auth/login
   Headers:
     Content-Type: application/json

   Body (JSON):

   {
     "username": "shlomi",
     "password": "1234"
   }

   אם המשתמש קיים בטבלת users:
   תקבל:

   {
     "success": true,
     "token": "....",
     "role": "owner",
     "user": {
       "id": 1,
       "username": "shlomi",
       "full_name": "שלומי פרץ",
       "phone": "0512121493"
     }
   }

חיבור לפרונט (crm.pro-net.pro):
--------------------------------
בפרונט, ה-API_BASE_URL צריך להיות:

  https://provent-crm-backend.onrender.com

והלוגין מגדיר קריאה ל:
  POST /api/auth/login

ברנדֶר:
-------
כשתעלה את הפרויקט לרנדר כ-Web Service:
- Build Command:  npm install
- Start Command:  npm start
- Environment Variables:
    DB_HOST     = (ה-Host של ה-MySQL מ-Hostinger)
    DB_USER     = u894002499_provicrm
    DB_PASSWORD = (הסיסמה שלך למסד)
    DB_NAME     = u894002499_provicrm
    JWT_SECRET  = (מחרוזת סודית חזקה)
