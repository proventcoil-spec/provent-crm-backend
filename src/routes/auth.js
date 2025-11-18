// src/routes/auth.js
import express from "express";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import pool from "../db.js";

const router = express.Router();

// POST /api/auth/login
router.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: "חסר מייל או סיסמה" });
    }

    // משתמש לפי מייל
    const [rows] = await pool.query(
      "SELECT id, full_name, email, password_hash, role FROM users WHERE email = ? LIMIT 1",
      [email]
    );

    if (rows.length === 0) {
      return res.status(401).json({ message: "מייל או סיסמה לא נכונים" });
    }

    const user = rows[0];

    // בדיקת סיסמה
    const match = await bcrypt.compare(password, user.password_hash);
    if (!match) {
      return res.status(401).json({ message: "מייל או סיסמה לא נכונים" });
    }

    // יצירת טוקן
    const payload = {
      id: user.id,
      full_name: user.full_name,
      email: user.email,
      role: user.role, // super_admin, manager, worker, client
    };

    const token = jwt.sign(payload, process.env.JWT_SECRET, {
      expiresIn: "12h",
    });

    // לא להחזיר את ה-hash
    delete user.password_hash;

    res.json({
      token,
      user: payload,
    });
  } catch (err) {
    console.error("LOGIN ERROR:", err);
    res.status(500).json({ message: "שגיאה בשרת" });
  }
});

// GET /api/auth/me  – לבדוק טוקן קיים
router.get("/me", (req, res) => {
  const authHeader = req.headers.authorization || "";
  const token = authHeader.startsWith("Bearer ")
    ? authHeader.slice(7)
    : null;

  if (!token) {
    return res.status(401).json({ message: "אין טוקן" });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    res.json({ user: decoded });
  } catch (err) {
    return res.status(401).json({ message: "טוקן לא תקין או פג תוקף" });
  }
});

export default router;
