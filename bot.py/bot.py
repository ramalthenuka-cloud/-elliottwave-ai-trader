
import os
import logging

from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# ---------------- CONFIGURATION ----------------

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
PORT = int(os.getenv("PORT", "10000"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

BASE_URL = (RENDER_URL or WEBHOOK_URL or "").rstrip("/")

if not BASE_URL:
    raise RuntimeError(
        "RENDER_EXTERNAL_URL or WEBHOOK_URL is missing"
    )

# ---------------- TELEGRAM COMMANDS ----------------

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = (
        "Welcome to ElliottWaveAI Trader Bot! 🚀\n\n"
        "Your trading assistant is online.\n\n"
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Help menu\n"
        "/status - Bot status\n"
        "/markets - Supported markets\n"
        "/about - About this bot\n\n"
        "More trading analysis features are coming soon."
    )

    await update.message.reply_text(message)


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = (
        "📘 HELP MENU\n\n"
        "/start - Start the bot\n"
        "/help - Show help\n"
        "/status - Check bot status\n"
        "/markets - View planned markets\n"
        "/about - About the project\n\n"
        "This bot is currently under development."
    )

    await update.message.reply_text(message)


async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🟢 Bot Status: ONLINE\n"
        "Telegram connection: Active\n"
        "Webhook: Active\n"
        "Trading engine: Under development"
    )


async def markets(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = (
        "📊 PLANNED MARKET COVERAGE\n\n"
        "Binance Spot - Planned\n"
        "Bybit Spot - Planned\n"
        "Gold XAUUSD - Planned\n\n"
        "Market scanning is not active yet."
    )

    await update.message.reply_text(message)


async def about(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = (
        "🤖 ElliottWaveAI Trader Bot\n\n"
        "Planned features:\n"
        "• Elliott Wave analysis\n"
        "• Fibonacci levels\n"
        "• Support and resistance\n"
        "• Entry, Stop Loss and Take Profit\n"
        "• Market scanning\n\n"
        "This is an analysis project, not a "
        "guaranteed-profit trading system."
    )

    await update.message.reply_text(message)


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.exception(
        "Telegram update error",
        exc_info=context.error,
    )


# ---------------- TELEGRAM APPLICATION ----------------

telegram_app = (
    Application.builder()
    .token(TOKEN)
    .updater(None)
    .build()
)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CommandHandler("status", status))
telegram_app.add_handler(CommandHandler("markets", markets))
telegram_app.add_handler(CommandHandler("about", about))

telegram_app.add_error_handler(error_handler)


# ---------------- WEBHOOK HANDLERS ----------------

async def home(request):
    return web.json_response({
        "project": "ElliottWaveAI Trader Bot",
        "status": "online",
    })


async def telegram_webhook(request):
    if WEBHOOK_SECRET:
        received_secret = request.headers.get(
            "X-Telegram-Bot-Api-Secret-Token"
        )

        if received_secret != WEBHOOK_SECRET:
            raise web.HTTPUnauthorized()

    try:
        data = await request.json()
        telegram_update = Update.de_json(
            data=data,
            bot=telegram_app.bot,
        )

        await telegram_app.update_queue.put(telegram_update)

        return web.Response(text="OK")

    except Exception:
        logger.exception("Webhook processing error")
        raise web.HTTPBadRequest(text="Invalid update")


async def startup(app):
    await telegram_app.initialize()
    await telegram_app.start()

    webhook_options = {
        "url": f"{BASE_URL}/telegram",
        "allowed_updates": Update.ALL_TYPES,
    }

    if WEBHOOK_SECRET:
        webhook_options["secret_token"] = WEBHOOK_SECRET

    await telegram_app.bot.set_webhook(**webhook_options)

    logger.info("Telegram webhook configured successfully")


async def cleanup(app):
    await telegram_app.stop()
    await telegram_app.shutdown()

    logger.info("Telegram application stopped")


# ---------------- START SERVER ----------------

def main():
    server = web.Application()

    server.router.add_get("/", home)
    server.router.add_post("/telegram", telegram_webhook)

    server.on_startup.append(startup)
    server.on_cleanup.append(cleanup)

    logger.info("Starting ElliottWaveAI Trader Bot...")

    web.run_app(
        server,
        host="0.0.0.0",
        port=PORT,
    )


if __name__ == "__main__":
    main()
