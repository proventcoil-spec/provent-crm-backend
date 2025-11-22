const axios = require("axios");

const SMS_API_URL = process.env.SMS_API_URL;
const SMS_USERNAME = process.env.SMS_USERNAME;
const SMS_PASSWORD = process.env.SMS_PASSWORD;
const SMS_USERNAME_FOR_TOKEN = process.env.SMS_USERNAME_FOR_TOKEN;

// יצירת טוקן חדש מה-API
async function getToken() {
  const xml = `
    <getApiToken>
      <user>
        <username>${SMS_USERNAME}</username>
      </user>
      <username>${SMS_USERNAME_FOR_TOKEN}</username>
      <action>new</action>
    </getApiToken>
  `;

  const res = await axios.post(SMS_API_URL, xml, {
    headers: { "Content-Type": "application/xml" }
  });

  const token = res.data.match(/<message>(.*?)<\/message>/)?.[1];
  if (!token) throw new Error("Failed extracting token");

  return token;
}

// בדיקת טוקן בלבד
async function testSmsConnection() {
  try {
    const token = await getToken();
    return { success: true, message: "Token OK", token: token };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// שליחת SMS אמיתית
async function sendSms(to, message) {
  try {
    const token = await getToken();

    const xml = `
      <sendSms>
        <user>
          <username>${SMS_USERNAME}</username>
          <password>${SMS_PASSWORD}</password>
        </user>
        <msg>
          <recipient>${to}</recipient>
          <message>${message}</message>
          <sender>PROVENT</sender>
        </msg>
        <token>${token}</token>
      </sendSms>
    `;

    const res = await axios.post(SMS_API_URL, xml, {
      headers: { "Content-Type": "application/xml" }
    });

    return { success: true, response: res.data };

  } catch (e) {
    console.error("SMS ERROR:", e.message);
    return { success: false, error: e.message };
  }
}

module.exports = {
  getToken,
  testSmsConnection,
  sendSms
};
