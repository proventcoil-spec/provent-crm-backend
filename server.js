import express from "express";
import cors from "cors";
import dotenv from "dotenv";

import authRoutes from "./src/routes/auth.js";
import employeesRoutes from "./src/routes/employees.js";

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// בדיקה מהירה שהשרת חי
app.get("/", (req, res) => {
  res.send("Provent CRM backend is running");
});

// ראוטים
app.use("/api/auth", authRoutes);
app.use("/api/employees", employeesRoutes);

app.listen(port, () => {
  console.log(`API listening on port ${port}`);
});
