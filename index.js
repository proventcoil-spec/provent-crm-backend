// index.js - Provent CRM backend (גרסה מעודכנת)

// טוען משתני סביבה
require("dotenv").config();

const express = require("express");
const cors = require("cors");
const mysql = require("mysql2/promise");
const jwt = require("jsonwebtoken");

const app = express();

// ===== הגדרות בסיס =====
const PORT = process.env.PORT || 3000;

// נתוני DB מה-.env / Render Environment
const DB_HOST = process.env.DB_HOST;
const DB_USER = process.env.DB_USER;
const DB_PASSWORD = process.env.DB_PASSWORD;
const DB_NAME = process.env.DB_NAME;

const JWT_SECRET = process.env.JWT_SECRET || "ProventCRM2025SecretKey";

// ===== חיבור ל-SMS =====
let smsService = null;
try {
  smsService = require("./smsService");
  console.log("smsService loaded");
} catch (e) {
  console.warn("smsService.js not found - SMS routes will be limited");
}

// ===== MIDDLEWARE =====
app.use(cors());
app.use(express.json());

// ===== MySQL Pool =====
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

  // --- טבלת משתמשים ---
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

  // --- טבלת לידים בסיסית (נרחיב בהמשך) ---
  await dbPool.query(`
    CREATE TABLE IF NOT EXISTS provent_crm_leads (
      id INT AUTO_INCREMENT PRIMARY KEY,
      full_name VARCHAR(255) NOT NULL,
      phone VARCHAR(50),
      email VARCHAR(255),
      source VARCHAR(100),
      event_type VARCHAR(100),
      event_date DATE,
      location VARCHAR(255),
      status VARCHAR(50) DEFAULT 'new',
      owner_user_id INT NULL,
      notes TEXT,
      attempts_count INT DEFAULT 0,
      last_contact_at DATETIME NULL,
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      INDEX idx_status (status),
      INDEX idx_event_date (event_date),
      CONSTRAINT fk_leads_owner FOREIGN KEY (owner_user_id)
        REFERENCES provent_crm_users(id)
        ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
  `);

  console.log("Table provent_crm_leads ensured");
}

// ===== JWT =====
function createToken(user) {
  const payload = {
    id: user.id,
    username: user.username,
    role: user.role,
    fullName: user.full_name,
  };
  return jwt.sign(payload, JWT_SECRET, { expiresIn: "7d" });
}

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

