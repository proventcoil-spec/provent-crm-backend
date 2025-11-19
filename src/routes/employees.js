import express from "express";
import pool from "../db.js";
import { authRequired, requireRole } from "../middleware/auth.js";

const router = express.Router();

// Example: list employees assigned to the logged-in user
router.get("/", authRequired, async (req, res) => {
  try {
    const [rows] = await pool.query(
      "SELECT id, full_name, role, phone FROM employees ORDER BY id DESC LIMIT 100"
    );
    res.json(rows);
  } catch (err) {
    console.error("Employees list error:", err);
    res.status(500).json({ message: "Server error" });
  }
});

// Example: only managers / super_admin can create employees
router.post("/", authRequired, requireRole("manager", "super_admin"), async (req, res) => {
  const { full_name, role, phone } = req.body || {};

  if (!full_name || !role) {
    return res.status(400).json({ message: "full_name and role are required" });
  }

  try {
    const [result] = await pool.query(
      "INSERT INTO employees (full_name, role, phone) VALUES (?, ?, ?)",
      [full_name, role, phone || null]
    );

    res.status(201).json({ id: result.insertId, full_name, role, phone: phone || null });
  } catch (err) {
    console.error("Create employee error:", err);
    res.status(500).json({ message: "Server error" });
  }
});

export default router;
