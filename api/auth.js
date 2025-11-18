// src/api/auth.js
import { API_BASE_URL } from "./config";

export async function loginRequest(email, password) {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.message || "שגיאה בהתחברות");
  }

  // שמירה ב-localStorage
  localStorage.setItem("provent_crm_token", data.token);
  localStorage.setItem("provent_crm_user", JSON.stringify(data.user));

  return data.user;
}

export function getStoredUser() {
  const raw = localStorage.getItem("provent_crm_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function getAuthToken() {
  return localStorage.getItem("provent_crm_token");
}

export function logout() {
  localStorage.removeItem("provent_crm_token");
  localStorage.removeItem("provent_crm_user");
}