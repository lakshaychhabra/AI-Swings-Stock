# login_z.py
from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ZERODHA_API_KEY")
api_secret = os.getenv("ZERODHA_API_SECRET")

kite = KiteConnect(api_key=api_key)
print("🔗 Login URL:", kite.login_url())

request_token = input("Paste the request_token from redirected URL: ").strip()

# Exchange for access token
data = kite.generate_session(request_token, api_secret=api_secret)
access_token = data["access_token"]
print(f"✅ Access token: {access_token}")

# Optionally: overwrite .env
with open(".env", "r") as f:
    lines = f.readlines()

with open(".env", "w") as f:
    for line in lines:
        if line.startswith("ZERODHA_TOKEN"):
            f.write(f"ZERODHA_TOKEN={access_token}\n")
        else:
            f.write(line)
