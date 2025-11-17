import express from 'express';
import pool from '../db.js';
import { authRequired } from '../middleware/auth.js';

const router = express.Router();

// list notes for client
router.get('/client/:clientId', authRequired, async (req, res) => {
  const clientId = parseInt(req.params.clientId, 10);
  const [rows] = await pool.query(
    `SELECT n.id, n.note, n.created_at, u.full_name AS author
     FROM client_notes n
     JOIN users u ON n.user_id = u.id
     WHERE n.client_id = ?
     ORDER BY n.created_at DESC`,
    [clientId]
  );
  res.json(rows);
});

// add note
router.post('/', authRequired, async (req, res) => {
  const { client_id, note } = req.body;
  if (!client_id || !note) {
    return res.status(400).json({ error: 'Missing fields' });
  }
  await pool.query(
    'INSERT INTO client_notes (client_id, user_id, note) VALUES (?,?,?)',
    [client_id, req.user.id, note]
  );
  res.status(201).json({ message: 'Note added' });
});

export default router;
