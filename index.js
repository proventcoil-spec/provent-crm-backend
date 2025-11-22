// index.js - Provent CRM Backend
require("dotenv").config();

const express = require("express");
const cors = require("cors");
const jwt = require("jsonwebtoken");
const mysql = require("mysql2/promise");
const smsService = require("./smsService");

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || "CHANGE_ME_SECRET";

// CORS – מאפשר גישה מה-CRM
app.use(
  cors({
    origin: true, // אפשר לשים ['https://crm.pro-net.pro'] אם תרצה לסגור
  })
);
app.use(express.json());

// ===== MySQL Pool =====
const dbPool = mysql.createPool({
  host: process.env.DB_HOST || "srv1016.hstgr.io",
  user: process.env.DB_USER || "u894002499_provicrm",
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME || "u894002499_provicrm",
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
  charset: "utf8mb4",
});

// ===== יצירת טבלאות ומשתמשי ברירת מחדל =====
async function ensureSchema() {
  const conn = await dbPool.getConnection();
  try {
    // משתמשים
    await conn.query(`
      CREATE TABLE IF NOT EXISTS provent_crm_users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        full_name VARCHAR(255),
        role ENUM('owner','admin','team_manager','employee','client') NOT NULL DEFAULT 'employee',
        phone VARCHAR(30),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    `);

    // לידים
    await conn.query(`
      CREATE TABLE IF NOT EXISTS provent_crm_leads (
        id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        phone VARCHAR(30) NOT NULL,
        email VARCHAR(255),
        event_type VARCHAR(100),
        event_date DATE,
        source VARCHAR(100),
        status VARCHAR(50) DEFAULT 'new',
        assigned_to INT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NULL,
        INDEX idx_leads_phone (phone)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    `);

    // לקוחות
    await conn.query(`
      CREATE TABLE IF NOT EXISTS provent_crm_clients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        phone VARCHAR(30) NOT NULL,
        email VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    `);

    // משתמשי ברירת מחדל
    const [rows] = await conn.query(
      "SELECT COUNT(*) AS cnt FROM provent_crm_users"
    );
    if (rows[0].cnt === 0) {
      await conn.query(`
        INSERT INTO provent_crm_users (username, password, full_name, role)
        VALUES 
          ('shlomi', 'Provent-2025', 'שלומי פרץ', 'owner'),
          ('shimon', 'Provent-2025', 'שמעון אסרף', 'owner')
      `);
      console.log(
        "Default users created: shlomi / shimon with password: Provent-2025"
      );
    }
  } finally {
    conn.release();
  }
}

ensureSchema()
  .then(() => console.log("DB schema ensured"))
  .catch((err) => {
    console.error("DB schema error:", err);
    process.exit(1);
  });

// ===== אימות JWT =====
function authMiddleware(req, res, next) {
  const authHeader = req.headers["authorization"] || "";
  const token = authHeader.startsWith("Bearer ")
    ? authHeader.slice(7)
    : null;

  if (!token) {
    return res
      .status(401)
      .json({ success: false, error: "Missing Authorization token" });
  }

  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = payload;
    next();
  } catch (err) {
    return res
      .status(401)
      .json({ success: false, error: "Invalid or expired token" });
  }
}

// ===== Routes בסיס =====
app.get("/", (req, res) => {
  res.json({ status: "ok", message: "Provent CRM backend is running" });
});

// ===== AUTH =====

