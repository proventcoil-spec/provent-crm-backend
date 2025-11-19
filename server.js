import express from "express";
import cors from "cors";
import dotenv from "dotenv";

import authRoutes from "./src/routes/auth.js";
import employeesRoutes from "./src/routes/employees.js";

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

// Simple health-check route
app.get("/", (req, res) => {
  res.json({ status: "ok", message: "Provent CRM backend is running" });
});

// API routes
app.use("/api/auth", authRoutes);
app.use("/api/employees", employeesRoutes);

const PORT = process.env.PORT || 3306;

app.listen(PORT, () => {
  console.log(`API listening on port ${PORT}`);
});
