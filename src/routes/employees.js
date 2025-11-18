// backend/src/routes/employees.js
import express from 'express';
import pool from '../db.js';
import { authRequired, requireRole } from '../middleware/auth.js';

const router = express.Router();

// החזרת כל העובדים (לא כולל סופר אדמינים)
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

// יצירת עובד חדש
router.post('/', authRequired, requireRole(['admin', 'super_admin']), async (req, res) => {
  try {
    const { full_name, email, password, role } = req.body;

    if (!full_name || !email || !password) {
      return res.status(400).json({ error: 'Missing fields' });
    }

    const userRole = role || 'employee';

    // לוודא שאין כפילות מייל
    const [existing] = await pool.query('SELECT id FROM users WHERE email = ?', [email]);
    if (existing.length > 0) {
      return res.status(409).json({ error: 'Email already exists' });
    }

    // הצפנת סיסמה
    const bcrypt = (await import('bcryptjs')).default;
    const hash = await bcrypt.hash(password, 10);

    const [result] = await pool.query(
      'INSERT INTO users (full_name, email, password, role, created_at) VALUES (?, ?, ?, ?, NOW())',
      [full_name, email, hash, userRole]
    );

    res.status(201).json({
      id: result.insertId,
      full_name,
      email,
      role: userRole,
    });
  } catch (err) {
    console.error('Error creating employee:', err);
    res.status(500).json({ error: 'Server error' });
  }
});

// מחיקת עובד
router.delete('/:id', authRequired, requireRole(['admin', 'super_admin']), async (req, res) => {
  try {
    const { id } = req.params;

    // לא מאפשרים למחוק את עצמך
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
