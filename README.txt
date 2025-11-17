# Provent CRM Backend (Node.js + Express)

1. צור מסד נתונים ב-MySQL והרץ עליו את הקובץ `schema.sql`.
2. צור משתמש אדמין ידנית:

   - בהרצת SQL:

     INSERT INTO users (full_name, email, password_hash, role)
     VALUES ('Admin', 'admin@example.com', '<hash>', 'admin');

   את ה-hash אפשר ליצור דרך סקריפט Node קטן או כלי אונליין של bcrypt.

3. צור קובץ `.env` (על בסיס `.env.example`) עם פרטי החיבור למסד ו-JWT_SECRET.
4. `npm install`
5. `npm start`

מומלץ להעלות את הקוד ל-Render / Railway ולהגדיר שם את משתני ה-ENV.
