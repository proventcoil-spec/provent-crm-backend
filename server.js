import employeesRouter from './src/routes/employees.js';
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import authRouter from './src/routes/auth.js';
import clientsRouter from './src/routes/clients.js';
import eventsRouter from './src/routes/events.js';
import notesRouter from './src/routes/notes.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.json({ status: 'ok', message: 'Provent CRM API' });
});

app.use('/api/auth', authRouter);
app.use('/api/clients', clientsRouter);
app.use('/api/events', eventsRouter);
app.use('/api/notes', notesRouter);

app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Server error' });
});

app.listen(PORT, () => {
  console.log(`API listening on port ${PORT}`);
});
app.use('/api/employees', employeesRouter);