// התחברות
app.post("/api/auth/login", async (req, res) => {
  try {
    const { username, password } = req.body || {};

    if (!username || !password) {
      return res
        .status(400)
        .json({ success: false, error: "Missing username or password" });
    }

    const [rows] = await dbPool.query(
      "SELECT id, username, password, full_name, role FROM provent_crm_users WHERE username = ? LIMIT 1",
      [username]
    );

    if (!rows.length) {
      return res
        .status(401)
        .json({ success: false, error: "User not found" });
    }

    const user = rows[0];

    if (user.password !== password) {
      return res
        .status(401)
        .json({ success: false, error: "Invalid password" });
    }

    const token = jwt.sign(
      {
        id: user.id,
        username: user.username,
        role: user.role,
        fullName: user.full_name || "",
      },
      JWT_SECRET,
      { expiresIn: "7d" }
    );

    res.json({
      success: true,
      token,
      username: user.username,
      role: user.role,
      fullName: user.full_name || "",
    });
  } catch (err) {
    console.error("POST /api/auth/login error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

app.get("/api/auth/me", authMiddleware, (req, res) => {
  res.json({ success: true, user: req.user });
});

// ===== LEADS API =====

app.get("/api/leads", authMiddleware, async (req, res) => {
  try {
    const [rows] = await dbPool.query(
      "SELECT * FROM provent_crm_leads ORDER BY created_at DESC"
    );
    res.json({ success: true, leads: rows });
  } catch (err) {
    console.error("GET /api/leads error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

app.post("/api/leads", authMiddleware, async (req, res) => {
  try {
    const {
      full_name,
      phone,
      email,
      event_type,
      event_date,
      source,
      status,
      assigned_to,
      notes,
    } = req.body || {};

    if (!full_name || !phone) {
      return res
        .status(400)
        .json({ success: false, error: "Missing full_name or phone" });
    }

    const [result] = await dbPool.query(
      `
      INSERT INTO provent_crm_leads
      (full_name, phone, email, event_type, event_date, source, status, assigned_to, notes)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `,
      [
        full_name,
        phone,
        email || null,
        event_type || null,
        event_date || null,
        source || null,
        status || "new",
        assigned_to || null,
        notes || null,
      ]
    );

    res.json({ success: true, id: result.insertId });
  } catch (err) {
    console.error("POST /api/leads error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

app.put("/api/leads/:id", authMiddleware, async (req, res) => {
  try {
    const leadId = parseInt(req.params.id, 10);
    const fields = req.body || {};

    if (!leadId) {
      return res
        .status(400)
        .json({ success: false, error: "Invalid lead id" });
    }

    const allowed = [
      "full_name",
      "phone",
      "email",
      "event_type",
      "event_date",
      "source",
      "status",
      "assigned_to",
      "notes",
    ];
    const sets = [];
    const values = [];

    for (const key of allowed) {
      if (key in fields) {
        sets.push(`${key} = ?`);
        values.push(fields[key]);
      }
    }

    if (!sets.length) {
      return res.json({ success: true, message: "No fields to update" });
    }

    sets.push("updated_at = NOW()");
    const sql = `UPDATE provent_crm_leads SET ${sets.join(
      ", "
    )} WHERE id = ? LIMIT 1`;
    values.push(leadId);

    await dbPool.query(sql, values);
    res.json({ success: true });
  } catch (err) {
    console.error("PUT /api/leads/:id error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

// ===== CLIENTS API =====

app.get("/api/clients", authMiddleware, async (req, res) => {
  try {
    const [rows] = await dbPool.query(
      "SELECT id, name, phone, email, created_at FROM provent_crm_clients ORDER BY created_at DESC"
    );
    res.json({ success: true, clients: rows });
  } catch (err) {
    console.error("GET /api/clients error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

app.post("/api/clients", authMiddleware, async (req, res) => {
  try {
    const { name, phone, email } = req.body || {};

    if (!name || !phone) {
      return res
        .status(400)
        .json({ success: false, error: "Missing name or phone" });
    }

    const [result] = await dbPool.query(
      "INSERT INTO provent_crm_clients (name, phone, email) VALUES (?, ?, ?)",
      [name, phone, email || null]
    );

    res.json({ success: true, id: result.insertId });
  } catch (err) {
    console.error("POST /api/clients error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

// ===== SMS API =====

app.get("/api/sms/test", authMiddleware, async (req, res) => {
  const { SMS_API_URL, SMS_USERNAME, SMS_USERNAME_FOR_TOKEN } = process.env;

  if (!SMS_API_URL || !SMS_USERNAME || !SMS_USERNAME_FOR_TOKEN) {
    return res.json({
      success: false,
      error:
        "SMS API settings missing (SMS_API_URL / SMS_USERNAME / SMS_USERNAME_FOR_TOKEN)",
    });
  }

  res.json({
    success: true,
    tokenPreview: "configured",
  });
});

app.post("/api/sms/send", authMiddleware, async (req, res) => {
  try {
    const { phone, text } = req.body || {};
    if (!phone || !text) {
      return res
        .status(400)
        .json({ success: false, error: "Missing phone or text" });
    }

    const result = await smsService.sendSms(phone, text);
    if (!result.success) {
      return res
        .status(500)
        .json({ success: false, error: result.error || "SMS failed" });
    }

    res.json({ success: true });
  } catch (err) {
    console.error("POST /api/sms/send error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

// ===== Start Server =====
app.listen(PORT, () => {
  console.log(`Provent CRM backend listening on port ${PORT}`);
});
