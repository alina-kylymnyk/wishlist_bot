import logging
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


async def start_with_args(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start with arguments (for viewing shared wishlists)"""
    if context.args and context.args[0].startswith("view_"):
        await view_shared_wishlist(update, context)
    else:
        await start_command(update, context)


def main():
    """Main function to launch the bot"""

    print("🔧 Database initialization...")
    init_db()

    print("🤖 Launching bot...")
    application = Application.builder().token(BOT_TOKEN).build()

    # === Conversation Handler for adding a wish ===
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

    # === Conversation Handler for editing a wish ===
    edit_wish_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_wish_callback, pattern="^edit_")],
        states={
            EDIT_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_title_handler)
            ],
            EDIT_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_description_handler)
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

    # === Register command handlers ===
    application.add_handler(CommandHandler("start", start_with_args))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("mywishlist", my_wishlist))
    application.add_handler(CommandHandler("share", share_wishlist))

    # === Add ConversationHandlers ===
    application.add_handler(add_wish_conv)
    application.add_handler(edit_wish_conv)

    # === CallbackQueryHandlers ===
    application.add_handler(
        CallbackQueryHandler(delete_wish_callback, pattern="^delete_")
    )
    application.add_handler(
        CallbackQueryHandler(confirm_delete_callback, pattern="^confirm_delete_")
    )
    application.add_handler(
        CallbackQueryHandler(cancel_delete_callback, pattern="^cancel_delete$")
    )

    # === Menu Buttons ===
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

    # === Launch the bot ===
    print("✅ Bot launched successfully!")
    print("Press Ctrl+C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
