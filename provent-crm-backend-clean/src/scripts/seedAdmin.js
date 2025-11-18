import bcrypt from 'bcrypt';
import pool from '../db.js';

async function seed() {
  const full_name = 'Shlomi Provent';
  const email = 'shlomi@provent.co.il';
  const password = 'Provent123!';
  const role = 'super_admin';

  const hash = await bcrypt.hash(password, 10);

  const [rows] = await pool.query(
    'SELECT id FROM users WHERE email = ? LIMIT 1',
    [email]
  );

  if (rows.length) {
    console.log('User already exists, updating password hash...');
    await pool.query(
      'UPDATE users SET full_name = ?, password_hash = ?, role = ? WHERE email = ?',
      [full_name, hash, role, email]
    );
  } else {
    console.log('Inserting admin user...');
    await pool.query(
      'INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, ?)',
      [full_name, email, hash, role]
    );
  }

  console.log('Done. You can now login with:', email, password);
  process.exit(0);
}

seed().catch((err) => {
  console.error('SEED ERROR:', err);
  process.exit(1);
});