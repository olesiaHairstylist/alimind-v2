import os
import httpx
from dotenv import load_dotenv

load_dotenv()


async def fetch_rates_to_try() -> dict[str, float]:
    api_key = os.getenv("EXCHANGE_API_KEY")

    if not api_key:
        raise RuntimeError("EXCHANGE_API_KEY is missing")

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/TRY"

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    rates = data.get("conversion_rates", {})

    return {
        "USD": 1 / float(rates["USD"]),
        "EUR": 1 / float(rates["EUR"]),
        "RUB": 1 / float(rates["RUB"]),
    }