function requireRole(roles) {
  const allowed = Array.isArray(roles) ? roles : [roles];
  return (req, res, next) => {
    if (!req.user || !allowed.includes(req.user.role)) {
      return res.status(403).json({ success: false, error: "אין לך הרשאה לפעולה זו" });
    }
    next();
  };
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

    // כרגע סיסמה בלי הצפנה – בהמשך נעבור ל-bcrypt
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

// ===== ניהול משתמשים (בפועל – אמיתי ב-DB) =====

// רשימת משתמשים – רק owner/admin
app.get("/api/users", authMiddleware, requireRole(["owner", "admin"]), async (req, res) => {
  try {
    const [rows] = await dbPool.query(
      "SELECT id, full_name, username, role, is_active, created_at FROM provent_crm_users ORDER BY id DESC"
    );
    res.json({ success: true, users: rows });
  } catch (err) {
    console.error("Get users error:", err);
    res.status(500).json({ success: false, error: "שגיאה בשליפת משתמשים" });
  }
});

// יצירת משתמש חדש
app.post("/api/users", authMiddleware, requireRole(["owner", "admin"]), async (req, res) => {
  try {
    const { full_name, username, password, role } = req.body || {};
    if (!full_name || !username || !password) {
      return res.status(400).json({ success: false, error: "חסר שם מלא/משתמש/סיסמה" });
    }

    const userRole = role || "worker";

    await dbPool.query(
      "INSERT INTO provent_crm_users (full_name, username, password, role, is_active) VALUES (?, ?, ?, ?, 1)",
      [full_name, username, password, userRole]
    );

    res.json({ success: true });
  } catch (err) {
    console.error("Create user error:", err);
    if (err && err.code === "ER_DUP_ENTRY") {
      return res.status(400).json({ success: false, error: "שם משתמש כבר קיים במערכת" });
    }
    res.status(500).json({ success: false, error: "שגיאה ביצירת משתמש" });
  }
});

// עדכון משתמש
app.put("/api/users/:id", authMiddleware, requireRole(["owner", "admin"]), async (req, res) => {
  try {
    const userId = parseInt(req.params.id, 10);
    const { full_name, password, role, is_active } = req.body || {};

    const fields = [];
    const values = [];

    if (full_name) {
      fields.push("full_name = ?");
      values.push(full_name);
    }
    if (password) {
      fields.push("password = ?");
      values.push(password);
    }
    if (role) {
      fields.push("role = ?");
      values.push(role);
    }
    if (typeof is_active === "number") {
      fields.push("is_active = ?");
      values.push(is_active);
    }

    if (!fields.length) {
      return res.json({ success: true }); // אין מה לעדכן
    }

    values.push(userId);

    await dbPool.query(`UPDATE provent_crm_users SET ${fields.join(", ")} WHERE id = ?`, values);

    res.json({ success: true });
  } catch (err) {
    console.error("Update user error:", err);
    res.status(500).json({ success: false, error: "שגיאה בעדכון משתמש" });
  }
});

// מחיקת משתמש (השבתה)
app.delete("/api/users/:id", authMiddleware, requireRole(["owner", "admin"]), async (req, res) => {
  try {
    const userId = parseInt(req.params.id, 10);

    await dbPool.query("UPDATE provent_crm_users SET is_active = 0 WHERE id = ?", [userId]);

    res.json({ success: true });
  } catch (err) {
    console.error("Delete user error:", err);
    res.status(500).json({ success: false, error: "שגיאה בעדכון משתמש" });
  }
});

// ===== לידים בסיסיים – GET + POST =====

// רשימת לידים
app.get("/api/leads", authMiddleware, async (req, res) => {
  try {
    const [rows] = await dbPool.query(
      `SELECT l.*, u.full_name AS owner_name
       FROM provent_crm_leads l
       LEFT JOIN provent_crm_users u ON u.id = l.owner_user_id
       ORDER BY l.created_at DESC`
    );
    res.json({ success: true, leads: rows });
  } catch (err) {
    console.error("Get leads error:", err);
    res.status(500).json({ success: false, error: "שגיאה בשליפת לידים" });
  }
});

// יצירת ליד
app.post("/api/leads", authMiddleware, async (req, res) => {
  try {
    const {
      full_name,
      phone,
      email,
      source,
      event_type,
      event_date,
      location,
      status,
      notes,
      owner_user_id,
    } = req.body || {};

    if (!full_name || !phone) {
      return res.status(400).json({ success: false, error: "חסר שם וטלפון לליד" });
    }

    const userId = owner_user_id || req.user.id;

    await dbPool.query(
      `INSERT INTO provent_crm_leads 
       (full_name, phone, email, source, event_type, event_date, location, status, notes, owner_user_id)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        full_name,
        phone,
        email || null,
        source || null,
        event_type || null,
        event_date || null,
        location || null,
        status || "new",
        notes || null,
        userId,
      ]
    );

    res.json({ success: true });
  } catch (err) {
    console.error("Create lead error:", err);
    res.status(500).json({ success: false, error: "שגיאה ביצירת ליד" });
  }
});

// ===== SMS ROUTES =====
if (smsService) {
  // בדיקה – מביא טוקן ומחזיר
  app.get("/api/sms/test", authMiddleware, requireRole(["owner", "admin"]), async (req, res) => {
    try {
      const info = await smsService.testSmsConnection();
      res.json({ success: true, ...info });
    } catch (err) {
      console.error("SMS test error:", err.message);
      res.status(500).json({ success: false, error: err.message });
    }
  });

  // שליחת SMS
  app.post("/api/sms/send", authMiddleware, async (req, res) => {
    try {
      const { to, text, senderName } = req.body || {};
      if (!to || !text) {
        return res.status(400).json({ success: false, error: "Missing 'to' or 'text'" });
      }

      const result = await smsService.sendSms({ to, text, senderName });
      res.json({ success: true, result });
    } catch (err) {
      console.error("SMS send error:", err.message);
      res.status(500).json({ success: false, error: err.message });
    }
  });
} else {
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
