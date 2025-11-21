// smsService.js
// שירות SMS ל-Provent CRM – 019SMS (טוקן + שליחת SMS)
//
// שים לב:
// 1. כתובת ה-API מגיעה מ-SMS_API_URL (למשל: https://019sms.co.il/api)
// 2. מבנה ה-XML ל-sendSms מבוסס על לוגיקה סטנדרטית,
//    ייתכן שתצטרך להתאים שמות תגיות לפי הדוקומנטציה הרשמית של 019SMS.

// חבילות נדרשות:
// npm install axios xml2js

const axios = require("axios");
const xml2js = require("xml2js");

// ערכים מתוך .env / Environment של Render
const SMS_API_URL = process.env.SMS_API_URL;             // לדוגמה: https://019sms.co.il/api
const SMS_USERNAME = process.env.SMS_USERNAME;           // לדוגמה: provent12
const SMS_USERNAME_FOR_TOKEN = process.env.SMS_USERNAME_FOR_TOKEN || SMS_USERNAME;
const SMS_PASSWORD = process.env.SMS_PASSWORD;           // אם נדרש בהמשך ע"י 019 – נשמש בזה

if (!SMS_API_URL) {
  console.warn("WARNING: SMS_API_URL is not defined. SMS service will not work properly.");
}

let cachedToken = null;
let tokenExpiresAt = null; // Date או null

// ======================= עזר ל-XML =======================

// XML לקבלת טוקן לפי הדוגמה שלך
function buildGetTokenXml() {
  return `<?xml version="1.0" encoding="utf-8"?>
<getApiToken>
  <user>
    <username>${SMS_USERNAME}</username>
  </user>
  <user>
    <username>${SMS_USERNAME_FOR_TOKEN}</username>
  </user>
  <action>new</action>
</getApiToken>`;
}

// XML לשליחת הודעה – יתכן שיהיה צורך לשנות לפי הדוקו הרשמי של 019
function buildSendSmsXml({ to, text, token, senderName }) {
  // senderName – שם השולח שיופיע אצל הלקוח (אם המערכת שלהם מאפשרת)
  const safeSender = senderName || "ProventCRM";

  // כאן אני בונה XML סטנדרטי. אם 019SMS דורשים מבנה אחר,
  // פשוט תצלם לי את הדף "sendSms" ואעדכן.
  return `<?xml version="1.0" encoding="utf-8"?>
<sendSms>
  <apiToken>${token}</apiToken>
  <user>
    <username>${SMS_USERNAME}</username>
  </user>
  <msg>
    <recipient>${to}</recipient>
    <text>${escapeXml(text)}</text>
    <sender>${safeSender}</sender>
  </msg>
</sendSms>`;
}

// פונקציה קטנה לבריחת תווים בעייתיים ב-XML
function escapeXml(unsafe) {
  if (!unsafe) return "";
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

// ======================= טוקן =======================

// בקשת טוקן חדש מה-API
async function fetchNewToken() {
  if (!SMS_API_URL || !SMS_USERNAME || !SMS_USERNAME_FOR_TOKEN) {
    throw new Error("SMS API settings missing (SMS_API_URL / SMS_USERNAME / SMS_USERNAME_FOR_TOKEN)");
  }

  const xmlBody = buildGetTokenXml();

  const { data } = await axios.post(SMS_API_URL, xmlBody, {
    headers: { "Content-Type": "application/xml" },
    timeout: 15000,
  });

  // data זה XML – ממירים לאובייקט JS
  const parsed = await xml2js.parseStringPromise(data, { explicitArray: false });

  // לפי הדוגמה – השורש הוא <getApiToken> ... </getApiToken>
  const root = parsed.getApiToken || parsed;

  const status = root.status;
  const message = root.message;           // אצל הרבה מערכות זה ה-token
  const expiration = root.expiration_date;

  if (!message) {
    console.error("SMS getApiToken response (no message/token):", root);
    throw new Error("SMS getApiToken: no token (message) in response");
  }

  cachedToken = message;
  tokenExpiresAt = expiration ? new Date(expiration) : null;

  console.log("SMS token received. Expires at:", tokenExpiresAt);

  return {
    token: cachedToken,
    expiration: tokenExpiresAt,
    raw: root,
  };
}

// מחזיר טוקן תקף – אם פג/אין, יביא חדש
async function getToken() {
  const now = new Date();
  if (!cachedToken || !tokenExpiresAt || tokenExpiresAt <= now) {
    return fetchNewToken();
  }
  return { token: cachedToken, expiration: tokenExpiresAt };
}

// ======================= שליחת הודעה =======================

// שליחת SMS ללקוח / עובד
async function sendSms({ to, text, senderName }) {
  if (!to || !text) {
    throw new Error("Missing 'to' or 'text' for SMS");
  }

  const { token } = await getToken();

  const xmlBody = buildSendSmsXml({ to, text, token, senderName });

  const { data } = await axios.post(SMS_API_URL, xmlBody, {
    headers: { "Content-Type": "application/xml" },
    timeout: 15000,
  });

  // תגובת XML – ממירים ל-JS
  const parsed = await xml2js.parseStringPromise(data, { explicitArray: false });

  // כאן אנחנו מנחשים מבנה אפשרי, כי אין דוקו מלא:
  // לדוגמה:
  // <sendSms>
  //   <status>0</status>
  //   <message>OK</message>
  //   <sms_id>123456</sms_id>
  // </sendSms>
  //
  // אם יש מבנה אחר – תצלם ונעדכן.

  const root =
    parsed.sendSms ||
    parsed.response ||
    parsed; // בהתאם למה שהמערכת מחזירה בפועל

  const status = root.status;
  const message = root.message || root.msg || "";

  // נחשב הצלחה לפי status:
  // 0 / "0" / "success" נחשב הצלחה
  const isSuccess =
    status === 0 ||
    status === "0" ||
    (typeof status === "string" && status.toLowerCase() === "success");

  if (!isSuccess) {
    console.error("SMS send error response:", root);
    throw new Error("SMS send failed: " + JSON.stringify(root));
  }

  return {
    success: true,
    status,
    message,
    raw: root,
  };
}

// ======================= בדיקת חיבור =======================

async function testSmsConnection() {
  const { token, expiration, raw } = await getToken();
  // לא נחשוף טוקן מלא בלוג ללקוח, רק בשביל בדיקה פנימית
  const shortToken = token ? token.substring(0, 6) + "..." : null;

  return {
    tokenPreview: shortToken,
    expiration,
    providerRaw: raw,
  };
}

module.exports = {
  getToken,
  sendSms,
  testSmsConnection,
};