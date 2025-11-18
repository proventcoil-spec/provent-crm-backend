import express from 'express';
import pool from '../db.js';
import { authRequired, requireRole } from '../middleware/auth.js';
import bcrypt from 'bcryptjs';

const router = express.Router();

// Get employees list
router.get('/', authRequired, requireRole(['admin', 'super_admin', 'manager']), async (req, res) => {
  try {
    const [rows] = await pool.query(
      'SELECT id, full_name, email, role, created_at FROM users WHERE role IN ("employee", "manager", "admin") ORDER BY created_at DESC'
    );
    res.json(rows);
  } catch (err) {
    console.error('Error fetching employees:', err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Create new employee
router.post('/', authRequired, requireRole(['admin', 'super_admin']), async (req, res) => {
  try {
    const { full_name, email, password, role } = req.body;

    if (!full_name || !email || !password) {
      return res.status(400).json({ error: 'Missing fields' });
    }

    const employeeRole = role || 'employee';

    const [existing] = await pool.query('SELECT id FROM users WHERE email = ?', [email]);
    if (existing.length > 0) {
      return res.status(409).json({ error: 'Email already exists' });
    }

    const hash = await bcrypt.hash(password, 10);

    const [result] = await pool.query(
      'INSERT INTO users (full_name, email, password, role, created_at) VALUES (?, ?, ?, ?, NOW())',
      [full_name, email, hash, employeeRole]
    );

    res.status(201).json({
      id: result.insertId,
      full_name,
      email,
      role: employeeRole,
    });
  } catch (err) {
    console.error('Error creating employee:', err);
    res.status(500).json({ error: 'Server error' });
  }
});

// Delete employee
router.delete('/:id', authRequired, requireRole(['admin', 'super_admin']), async (req, res) => {
  try {
    const { id } = req.params;

    if (Number(id) === req.user.id) {
      return res.status(400).json({ error: 'Cannot delete yourself' });
    }

    await pool.query('DELETE FROM users WHERE id = ?', [id]);
    res.json({ success: true });
  } catch (err) {
    console.error('Error deleting employee:', err);
    res.status(500).json({ error: 'Server error' });
  }
});

export default router;