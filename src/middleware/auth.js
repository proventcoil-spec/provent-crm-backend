import mysql from "mysql2/promise";
import dotenv from "dotenv";

dotenv.config();

const pool = mysql.createPool({
  host: process.env.DB_HOST,      // srv1016.hstgr.io
  user: process.env.DB_USER,      // u894002499_provi  (אצלך)
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,  // u894002499_provi_crm
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

export default pool;
