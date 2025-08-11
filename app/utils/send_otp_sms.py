import requests
import os

FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")

def send_otp_sms(phone, otp):
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        "variables_values": otp,
        "route": "otp",
        "numbers": phone,
    }
    headers = {
        'authorization': FAST2SMS_API_KEY,
        'Content-Type': "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        print("RAW RESPONSE:", response.text)  # Debug print

        if response.status_code == 200:
            json_resp = response.json()
            if json_resp.get("return") == True:
                print("✅ OTP sent successfully.")
                return True
            else:
                print("❌ OTP failed. Response:", json_resp)
                return False
        else:
            print("❌ Non-200 response:", response.status_code)
            return False

    except Exception as e:
        print("❌ SMS error:", e)
        return False
