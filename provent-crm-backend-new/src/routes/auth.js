import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';
import pool from '../db.js';

dotenv.config();

const router = express.Router();

// Login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }

    const [rows] = await pool.query(
      'SELECT * FROM users WHERE email = ?',
      [email]
    );

    if (!rows || rows.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const user = rows[0];
    const hash = user.password;

    if (!hash) {
      console.error('User has no password in DB:', user);
      return res.status(500).json({ error: 'Server password error' });
    }

    const ok = await bcrypt.compare(password, hash);
    if (!ok) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign(
      {
        id: user.id,
        role: user.role,
        full_name: user.full_name,
      },
      process.env.JWT_SECRET,
      { expiresIn: '12h' }
    );

    return res.json({
      token,
      user: {
        id: user.id,
        full_name: user.full_name,
        email: user.email,
        role: user.role,
      },
    });
  } catch (err) {
    console.error('Login error:', err);
    return res.status(500).json({ error: 'Server error' });
  }
});

// Dev helper: create hash for a password
router.get('/dev/hash', async (req, res) => {
  try {
    const password = req.query.password || 'Provent2024!';
    const hash = await bcrypt.hash(password, 10);
    res.json({ password, hash });
  } catch (err) {
    console.error('Hash error:', err);
    res.status(500).json({ error: 'Hash error' });
  }
});

export default router;