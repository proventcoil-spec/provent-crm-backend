// src/routes/employees.js
import express from "express";
import pool from "../db.js";
import { authRequired, requireRole } from "../middleware/auth.js";

const router = express.Router();

// GET /api/employees  – רק למנהל / סופר אדמין
router.get("/", authRequired, requireRole(["admin", "super_admin"]), async (req, res) => {
  try {
    const [rows] = await pool.query(
      "SELECT id, full_name, phone, email, role FROM employees ORDER BY id DESC"
    );
    res.json(rows);
  } catch (err) {
    console.error("Employees list error:", err);
    res.status(500).json({ message: "Server error" });
  }
});

export default router;
