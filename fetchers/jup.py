import httpx
import logging

async def fetch_jupiter_tokens():
    url = "https://quote-api.jup.ag/v6/tokens"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            # ✅ FIX: Check if data is a dict and contains "tokens"
            if isinstance(data, dict) and "tokens" in data:
                tokens = list(data["tokens"].values())
                logging.info(f"✅ Fetched {len(tokens)} tokens from Jupiter")
                return tokens
            else:
                logging.error("❌ Unexpected data format (not a dict or missing 'tokens')")
                return []
    except Exception as e:
        logging.error(f"❌ Error fetching Jupiter tokens: {e}")
        return []
