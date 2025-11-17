import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';
import pool from '../db.js';
import { authRequired, requireRole } from '../middleware/auth.js';

dotenv.config();

const router = express.Router();

// Login
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password required' });
  }
  try {
    const [rows] = await pool.query('SELECT * FROM users WHERE email = ?', [email]);
    const user = rows[0];
    if (!user) return res.status(401).json({ error: 'Invalid credentials' });
    const ok = await bcrypt.compare(password, user.password);
    if (!ok) return res.status(401).json({ error: 'Invalid credentials' });

    const token = jwt.sign(
      { id: user.id, role: user.role, full_name: user.full_name },
      process.env.JWT_SECRET,
      { expiresIn: '12h' }
    );
    res.json({
      token,
      user: {
        id: user.id,
        full_name: user.full_name,
        email: user.email,
        role: user.role
      }
    });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Server error' });
  }
});

// Create user (admin only)
router.post('/users', authRequired, requireRole(['admin']), async (req, res) => {
  const { full_name, email, password, role } = req.body;
  if (!full_name || !email || !password) {
    return res.status(400).json({ error: 'Missing fields' });
  }
  const validRoles = ['admin', 'team_lead', 'staff', 'client'];
  const finalRole = validRoles.includes(role) ? role : 'staff';
  try {
    const hash = await bcrypt.hash(password, 10);
    await pool.query(
      'INSERT INTO users (full_name, email, password_hash, role) VALUES (?,?,?,?)',
      [full_name, email, hash, finalRole]
    );
    res.status(201).json({ message: 'User created' });
  } catch (e) {
    console.error(e);
    if (e.code === 'ER_DUP_ENTRY') {
      return res.status(400).json({ error: 'Email already exists' });
    }
    res.status(500).json({ error: 'Server error' });
  }
});

// List users (admin only)
router.get('/users', authRequired, requireRole(['admin']), async (req, res) => {
  const [rows] = await pool.query(
    'SELECT id, full_name, email, role, created_at FROM users ORDER BY created_at DESC'
  );
  res.json(rows);
});

export default router;
