// smsService.js
const axios = require("axios");

const SMS_API_URL = process.env.SMS_API_URL;
const SMS_USERNAME = process.env.SMS_USERNAME;
const SMS_USERNAME_FOR_TOKEN = process.env.SMS_USERNAME_FOR_TOKEN;
const SMS_PASSWORD = process.env.SMS_PASSWORD;

if (!SMS_API_URL || !SMS_USERNAME || !SMS_USERNAME_FOR_TOKEN || !SMS_PASSWORD) {
    console.log("⚠ SMS ENV missing");
}

async function getToken() {
    try {
        const xmlReq = `
            <getApiToken>
                <user>
                    <username>${SMS_USERNAME}</username>
                </user>
                <username>${SMS_USERNAME_FOR_TOKEN}</username>
                <action>new</action>
            </getApiToken>
        `;

        const response = await axios.post(SMS_API_URL, xmlReq, {
            headers: { "Content-Type": "application/xml" }
        });

        const token = response.data.match(/<message>(.*?)<\/message>/);

        return token ? token[1] : null;
    } catch (err) {
        console.error("Token Error:", err.message);
        return null;
    }
}

async function sendSms(phone, message) {
    const token = await getToken();
    if (!token) return { success: false, error: "Token failed" };

    const xmlReq = `
        <sendSms>
            <user>
                <username>${SMS_USERNAME}</username>
                <password>${SMS_PASSWORD}</password>
            </user>
            <msg>
                <recipient>${phone}</recipient>
                <message>${message}</message>
                <sender>PROVENT</sender>
            </msg>
            <token>${token}</token>
        </sendSms>
    `;

    try {
        const response = await axios.post(SMS_API_URL, xmlReq, {
            headers: { "Content-Type": "application/xml" }
        });

        return { success: true, response: response.data };
    } catch (err) {
        console.error("SMS Error:", err.message);
        return { success: false, error: err.message };
    }
}

module.exports = { sendSms };
