// src/scripts/seedAdmin.js
import bcrypt from 'bcryptjs';
import pool from '../db.js';

async function seed() {
  const full_name = 'Shlomi Provent';
  const email = 'shlomi@provent.co.il';
  const password = 'Provent2025!'; // אפשר לשנות לסיסמה אחרת
  const role = 'super_admin';

  try {
    const password_hash = await bcrypt.hash(password, 10);

    const [result] = await pool.query(
      `INSERT INTO users (full_name, email, password_hash, role, created_at)
       VALUES (?, ?, ?, ?, NOW())`,
      [full_name, email, password_hash, role]
    );

    console.log('✅ Admin user created with id:', result.insertId);
    console.log('Email:', email);
    console.log('Password:', password);
  } catch (err) {
    console.error('❌ Error seeding admin user:', err);
  } finally {
    await pool.end();
    process.exit(0);
  }
}

seed();