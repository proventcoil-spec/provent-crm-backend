// src/server.js
import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import authRoutes from "./routes/auth.js";

dotenv.config();

const app = express();

// לאפשר פרונט מקומי + הדומיין שלך
app.use(
  cors({
    origin: [
      "http://localhost:5173",
      "https://crm-pro.provent.co.il",
    ],
    credentials: true,
  })
);

app.use(express.json());

// בדיקה פשוטה
app.get("/api/test", (req, res) => {
  res.json({ ok: true });
});

// ראוטים של לוגין
app.use("/api/auth", authRoutes);

// כאן בעתיד נוסיף ראוטים לאירועים, לידים וכו'
// app.use("/api/events", eventsRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`API listening on port ${PORT}`);
});
