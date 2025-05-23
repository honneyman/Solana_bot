import httpx
import logging

async def fetch_jupiter_tokens():
    url = "https://token.jup.ag/all"  # Updated to correct endpoint

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            # Preview the raw data in logs (limit to 500 chars)
            logging.info(f"🔍 Raw data preview: {str(data)[:500]}")

            if isinstance(data, list) and isinstance(data[0], dict):
                return data
            else:
                logging.error("❌ Unexpected data format (not a list of dicts)")
                return []

    except Exception as e:
        logging.error(f"❌ Error fetching Jupiter tokens: {e}")
        return []
