import express from 'express';
import pool from '../db.js';
import { authRequired, requireRole } from '../middleware/auth.js';

const router = express.Router();

// GET /api/employees - רק מנהלים/אדמין
router.get('/', authRequired, requireRole(['super_admin', 'manager', 'manager_secondary']), async (req, res) => {
  try {
    const [rows] = await pool.query(
      'SELECT id, full_name, phone, role FROM users WHERE role IN ("employee", "manager", "manager_secondary") ORDER BY full_name'
    );
    res.json(rows);
  } catch (err) {
    console.error('EMPLOYEES LIST ERROR:', err);
    res.status(500).json({ message: 'שגיאה בטעינת עובדים' });
  }
});

export default router;