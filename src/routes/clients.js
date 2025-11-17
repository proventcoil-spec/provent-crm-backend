import express from 'express';
import pool from '../db.js';
import { authRequired } from '../middleware/auth.js';

const router = express.Router();

// List clients
router.get('/', authRequired, async (req, res) => {
  const [rows] = await pool.query(
    'SELECT * FROM clients ORDER BY created_at DESC'
  );
  res.json(rows);
});

// Create / update client
router.post('/', authRequired, async (req, res) => {
  const c = req.body;
  if (!c.name || !c.phone) {
    return res.status(400).json({ error: 'Name and phone required' });
  }
  try {
    if (c.id) {
      await pool.query(
        `UPDATE clients SET
          name=?, phone=?, email=?, source=?, event_date=?, event_location=?,
          event_type=?, rep=?, notes=?, quote_amount=?, status=?, deposit_amount=?,
          agreement_url=?, agreement_signed=?
         WHERE id=?`,
        [
          c.name, c.phone, c.email || null, c.source || null, c.event_date || null,
          c.event_location || null, c.event_type || null, c.rep || null,
          c.notes || null, c.quote_amount ?? null, c.status || 'lead',
          c.deposit_amount ?? 0, c.agreement_url || null,
          c.agreement_signed ? 1 : 0, c.id
        ]
      );
      res.json({ message: 'Client updated' });
    } else {
      const [result] = await pool.query(
        `INSERT INTO clients
          (name, phone, email, source, event_date, event_location, event_type,
           rep, notes, quote_amount, status, deposit_amount, agreement_url, agreement_signed)
         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
        [
          c.name, c.phone, c.email || null, c.source || null, c.event_date || null,
          c.event_location || null, c.event_type || null, c.rep || null,
          c.notes || null, c.quote_amount ?? null, c.status || 'lead',
          c.deposit_amount ?? 0, c.agreement_url || null,
          c.agreement_signed ? 1 : 0
        ]
      );
      res.status(201).json({ message: 'Client created', id: result.insertId });
    }
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Server error' });
  }
});

export default router;
