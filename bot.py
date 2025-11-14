import os
import logging
import asyncio
from fastapi import FastAPI, Request
import uvicorn

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from config import BOT_TOKEN
from database import init_db
from handlers.start import start_command, help_command
from handlers.wishlist import (
    add_wish_start,
    wish_title,
    wish_description,
    wish_url,
    wish_price,
    wish_image,
    cancel_add_wish,
    my_wishlist,
    handle_menu_buttons,
    delete_wish_callback,
    confirm_delete_callback,
    cancel_delete_callback,
    edit_wish_callback,
    edit_field_choice_callback,
    edit_title_handler,
    edit_description_handler,
    edit_url_handler,
    edit_price_handler,
    edit_image_handler,
    cancel_edit_callback,
    TITLE,
    DESCRIPTION,
    URL,
    PRICE,
    IMAGE,
    EDIT_TITLE,
    EDIT_DESCRIPTION,
    EDIT_URL,
    EDIT_PRICE,
    EDIT_IMAGE,
)
from handlers.share import share_wishlist, view_shared_wishlist
from keyboards import (
    MY_WISHLIST_BUTTON,
    ADD_WISH_BUTTON,
    SHARE_BUTTON,
    SETTINGS_BUTTON,
    CANCEL_BUTTON,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- FastAPI app ---
app = FastAPI()
bot_app: Application  # will be initialized later


@app.get("/")
async def root():
    return {"message": "Bot is running!"}


# --- Telegram webhook endpoint ---
@app.post(f"/telegram/{BOT_TOKEN}")
async def telegram_webhook(req: Request):
    """Receive updates from Telegram via webhook."""
    json_data = await req.json()
    update = Update.de_json(json_data, bot_app.bot)
    await bot_app.update_queue.put(update)
    return {"ok": True}


# --- Background task ---
async def background_task(application: Application):
    while True:
        chat_ids = os.environ.get("TELEGRAM_CHAT_ID", "").split(",")
        for chat_id in chat_ids:
            chat_id = chat_id.strip()
            if chat_id:
                try:
                    await application.bot.send_message(
                        chat_id, "Hello! This is a background message."
                    )
                except Exception as e:
                    logger.error(f"Failed to send message to {chat_id}: {e}")
        await asyncio.sleep(60)  # every 60 seconds


# --- /start command with args support ---
async def start_with_args(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command, including shared wishlist links."""
    if context.args and context.args[0].startswith("view_"):
        await view_shared_wishlist(update, context)
    else:
        await start_command(update, context)


# --- Initialize bot and handlers ---
async def main():
    global bot_app
    print("🔧 Initializing database...")
    init_db()

    print("🤖 Launching Telegram bot with webhook...")
    bot_app = Application.builder().token(BOT_TOKEN).build()

    # --- Conversation handler for adding a wish ---
    add_wish_conv = ConversationHandler(
        entry_points=[
            CommandHandler("add", add_wish_start),
            MessageHandler(filters.Regex(f"^{ADD_WISH_BUTTON}$"), add_wish_start),
        ],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, wish_title)],
            DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, wish_description)
            ],
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, wish_url)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, wish_price)],
            IMAGE: [
                MessageHandler(filters.PHOTO, wish_image),
                MessageHandler(filters.TEXT & ~filters.COMMAND, wish_image),
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex(f"^{CANCEL_BUTTON}$"), cancel_add_wish),
            CommandHandler("cancel", cancel_add_wish),
        ],
    )

    # --- Conversation handler for editing a wish ---
    edit_wish_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_wish_callback, pattern="^edit_")],
        states={
            EDIT_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_title_handler)
            ],
            EDIT_DESCRIPTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, edit_description_handler
                )
            ],
            EDIT_URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_url_handler)
            ],
            EDIT_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_price_handler)
            ],
            EDIT_IMAGE: [
                MessageHandler(filters.PHOTO, edit_image_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_image_handler),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(edit_field_choice_callback, pattern=r"^edit_field_"),
            MessageHandler(filters.Regex(f"^{CANCEL_BUTTON}$"), cancel_edit_callback),
            CommandHandler("cancel", cancel_edit_callback),
            CallbackQueryHandler(cancel_edit_callback, pattern="^cancel_edit$"),
        ],
    )

    # --- Register handlers ---
    bot_app.add_handler(CommandHandler("start", start_with_args))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("mywishlist", my_wishlist))
    bot_app.add_handler(CommandHandler("share", share_wishlist))
    bot_app.add_handler(add_wish_conv)
    bot_app.add_handler(edit_wish_conv)
    bot_app.add_handler(CallbackQueryHandler(delete_wish_callback, pattern="^delete_"))
    bot_app.add_handler(
        CallbackQueryHandler(confirm_delete_callback, pattern="^confirm_delete_")
    )
    bot_app.add_handler(
        CallbackQueryHandler(cancel_delete_callback, pattern="^cancel_delete$")
    )
    bot_app.add_handler(
        MessageHandler(filters.Regex(f"^{MY_WISHLIST_BUTTON}$"), my_wishlist)
    )
    bot_app.add_handler(
        MessageHandler(filters.Regex(f"^{SHARE_BUTTON}$"), share_wishlist)
    )
    bot_app.add_handler(
        MessageHandler(
            filters.Regex(f"^({ADD_WISH_BUTTON}|{SETTINGS_BUTTON})$"),
            handle_menu_buttons,
        )
    )

    # --- Start background task ---
    bot_app.create_task(background_task(bot_app))

    # --- Set Telegram webhook ---
    webhook_url = (
        f"https://{os.environ.get('RENDER_EXTERNAL_URL')}/telegram/{BOT_TOKEN}"
    )
    await bot_app.bot.set_webhook(webhook_url)
    print(f"Webhook set to: {webhook_url}")

    print("✅ Bot launched successfully with webhook!")


# === Run everything on Render ===
if __name__ == "__main__":
    import nest_asyncio

    nest_asyncio.apply()
    import asyncio

    asyncio.run(main())

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
