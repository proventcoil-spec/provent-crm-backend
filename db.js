
const mysql = require("mysql2/promise");

const pool = mysql.createPool({
  host: process.env.DB_HOST,      // לדוגמה: srvXXXX.hstgr.io (מ-Hostinger)
  user: process.env.DB_USER,      // לדוגמה: u894002499_provicrm
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,  // לדוגמה: u894002499_provicrm
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

module.exports = pool;
