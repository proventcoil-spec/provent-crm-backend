<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <title>PROVENT CRM - התחברות</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      direction: rtl;
      background: radial-gradient(circle at top, #1d4ed8, #020617);
      color: #e5e7eb;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    .login-card {
      background: rgba(15,23,42,0.96);
      padding: 24px 22px;
      border-radius: 16px;
      border: 1px solid #1f2937;
      width: 360px;
      max-width: 95vw;
      box-shadow: 0 20px 40px rgba(0,0,0,0.7);
    }
    h1 {
      margin: 0 0 8px 0;
      text-align: center;
      font-size: 22px;
    }
    .subtitle {
      text-align: center;
      font-size: 13px;
      color: #9ca3af;
      margin-bottom: 18px;
    }
    label {
      display: block;
      font-size: 13px;
      margin-bottom: 4px;
    }
    input {
      width: 100%;
      padding: 8px 9px;
      border-radius: 8px;
      border: 1px solid #374151;
      background: #020617;
      color: #e5e7eb;
      font-size: 14px;
      margin-bottom: 10px;
    }
    input:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 1px #3b82f6;
    }
    button {
      width: 100%;
      padding: 9px 0;
      border-radius: 999px;
      border: none;
      background: #3b82f6;
      color: #fff;
      font-size: 14px;
      cursor: pointer;
      margin-top: 4px;
    }
    button:hover {
      background: #2563eb;
    }
    .links {
      margin-top: 14px;
      text-align: center;
      font-size: 12px;
    }
    .links a {
      color: #60a5fa;
      text-decoration: none;
      display: inline-block;
      margin: 2px 0;
    }

    /* טוסט קטן להודעות */
    .toast {
      position: fixed;
      top: 20px;
      right: 50%;
      transform: translateX(50%);
      background: rgba(15,23,42,0.95);
      color: #e5e7eb;
      padding: 12px 18px;
      border-radius: 12px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.6);
      font-size: 14px;
      z-index: 9999;
      display: none;
    }
    .toast.show {
      display: block;
    }
  </style>
</head>
<body>

<div class="toast" id="toast"></div>

<div class="login-card">
  <h1>PROVENT CRM</h1>
  <div class="subtitle">התחברות לאיזור הניהול</div>

  <form id="loginForm">
    <label for="username">שם משתמש</label>
    <input id="username" type="text" autocomplete="username" />

    <label for="password">סיסמה</label>
    <input id="password" type="password" autocomplete="current-password" />

    <button type="submit">התחברות</button>
  </form>

  <div class="links">
    <div>
      <a href="https://www.provent.co.il" target="_blank">לאתר הראשי</a>
    </div>
    <div>
      <a href="https://www.instagram.com/provent.il?igsh=MTEwZmcya2xmODdvYQ%3D%3D&utm_source=qr" target="_blank">אינסטגרם</a>
      |
      <a href="https://www.tiktok.com/@provent.il?_r=1&_t=ZS-91aIk0JAo7t" target="_blank">טיקטוק</a>
    </div>
  </div>
</div>

<script>
  // שים לב: בלי רווחים ב־URL!
  const API_BASE_URL = "https://provent-crm-backend.onrender.com/api";

  function showToast(msg) {
    const t = document.getElementById("toast");
    t.textContent = msg;
    t.classList.add("show");
    setTimeout(() => t.classList.remove("show"), 3000);
  }

  async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
      showToast("חובה למלא שם משתמש וסיסמה");
      return;
    }

    try {
      const res = await fetch(API_BASE_URL + "/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });

      let data;
      try {
        data = await res.json();
      } catch (e) {
        const text = await res.text();
        console.error("Server raw response:", text);
        showToast("שגיאה בשרת (" + res.status + ")");
        return;
      }

      if (!res.ok || !data.success) {
        showToast(data.error || "שם משתמש או סיסמה שגויים");
        return;
      }

      localStorage.setItem("provent_crm_token", data.token);
      localStorage.setItem("provent_crm_user", JSON.stringify({
        username: data.username,
        role: data.role,
        fullName: data.fullName || ""
      }));

      // כניסה לאיזור הניהול
      window.location.href = "admin/index.html";

    } catch (err) {
      console.error("Network error:", err);
      showToast("שגיאה בחיבור לשרת (Network error)");
    }
  }

  document.getElementById("loginForm").addEventListener("submit", handleLogin);
</script>

</body>
</html>
