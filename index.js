// index.js - Provent CRM backend (חדש ומסודר)

require("dotenv").config();
const express = require("express");
const cors = require("cors");
const mysql = require("mysql2/promise");
const jwt = require("jsonwebtoken");

const app = express();

// ===== הגדרות בסיס =====
const PORT = process.env.PORT || 3000;

// חיבור למסד נתונים (Hostinger)
const DB_HOST = process.env.DB_HOST;
const DB_USER = process.env.DB_USER;
const DB_PASSWORD = process.env.DB_PASSWORD;
const DB_NAME = process.env.DB_NAME;

const JWT_SECRET = process.env.JWT_SECRET || "ProventCRM2025SecretKey";

// ===== חיבור ל-SMS (019) =====
let smsService = null;
try {
  smsService = require("./smsService");
  console.log("smsService loaded");
} catch (e) {
  console.warn("smsService.js not found - SMS routes will be disabled for now");
}

// ===== MIDDLEWARE =====
app.use(cors());
app.use(express.json());

// ===== חיבור ל-DB =====
let dbPool;

async function initDb() {
  dbPool = await mysql.createPool({
    host: DB_HOST,
    user: DB_USER,
    password: DB_PASSWORD,
    database: DB_NAME,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0,
    charset: "utf8mb4",
  });

  console.log("MySQL pool created");

  // יצירת טבלת משתמשים אם לא קיימת
  await dbPool.query(`
    CREATE TABLE IF NOT EXISTS provent_crm_users (
      id INT AUTO_INCREMENT PRIMARY KEY,
      full_name VARCHAR(255) NOT NULL,
      username VARCHAR(100) NOT NULL UNIQUE,
      password VARCHAR(255) NOT NULL,
      role VARCHAR(50) NOT NULL DEFAULT 'worker',
      is_active TINYINT(1) NOT NULL DEFAULT 1,
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
  `);

  console.log("Table provent_crm_users ensured");

  // אם אין משתמשים – ניצור ברירת מחדל
  const [rows] = await dbPool.query("SELECT COUNT(*) AS cnt FROM provent_crm_users");
  if (rows[0].cnt === 0) {
    console.log("No users found, creating default users...");

    await dbPool.query(
      `INSERT INTO provent_crm_users (full_name, username, password, role, is_active)
       VALUES 
        ('Shlomi (Owner)', 'shlomi', 'Provent-2025', 'owner', 1),
        ('Shimon (Admin)', 'shimon', 'Provent-2025', 'admin', 1)`
    );

    console.log("Default users created: shlomi / shimon with password: Provent-2025");
  }
}

// ===== פונקציה ליצירת JWT =====
function createToken(user) {
  const payload = {
    id: user.id,
    username: user.username,
    role: user.role,
    fullName: user.full_name,
  };
  return jwt.sign(payload, JWT_SECRET, { expiresIn: "7d" });
}

// ===== Middleware לבדיקה (אם תרצה להוסיף בעתיד) =====
function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ success: false, error: "Missing token" });

  const token = authHeader.replace("Bearer ", "").trim();
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    return next();
  } catch (e) {
    return res.status(401).json({ success: false, error: "Invalid or expired token" });
  }
}

// ===== ROUTES =====

// בריאות השרת
app.get("/", (req, res) => {
  res.json({ status: "ok", message: "Provent CRM backend is running" });
});

// התחברות
app.post("/api/auth/login", async (req, res) => {
  try {
    const { username, password } = req.body || {};
    if (!username || !password) {
      return res.status(400).json({ success: false, error: "חסר שם משתמש או סיסמה" });
    }

    const [rows] = await dbPool.query(
      "SELECT * FROM provent_crm_users WHERE username = ? AND is_active = 1 LIMIT 1",
      [username]
    );

    if (!rows.length) {
      return res.status(401).json({ success: false, error: "שם משתמש או סיסמה שגויים" });
    }

    const user = rows[0];

    // שים לב: כרגע בדיקה פשוטה (סיסמה ב-Plain Text)
    // בהמשך נחליף ל-bcrypt והשוואת hash
    if (user.password !== password) {
      return res.status(401).json({ success: false, error: "שם משתמש או סיסמה שגויים" });
    }

    const token = createToken(user);

    return res.json({
      success: true,
      token,
      username: user.username,
      fullName: user.full_name,
      role: user.role,
    });
  } catch (err) {
    console.error("Login error:", err);
    res.status(500).json({ success: false, error: "שגיאה בשרת בעת התחברות" });
  }
});

// ===== דוגמה לראוט שמוגן (אם תרצה להשתמש) =====
// app.get("/api/me", authMiddleware, (req, res) => {
//   res.json({ success: true, user: req.user });
// });

// ===== SMS ROUTES (019) =====
if (smsService) {
  // בדיקה – מביא טוקן ומחזיר
  app.get("/api/sms/test", async (req, res) => {
    try {
      const info = await smsService.testSmsConnection();
      res.json({ success: true, ...info });
    } catch (err) {
      console.error("SMS test error:", err.message);
      res.status(500).json({ success: false, error: err.message });
    }
  });

  // שליחת SMS בסיסית
  app.post("/api/sms/send", async (req, res) => {
    try {
      const { to, text } = req.body || {};
      if (!to || !text) {
        return res.status(400).json({ success: false, error: "Missing 'to' or 'text'" });
      }

      const result = await smsService.sendSms({ to, text });
      res.json({ success: true, result });
    } catch (err) {
      console.error("SMS send error:", err.message);
      res.status(500).json({ success: false, error: err.message });
    }
  });
} else {
  // אם אין smsService – נעשה ראוט שמודיע שזה לא זמין
  app.get("/api/sms/test", (req, res) => {
    res.status(501).json({ success: false, error: "SMS service not configured (missing smsService.js)" });
  });
  app.post("/api/sms/send", (req, res) => {
    res.status(501).json({ success: false, error: "SMS service not configured (missing smsService.js)" });
  });
}

// ===== הפעלת השרת =====
initDb()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Provent CRM backend listening on port ${PORT}`);
    });
  })
  .catch((err) => {
    console.error("Failed to init DB:", err);
    process.exit(1);
  });