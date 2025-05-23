import os
import asyncio
import logging
from aiohttp import web
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from filters import is_token_valid
from alert import send_alert
from fetchers.birdeye import fetch_token_info_birdeye
from fetchers.jup import fetch_jupiter_tokens

load_dotenv()
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in environment variables.")

# --- Web server (for Cyclic.sh / Railway / Fly.io) ---
async def handle_ping(request):
    return web.Response(text="OK")

# --- Telegram Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot is live and tracking Solana tokens!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running...")

async def hot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("🔥 Received /hot command")
    try:
        tokens = await fetch_jupiter_tokens()
        hot_tokens = sorted(tokens, key=lambda x: x.get("volume", 0), reverse=True)[:5]

        if not hot_tokens:
            await update.message.reply_text("⚠️ No hot tokens found.")
            return

        response = "🔥 Hot Tokens (Top 5 by 24h Volume):\n"
        for token in hot_tokens:
            name = token.get("name", "Unknown")
            symbol = token.get("symbol", "???")
            volume = token.get("volume", 0)
            response += f"• {name} ({symbol}) — 24h Volume: ${volume:,.0f}\n"

        await update.message.reply_text(response)

    except Exception as e:
        logging.error(f"❌ Error in /hot command: {e}")
        await update.message.reply_text("⚠️ Failed to fetch hot tokens.")

# --- Telegram Bot Loop ---
async def run_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("hot", hot))

    logging.info("🤖 Telegram bot starting...")
    await app.initialize()
    await app.start()
    await app.bot.delete_webhook(drop_pending_updates=True)

    while True:
        await asyncio.sleep(3600)

# --- Real-Time Token Monitor ---
async def process_tokens():
    while True:
        logging.info("🔍 Fetching tokens...")
        try:
            tokens = await fetch_jupiter_tokens()

            for token in tokens:
                if not isinstance(token, dict):
                    logging.warning("⚠️ Skipping invalid token (not a dict)")
                    continue

                if await is_token_valid(token):
                    chat_id = int(CHAT_ID) if CHAT_ID else 123456789
                    await send_alert(token, chat_id)

        except Exception as e:
            logging.error(f"❌ Error in token processing: {e}")

        await asyncio.sleep(60)

# --- Main Entry Point ---
async def main():
    app = web.Application()
    app.add_routes([web.get('/', handle_ping)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logging.info("🌐 Web server running on port 8080")

    await asyncio.gather(
        run_telegram_bot(),
        process_tokens()
    )

if __name__ == "__main__":
    asyncio.run(main())
