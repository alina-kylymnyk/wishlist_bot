import os
import logging
from fastapi import FastAPI
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

# --- FastAPI app for Render ---
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Bot is running!"}


# --- Background task for Telegram notifications ---
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
        await asyncio.sleep(60)  # repeat interval in seconds


# --- /start command with optional arguments ---
async def start_with_args(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0].startswith("view_"):
        await view_shared_wishlist(update, context)
    else:
        await start_command(update, context)


# === Main async function ===
async def main():
    print("🔧 Initializing database...")
    init_db()

    print("🤖 Launching Telegram bot...")
    application = Application.builder().token(BOT_TOKEN).build()

    # --- Add handlers ---

    # Conversation handler for adding a wish
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

    # Conversation handler for editing a wish
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

    # Register command handlers
    application.add_handler(CommandHandler("start", start_with_args))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("mywishlist", my_wishlist))
    application.add_handler(CommandHandler("share", share_wishlist))

    # Add conversation handlers
    application.add_handler(add_wish_conv)
    application.add_handler(edit_wish_conv)

    # Callback query handlers
    application.add_handler(
        CallbackQueryHandler(delete_wish_callback, pattern="^delete_")
    )
    application.add_handler(
        CallbackQueryHandler(confirm_delete_callback, pattern="^confirm_delete_")
    )
    application.add_handler(
        CallbackQueryHandler(cancel_delete_callback, pattern="^cancel_delete$")
    )

    # Menu buttons
    application.add_handler(
        MessageHandler(filters.Regex(f"^{MY_WISHLIST_BUTTON}$"), my_wishlist)
    )
    application.add_handler(
        MessageHandler(filters.Regex(f"^{SHARE_BUTTON}$"), share_wishlist)
    )
    application.add_handler(
        MessageHandler(
            filters.Regex(f"^({ADD_WISH_BUTTON}|{SETTINGS_BUTTON})$"),
            handle_menu_buttons,
        )
    )

    # --- Start background task correctly ---
    application.create_task(background_task(application))

    # --- Start polling ---
    print("✅ Bot launched successfully!")
    await application.run_polling()


# === Run everything on Render ===
if __name__ == "__main__":
    import nest_asyncio

    nest_asyncio.apply()  # allow nested loops in Jupyter/uvicorn/Render
    import asyncio

    # Run the async main
    asyncio.run(main())

    # Run FastAPI server on the same process (port from environment)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
