// src/server.js
import express from "express";
import cors from "cors";
import helmet from "helmet";
import dotenv from "dotenv";

import authRoutes from "./routes/auth.js";
import employeesRoutes from "./routes/employees.js";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3306;

// CORS – לאפשר גם ל־localhost וגם ל־crm-pro.provent.co.il
const allowedOrigins = [
  "http://localhost:5173",
  "http://localhost:3000",
  "https://crm-pro.provent.co.il"
];

app.use(
  cors({
    origin: function (origin, callback) {
      // לאפליקציה בלי origin (למשל Postman)
      if (!origin) return callback(null, true);
      if (allowedOrigins.includes(origin)) {
        return callback(null, true);
      }
      return callback(new Error("Not allowed by CORS"), false);
    },
    credentials: true
  })
);

app.use(helmet());
app.use(express.json());

// טסט פשוט
app.get("/api/test", (req, res) => {
  res.json({ status: "ok", message: "Provent CRM backend is running" });
});

// ראוטים
app.use("/api/auth", authRoutes);
app.use("/api/employees", employeesRoutes);

// 404 ל־API
app.use("/api/*", (req, res) => {
  res.status(404).json({ message: "API route not found" });
});

// סטטוס כללי
app.get("/", (req, res) => {
  res.send("Provent CRM backend");
});

app.listen(PORT, () => {
  console.log(`API listening on port ${PORT}`);
});
