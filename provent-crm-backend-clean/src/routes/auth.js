import express from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import pool from '../db.js';
import { authRequired } from '../middleware/auth.js';

const router = express.Router();

// POST /api/auth/login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body || {};

    if (!email || !password) {
      return res.status(400).json({ message: 'חסר אימייל או סיסמה' });
    }

    const [rows] = await pool.query(
      'SELECT id, full_name, email, password_hash, role FROM users WHERE email = ? LIMIT 1',
      [email]
    );

    if (!rows.length) {
      return res.status(401).json({ message: 'אימייל או סיסמה לא נכונים' });
    }

    const user = rows[0];
    const ok = await bcrypt.compare(password, user.password_hash);

    if (!ok) {
      return res.status(401).json({ message: 'אימייל או סיסמה לא נכונים' });
    }

    const payload = {
      id: user.id,
      full_name: user.full_name,
      email: user.email,
      role: user.role,
    };

    const token = jwt.sign(payload, process.env.JWT_SECRET, {
      expiresIn: '7d',
    });

    return res.json({ token, user: payload });
  } catch (err) {
    console.error('LOGIN ERROR:', err);
    return res.status(500).json({ message: 'שגיאה בכניסה למערכת' });
  }
});

// GET /api/auth/me
router.get('/me', authRequired, async (req, res) => {
  try {
    const [rows] = await pool.query(
      'SELECT id, full_name, email, role FROM users WHERE id = ? LIMIT 1',
      [req.user.id]
    );

    if (!rows.length) {
      return res.status(404).json({ message: 'המשתמש לא נמצא' });
    }

    return res.json(rows[0]);
  } catch (err) {
    console.error('ME ERROR:', err);
    return res.status(500).json({ message: 'שגיאה בטעינת המשתמש' });
  }
});

export default router;