// index.js - PROVENT CRM Backend – נקי ומלא

require("dotenv").config();

const express = require("express");
const cors = require("cors");
const jwt = require("jsonwebtoken");
const mysql = require("mysql2/promise");
const smsService = require("./smsService");

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || "CHANGE_ME_SECRET";

// ---------- בסיס ----------

app.use(
  cors({
    origin: true, // אפשר לסגור ספציפית ל https://crm.pro-net.pro בהמשך
  })
);
app.use(express.json());

// ---------- חיבור MySQL ----------

const dbPool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
  charset: "utf8mb4",
});

// ---------- יצירת טבלאות בסיס ----------

async function ensureSchema() {
  const conn = await dbPool.getConnection();
  try {
    // משתמשי מערכת
    await conn.query(`
      CREATE TABLE IF NOT EXISTS provent_crm_users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        full_name VARCHAR(255),
        role ENUM('owner','admin','team_manager','employee','client') NOT NULL DEFAULT 'employee',
        phone VARCHAR(30),
        email VARCHAR(255),
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

    // עובדים / ספקים
    await conn.query(`
      CREATE TABLE IF NOT EXISTS provent_crm_workers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username VARCHAR(100),
        phone VARCHAR(30),
        email VARCHAR(255),
        type ENUM('employee','supplier') NOT NULL DEFAULT 'employee',
        role ENUM('owner','admin','team_manager','employee') NOT NULL DEFAULT 'employee',
        active TINYINT(1) NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    `);

    // אירועים
    await conn.query(`
      CREATE TABLE IF NOT EXISTS provent_crm_events (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        event_date DATE,
        event_type VARCHAR(100),
        location VARCHAR(255),
        client_id INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    `);

    // משתמשי ברירת מחדל אם אין אף אחד
    const [rows] = await conn.query(
      "SELECT COUNT(*) AS cnt FROM provent_crm_users"
    );
    if (rows[0].cnt === 0) {
      await conn.query(`
        INSERT INTO provent_crm_users (username, password, full_name, role, email)
        VALUES 
          ('shlomi', 'Provent-2025', 'שלומי פרץ', 'owner', 'shlomi@provent.co.il'),
          ('shimon', 'Provent-2025', 'שמעון אסרף', 'owner', 'shimon@provent.co.il')
      `);
      console.log("Default users created (shlomi / shimon, pass: Provent-2025)");
    }
  } finally {
    conn.release();
  }
}

ensureSchema()
  .then(() => console.log("✅ DB schema ready"))
  .catch((err) => {
    console.error("❌ DB schema error:", err);
    process.exit(1);
  });

// ---------- Middleware JWT ----------

function authMiddleware(req, res, next) {
  const authHeader = req.headers["authorization"] || "";
  const token = authHeader.startsWith("Bearer ")
    ? authHeader.slice(7)
    : null;

  if (!token) {
    return res.status(401).json({ success: false, error: "Missing token" });
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

// ---------- בסיס ----------

app.get("/", (req, res) => {
  res.json({ status: "ok", message: "Provent CRM backend is running" });
});

// ---------- AUTH ----------

// לוגין
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
      return res.status(401).json({ success: false, error: "User not found" });
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

// מי אני
app.get("/api/auth/me", authMiddleware, (req, res) => {
  res.json({ success: true, user: req.user });
});

// ---------- LEADS API ----------

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

// ---------- CLIENTS API ----------

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

app.get("/api/clients/:id", authMiddleware, async (req, res) => {
  try {
    const clientId = parseInt(req.params.id, 10);
    const [rows] = await dbPool.query(
      "SELECT id, name, phone, email, created_at FROM provent_crm_clients WHERE id = ? LIMIT 1",
      [clientId]
    );
    if (!rows.length) {
      return res.status(404).json({ success: false, error: "Client not found" });
    }
    res.json({ success: true, client: rows[0] });
  } catch (err) {
    console.error("GET /api/clients/:id error:", err);
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

app.put("/api/clients/:id", authMiddleware, async (req, res) => {
  try {
    const clientId = parseInt(req.params.id, 10);
    const { name, phone, email } = req.body || {};

    if (!clientId) {
      return res
        .status(400)
        .json({ success: false, error: "Invalid client id" });
    }

    await dbPool.query(
      "UPDATE provent_crm_clients SET name = ?, phone = ?, email = ? WHERE id = ? LIMIT 1",
      [name || null, phone || null, email || null, clientId]
    );

    res.json({ success: true });
  } catch (err) {
    console.error("PUT /api/clients/:id error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

// ---------- WORKERS API ----------

app.get("/api/workers", authMiddleware, async (req, res) => {
  try {
    const [rows] = await dbPool.query(
      "SELECT id, full_name, username, phone, email, type, role, active, created_at FROM provent_crm_workers ORDER BY created_at DESC"
    );
    res.json({ success: true, workers: rows });
  } catch (err) {
    console.error("GET /api/workers error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

app.post("/api/workers", authMiddleware, async (req, res) => {
  try {
    const { full_name, username, phone, email, type, role } = req.body || {};
    if (!full_name) {
      return res
        .status(400)
        .json({ success: false, error: "Missing full_name" });
    }

    const [result] = await dbPool.query(
      `
      INSERT INTO provent_crm_workers
      (full_name, username, phone, email, type, role)
      VALUES (?, ?, ?, ?, ?, ?)
    `,
      [
        full_name,
        username || null,
        phone || null,
        email || null,
        type || "employee",
        role || "employee",
      ]
    );

    res.json({ success: true, id: result.insertId });
  } catch (err) {
    console.error("POST /api/workers error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

// ---------- EVENTS API (בייסיק) ----------

app.get("/api/events", authMiddleware, async (req, res) => {
  try {
    const [rows] = await dbPool.query(
      "SELECT * FROM provent_crm_events ORDER BY event_date DESC, created_at DESC"
    );
    res.json({ success: true, events: rows });
  } catch (err) {
    console.error("GET /api/events error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

app.post("/api/events", authMiddleware, async (req, res) => {
  try {
    const { title, event_date, event_type, location, client_id } = req.body || {};

    if (!title) {
      return res
        .status(400)
        .json({ success: false, error: "Missing title" });
    }

    const [result] = await dbPool.query(
      `
      INSERT INTO provent_crm_events (title, event_date, event_type, location, client_id)
      VALUES (?, ?, ?, ?, ?)
    `,
      [title, event_date || null, event_type || null, location || null, client_id || null]
    );

    res.json({ success: true, id: result.insertId });
  } catch (err) {
    console.error("POST /api/events error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
});

// ---------- SMS API ----------

app.get("/api/sms/test", authMiddleware, async (req, res) => {
  try {
    const result = await smsService.testSmsConnection();
    if (!result.success) {
      return res.json({ success: false, error: result.error });
    }
    res.json({
      success: true,
      message: result.message || "Token OK",
      token: result.token || null,
    });
  } catch (err) {
    console.error("GET /api/sms/test error:", err);
    res.status(500).json({ success: false, error: "Server error" });
  }
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

// ---------- START ----------

app.listen(PORT, () => {
  console.log(`✅ PROVENT CRM backend listening on port ${PORT}`);
});
