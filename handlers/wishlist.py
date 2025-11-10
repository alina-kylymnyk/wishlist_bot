from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from keyboards import (
    main_menu_keyboard,
    skip_keyboard,
    cancel_keyboard,
    wish_actions_keyboard,
    confirm_delete_keyboard,
    MY_WISHLIST_BUTTON,
    ADD_WISH_BUTTON,
    SHARE_BUTTON,
    SETTINGS_BUTTON,
    CANCEL_BUTTON,
    SKIP_BUTTON,
    EDIT_BUTTON,
    DELETE_BUTTON,
    CONFIRM_DELETE_BUTTON,
)
from database import add_wish, get_user_wishes, get_wish, delete_wish, update_wish


# States for ConversationHandler (adding a wish)
TITLE, DESCRIPTION, URL, PRICE, IMAGE = range(5)

# States for editing
EDIT_CHOICE, EDIT_TITLE, EDIT_DESCRIPTION, EDIT_URL, EDIT_PRICE, EDIT_IMAGE = range(
    6, 12
)

# ===== ADD A WISH =====


async def add_wish_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start the process of adding a new wish.
    Sends the first message asking for the wish title.
    """
    await update.message.reply_text(
        "➕ <b>Adding a new wish</b>\n\n"
        "📝 Step 1 of 5: <b>Title</b>\n"
        "Write what you want (e.g., 'Hot Wheels car' or 'Harry Potter Book')",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    return TITLE


async def wish_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receive the wish title from the user.
    """
    if update.message.text == CANCEL_BUTTON:
        return await cancel_add_wish(update, context)  # Handle cancellation

    # Save the title in the context to use later
    context.user_data["wish_title"] = update.message.text

    await update.message.reply_text(
        "💭 <b>Step 2 of 5: Description</b>\n"
        "Add a description or details about the wish.\n\n"
        "Example: 'Color: blue, 128 GB' or 'Illustrated edition'\n\n"
        "Or press <b>⏭ Skip</b> if no description is needed",
        parse_mode="HTML",
        reply_markup=skip_keyboard(),
    )
    return DESCRIPTION


async def wish_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receive the description of the wish.
    """
    if update.message.text == CANCEL_BUTTON:
        return await cancel_add_wish(update, context)

    if update.message.text.strip() == SKIP_BUTTON:
        context.user_data["wish_description"] = None
    else:
        context.user_data["wish_description"] = update.message.text

    await update.message.reply_text(
        "🔗 <b>Step 3 of 5: URL</b>\n"
        "Send a link to the product or website (e.g., https://example.com/...)\n\n"
        "Or press <b>⏭ Skip</b>",
        parse_mode="HTML",
        reply_markup=skip_keyboard(),
    )
    return URL


async def wish_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receive the URL of the wish.
    """
    if update.message.text == CANCEL_BUTTON:
        return await cancel_add_wish(update, context)

    if update.message.text.strip() == SKIP_BUTTON:
        context.user_data["wish_url"] = None
    else:
        context.user_data["wish_url"] = update.message.text

    await update.message.reply_text(
        "💰 <b>Step 4 of 5: Price</b>\n"
        "Enter a price (for example: '3500 UAH', '$100', '50 EUR')\n\n"
        "Or click <b>⏭ Skip</b>",
        parse_mode="HTML",
        reply_markup=skip_keyboard(),
    )
    return PRICE


