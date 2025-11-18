import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import authRoutes from './src/routes/auth.js';
import employeesRoutes from './src/routes/employees.js';

dotenv.config();

const app = express();

// basic middlewares
app.use(cors());
app.use(express.json());

// health checks
app.get('/', (req, res) => {
  res.send('Provent CRM API is running');
});

app.get('/api/test', (req, res) => {
  res.json({ ok: true, message: 'API test ok' });
});

// routes
app.use('/api/auth', authRoutes);
app.use('/api/employees', employeesRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log('API listening on port', PORT);
});