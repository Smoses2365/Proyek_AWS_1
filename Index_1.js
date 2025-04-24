import 'dotenv/config';               // load .env ke process.env
import express from 'express';
import mysql from 'mysql2/promise';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

// 1) Pool koneksi ke Aurora (MySQL‑compatible)
const pool = mysql.createPool({
  host:     process.env.DB_HOST,      // Aurora endpoint
  port:     +process.env.DB_PORT,     // 3306
  user:     process.env.DB_USER,      // misal "admin"
  password: process.env.DB_PASS,      // password Aurora Anda
  database: process.env.DB_NAME,      // misal "todo_app"
  waitForConnections: true,
  connectionLimit:    10
});

// 2) CRUD To‑Do List
app.get('/todos', async (req, res) => {
  const [rows] = await pool.query('SELECT * FROM todos;');
  res.json(rows);
});

app.post('/todos', async (req, res) => {
  const { title } = req.body;
  const [result] = await pool.query(
    'INSERT INTO todos (title) VALUES (?);',
    [title]
  );
  res.status(201).json({ id: result.insertId, title, completed: false });
});

app.put('/todos/:id', async (req, res) => {
  const { id }        = req.params;
  const { title, completed } = req.body;
  await pool.query(
    'UPDATE todos SET title = ?, completed = ? WHERE id = ?;',
    [title, completed, id]
  );
  res.sendStatus(204);
});

app.delete('/todos/:id', async (req, res) => {
  const { id } = req.params;
  await pool.query('DELETE FROM todos WHERE id = ?;', [id]);
  res.sendStatus(204);
});

// 3) CRUD Event Reminder
app.get('/events', async (req, res) => {
  const [rows] = await pool.query('SELECT * FROM events;');
  res.json(rows);
});

app.post('/events', async (req, res) => {
  const { name, date, category } = req.body;
  // category ∈ ['absolutely important','important','moderate']
  const [result] = await pool.query(
    'INSERT INTO events (name, date, category) VALUES (?,?,?);',
    [name, date, category]
  );
  res.status(201).json({ id: result.insertId, name, date, category });
});

app.put('/events/:id', async (req, res) => {
  const { id } = req.params;
  const { name, date, category } = req.body;
  await pool.query(
    'UPDATE events SET name = ?, date = ?, category = ? WHERE id = ?;',
    [name, date, category, id]
  );
  res.sendStatus(204);
});

app.delete('/events/:id', async (req, res) => {
  const { id } = req.params;
  await pool.query('DELETE FROM events WHERE id = ?;', [id]);
  res.sendStatus(204);
});

// 4) Notification: urutkan by priority category
app.get('/events/notifications', async (req, res) => {
  const sql = `
    SELECT id, name, date, category
      FROM events
    ORDER BY
      CASE category
        WHEN 'absolutely important' THEN 1
        WHEN 'important'            THEN 2
        WHEN 'moderate'             THEN 3
        ELSE 4
      END,
      date ASC;
  `;
  const [rows] = await pool.query(sql);
  res.json(rows);
});

// 5) Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
