
require("dotenv").config();
const express = require("express");
const cors = require("cors");
const jwt = require("jsonwebtoken");
const pool = require("./db");

const app = express();
const PORT = process.env.PORT || 10000;
const JWT_SECRET = process.env.JWT_SECRET || "CHANGE_ME_SECRET";

app.use(cors({
  origin: "*"
}));

app.use(express.json());

// בדיקת בריאות בסיסית
app.get("/", (req, res) => {
  res.json({ status: "ok", message: "Provent CRM backend is running" });
});

function createToken(user) {
  return jwt.sign(
    {
      id: user.id,
      username: user.username,
      role: user.role
    },
    JWT_SECRET,
    { expiresIn: "12h" }
  );
}

function authMiddleware(req, res, next) {
  const authHeader = req.headers["authorization"];
  if (!authHeader) {
    return res.status(401).json({ success: false, message: "No token provided" });
  }
  const parts = authHeader.split(" ");
  if (parts.length !== 2 || parts[0] !== "Bearer") {
    return res.status(401).json({ success: false, message: "Invalid token format" });
  }
  const token = parts[1];
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    console.error("JWT error:", err.message);
    return res.status(401).json({ success: false, message: "Invalid or expired token" });
  }
}

// לוגין – משתמשים מתוך טבלת users
app.post("/api/auth/login", async (req, res) => {
  const { username, password } = req.body || {};

  if (!username || !password) {
    return res.status(400).json({
      success: false,
      message: "חסר שם משתמש או סיסמה"
    });
  }

  try {
    const [rows] = await pool.query(
      "SELECT * FROM users WHERE username = ? AND password = ? LIMIT 1",
      [username, password]
    );

    if (!rows || rows.length === 0) {
      return res.status(401).json({
        success: false,
        message: "שם משתמש או סיסמה שגויים"
      });
    }

    const user = rows[0];
    const token = createToken(user);

    return res.json({
      success: true,
      token,
      role: user.role,
      user: {
        id: user.id,
        username: user.username,
        full_name: user.full_name,
        phone: user.phone
      }
    });
  } catch (err) {
    console.error("Login error:", err);
    return res.status(500).json({
      success: false,
      message: "שגיאה בשרת בעת ניסיון התחברות"
    });
  }
});

// קבלת פרטי המשתמש המחובר
app.get("/api/me", authMiddleware, async (req, res) => {
  try {
    const [rows] = await pool.query(
      "SELECT id, username, full_name, phone, role FROM users WHERE id = ? LIMIT 1",
      [req.user.id]
    );

    if (!rows || rows.length === 0) {
      return res.status(404).json({ success: false, message: "User not found" });
    }

    return res.json({ success: true, user: rows[0] });
  } catch (err) {
    console.error("Me error:", err);
    return res.status(500).json({
      success: false,
      message: "שגיאה בשרת"
    });
  }
});

// בהמשך אפשר להוסיף כאן /api/dashboard/owner, /api/events וכו'

app.listen(PORT, () => {
  console.log(`Provent CRM backend listening on port ${PORT}`);
});
