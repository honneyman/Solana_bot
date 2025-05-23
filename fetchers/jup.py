import httpx
import logging

async def fetch_jupiter_tokens():
    url = "https://quote-api.jup.ag/v6/tokens"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            # Log the raw response for debugging
            logging.info(f"🔍 Raw data preview: {str(data)[:500]}")  # truncate to avoid huge logs

            # Validate structure
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
