import express from 'express';
import pool from '../db.js';
import { authRequired } from '../middleware/auth.js';

const router = express.Router();

// basic events CRUD (simplified)
router.get('/', authRequired, async (req, res) => {
  const [rows] = await pool.query(
    'SELECT * FROM events ORDER BY event_date DESC'
  );
  res.json(rows);
});

router.post('/', authRequired, async (req, res) => {
  const e = req.body;
  if (!e.client_id || !e.title || !e.event_date) {
    return res.status(400).json({ error: 'Missing fields' });
  }
  try {
    if (e.id) {
      await pool.query(
        `UPDATE events SET client_id=?, title=?, event_date=?, event_location=?, event_type=?, timeline=? WHERE id=?`,
        [
          e.client_id, e.title, e.event_date, e.event_location || null,
          e.event_type || null, e.timeline ? JSON.stringify(e.timeline) : null,
          e.id
        ]
      );
      res.json({ message: 'Event updated' });
    } else {
      const [result] = await pool.query(
        `INSERT INTO events (client_id, title, event_date, event_location, event_type, timeline)
         VALUES (?,?,?,?,?,?)`,
        [
          e.client_id, e.title, e.event_date,
          e.event_location || null, e.event_type || null,
          e.timeline ? JSON.stringify(e.timeline) : null
        ]
      );
      res.status(201).json({ message: 'Event created', id: result.insertId });
    }
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Server error' });
  }
});

export default router;
