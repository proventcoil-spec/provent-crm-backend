import bcrypt from "bcryptjs";
import pool from "../db.js";

async function seed() {
  const full_name = "Shlomi Provent";
  const email = "shlomi@provent.co.il";
  const password = "Provi2025!";
  const role = "super_admin";

  try {
    console.log("Ensuring users table exists...");
    await pool.query(`
      CREATE TABLE IF NOT EXISTS users (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        full_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        role ENUM('super_admin','admin','manager','employee','client') NOT NULL DEFAULT 'client',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    `);

    const hash = await bcrypt.hash(password, 10);

    const [rows] = await pool.query(
      "SELECT id FROM users WHERE email = ? LIMIT 1",
      [email]
    );

    if (rows.length) {
      const userId = rows[0].id;
      console.log("Admin exists, updating password and role...", userId);
      await pool.query(
        "UPDATE users SET full_name = ?, password_hash = ?, role = ? WHERE id = ?",
        [full_name, hash, role, userId]
      );
    } else {
      console.log("Inserting admin user...");
      await pool.query(
        "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        [full_name, email, hash, role]
      );
    }

    console.log("✅ Seed admin completed");
    process.exit(0);
  } catch (err) {
    console.error("SEED ERROR:", err);
    process.exit(1);
  }
}

seed();
