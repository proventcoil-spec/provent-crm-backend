import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

import authRouter from './src/routes/auth.js';
import employeesRouter from './src/routes/employees.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3306;

app.use(cors());
app.use(express.json());

// health check
app.get('/', (req, res) => {
  res.json({ status: 'ok', message: 'Provent CRM API' });
});

app.use('/api/auth', authRouter);
app.use('/api/employees', employeesRouter);

// global error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Server error' });
});

app.listen(PORT, () => {
  console.log(`API listening on port ${PORT}`);
});