async def wish_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receive the price of the wish.
    """
    if update.message.text == CANCEL_BUTTON:
        return await cancel_add_wish(update, context)

    if update.message.text.strip() == SKIP_BUTTON:
        context.user_data["wish_price"] = None
    else:
        context.user_data["wish_price"] = update.message.text

    await update.message.reply_text(
        "📸 <b>Step 5 of 5: Photo</b>\n"
        "Send a photo of your product or wish\n\n"
        "Or click <b>⏭ Skip</b>",
        parse_mode="HTML",
        reply_markup=skip_keyboard(),
    )
    return IMAGE


async def wish_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive a photo and save the wish"""

    if update.message.text == CANCEL_BUTTON:
        return await cancel_add_wish(update, context)

    if update.message.photo:
        # Get the largest version of the photo (the last in the list)
        photo = update.message.photo[-1]
        context.user_data["wish_image"] = photo.file_id

    elif update.message.text == SKIP_BUTTON:
        context.user_data["wish_image"] = None

    else:
        await update.message.reply_text(
            "❌ Please send a photo or press <b>⏭ Skip</b>", parse_mode="HTML"
        )
        return IMAGE

    # Save the wish to db
    user_id = update.effective_user.id
    wish = add_wish(
        user_id=user_id,
        title=context.user_data["wish_title"],
        description=context.user_data.get("wish_description"),
        url=context.user_data.get("wish_url"),
        price=context.user_data.get("wish_price"),
        image_file_id=context.user_data.get("wish_image"),
    )

    success_message = f"✅ <b>Wish added!</b>\n\n"
    success_message += f"📦 <b>{wish.title}</b>\n"

    if wish.description:
        success_message += f"💭 {wish.description}\n"
    if wish.price:
        success_message += f"💰 {wish.price}\n"
    if wish.url:
        success_message += f"🔗 {wish.url}\n"

    # Sending confirmation
    if wish.image_file_id:
        await update.message.reply_photo(
            photo=wish.image_file_id,
            caption=success_message,
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await update.message.reply_text(
            success_message, parse_mode="HTML", reply_markup=main_menu_keyboard()
        )

    context.user_data.clear()

    return ConversationHandler.END


async def cancel_add_wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancel the wish adding process.
    Clears temporary data and shows main menu.
    """
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Wish adding canceled", reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END


# ===== VIEW WISH LIST =====


async def my_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show my whishlist"""
    user_id = update.effective_user.id
    wishes = get_user_wishes(user_id)

    if not wishes:
        await update.message.reply_text(
            "📝 <b>Your wishlist is empty</b>\n\n"
            "Add your first wish by clicking <b>➕ Add wish</b>",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
        return

    await update.message.reply_text(
        f"📝 <b>Your wishlist</b>\n"
        f"Total wishes: {len(wishes)}\n\n"
        f"Here are your wishes:",
        parse_mode="HTML",
    )

    for wish in wishes:
        await send_wish_detail(update, wish, show_actions=True)


async def send_wish_detail(update: Update, wish, show_actions: bool = False):
    """Send details of one wish"""
    message = f"📦 <b>{wish.title}</b>\n"
    message += f"🆔 ID: {wish.wish_id}\n\n"

    if wish.description:
        message += f"💭 {wish.description}\n"
    if wish.price:
        message += f"💰 {wish.price}\n"
    if wish.url:
        message += f"🔗 {wish.url}\n"

    message += f"\n📅 Added: {wish.created_at.strftime('%d.%m.%Y %H:%M')}"

    keyboard = wish_actions_keyboard(wish.wish_id) if show_actions else None

    if wish.image_file_id:
        await update.message.reply_photo(
            photo=wish.image_file_id,
            caption=message,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(
            message, parse_mode="HTML", reply_markup=keyboard
        )


# ===== DELETE THE WISH =====


async def delete_wish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handling the delete button"""
    query = update.callback_query
    await query.answer()

    wish_id = int(query.data.split("_")[1])
    wish = get_wish(wish_id)

    if not wish:
        if query.message.photo:
            await query.edit_message_caption(
                caption="❌ Wish not found", parse_mode="HTML"
            )
        else:
            await query.edit_message_text(text="❌ Wish not found", parse_mode="HTML")
        return

    # Check if the wish belongs to the current user
    if wish.user_id != update.effective_user.id:
        await query.answer("❌ This is not your wish!", show_alert=True)
        return

    # Show confirmation
    confirm_message = f"❓ Are you sure you want to delete?\n\n📦 <b>{wish.title}</b>"

    if query.message.photo:
        await query.edit_message_caption(
            caption=confirm_message,
            parse_mode="HTML",
            reply_markup=confirm_delete_keyboard(wish_id),
        )
    else:
        await query.edit_message_text(
            text=confirm_message,
            parse_mode="HTML",
            reply_markup=confirm_delete_keyboard(wish_id),
        )


async def confirm_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm deletion of a wish"""
    query = update.callback_query
    await query.answer()

    wish_id = int(query.data.split("_")[2])
    user_id = update.effective_user.id

    success_message = "✅ Wish deleted"
    fail_message = "❌ Failed to delete wish"

    message = query.message

    if delete_wish(wish_id, user_id):
        text = success_message
    else:
        text = fail_message

    if message.caption:
        await query.edit_message_caption(caption=text, parse_mode="HTML")
    else:
        await query.edit_message_text(text=text, parse_mode="HTML")


async def cancel_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel deletion of a wish"""
    query = update.callback_query
    await query.answer("Delete canceled")

    message = query.message
    text_source = message.caption if message.caption else message.text

    wish_id = text_source.split("ID: ")[1].split("\n")[0]

    await query.edit_message_reply_markup(
        reply_markup=wish_actions_keyboard(int(wish_id))
    )


# ===== MAIN MENU BUTTON HANDLING =====


async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle clicks on main menu buttons"""
    text = update.message.text

    if text == MY_WISHLIST_BUTTON:
        await my_wishlist(update, context)

    elif text == ADD_WISH_BUTTON:
        return await add_wish_start(update, context)

    elif text == SHARE_BUTTON:
        await update.message.reply_text(
            "🔗 Feature in development...\n"
            "Soon you will be able to share your wishlist!",
            reply_markup=main_menu_keyboard(),
        )

    elif text == SETTINGS_BUTTON:
        await update.message.reply_text(
            "⚙️ Feature in development...\n" "Settings will be available soon!",
            reply_markup=main_menu_keyboard(),
        )


# ===== EDIT WISH =====


async def edit_wish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pressing the edit button"""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("edit_field_"):
        return

    wish_id = int(query.data.split("_")[1])
    wish = get_wish(wish_id)

    if not wish:
        await query.edit_message_caption(caption="❌ Wish not found", parse_mode="HTML")
        return

    # Check if the wish belongs to the user
    if wish.user_id != update.effective_user.id:
        await query.answer("❌ This is not your wish!", show_alert=True)
        return

    # Save the wish ID for editing
    context.user_data["editing_wish_id"] = wish_id

    # Inline keyboard for editing options
    keyboard = [
        [
            InlineKeyboardButton(
                "✏️ Title", callback_data=f"edit_field_title_{wish_id}"
            ),
            InlineKeyboardButton(
                "💭 Description", callback_data=f"edit_field_desc_{wish_id}"
            ),
        ],
        [
            InlineKeyboardButton("🔗 URL", callback_data=f"edit_field_url_{wish_id}"),
            InlineKeyboardButton(
                "💰 Price", callback_data=f"edit_field_price_{wish_id}"
            ),
        ],
        [InlineKeyboardButton("📸 Photo", callback_data=f"edit_field_photo_{wish_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")],
    ]

    edit_menu = (
        f"✏️ <b>Edit Wish</b>\n\n"
        f"📦 <b>{wish.title}</b>\n\n"
        f"Choose what you want to edit:"
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Use caption if message has a photo, otherwise text
    if query.message.photo:
        await query.edit_message_caption(
            caption=edit_menu, parse_mode="HTML", reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(
            text=edit_menu, parse_mode="HTML", reply_markup=reply_markup
        )


async def edit_field_choice_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Handle which field was chosen from inline buttons"""
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")  # e.g., edit_field_title_42
    field = data[2]
    wish_id = int(data[3])

    context.user_data["editing_wish_id"] = wish_id

    wish = get_wish(wish_id)
    if not wish:
        await query.edit_message_text("❌ Wish not found")
        return ConversationHandler.END

    if field == "title":
        await query.message.reply_text(
            f"✏️ <b>Edit Title</b>\nCurrent title: <code>{wish.title}</code>\n\nWrite a new title:",
            parse_mode="HTML",
            reply_markup=cancel_keyboard(),
        )
        return EDIT_TITLE

    elif field == "desc":
        await query.message.reply_text(
            f"💭 <b>Edit Description</b>\nCurrent description: <code>{wish.description or 'none'}</code>\n\nWrite a new one:",
            parse_mode="HTML",
            reply_markup=cancel_keyboard(),
        )
        return EDIT_DESCRIPTION

    elif field == "url":
        await query.message.reply_text(
            f"🔗 <b>Edit URL</b>\nCurrent URL: <code>{wish.url or 'none'}</code>\n\nSend a new one:",
            parse_mode="HTML",
            reply_markup=cancel_keyboard(),
        )
        return EDIT_URL

    elif field == "price":
        await query.message.reply_text(
            f"💰 <b>Edit Price</b>\nCurrent price: <code>{wish.price or 'none'}</code>\n\nWrite a new one:",
            parse_mode="HTML",
            reply_markup=cancel_keyboard(),
        )
        return EDIT_PRICE

    elif field == "photo":
        await query.message.reply_text(
            f"📸 <b>Edit Photo</b>\nSend a new photo:",
            parse_mode="HTML",
            reply_markup=cancel_keyboard(),
        )
        return EDIT_IMAGE


async def cancel_edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel editing via button"""
    query = update.callback_query
    await query.answer("Editing canceled")
    context.user_data.clear()

    await query.edit_message_text(
        "❌ Editing canceled", reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END
