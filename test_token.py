import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TRAVELPAYOUTS_TOKEN")

print("TOKEN EXISTS:", bool(token))
print("TOKEN PREFIX:", token[:6] if token else None)