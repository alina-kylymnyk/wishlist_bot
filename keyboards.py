from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton

# ===== BUTTON TEXT CONSTANTS =====
MY_WISHLIST_BUTTON = "⭐️ My wishlist"
ADD_WISH_BUTTON = "➕ Add a wish"
SHARE_BUTTON = "🔗 Share"
SETTINGS_BUTTON = "⚙️ Settings"

CANCEL_BUTTON = "❌ Cancel"
SKIP_BUTTON = "⏭ Skip"

EDIT_BUTTON = "✏️ Edit"
DELETE_BUTTON = "🗑 Delete"
CONFIRM_DELETE_BUTTON = "✅ Yes, delete"

# ===== REPLY KEYBOARDS =====
def main_menu_keyboard():
    """Main menu keyboard"""
    keyboard = [
        [KeyboardButton(MY_WISHLIST_BUTTON), KeyboardButton(ADD_WISH_BUTTON)],
        [KeyboardButton(SHARE_BUTTON), KeyboardButton(SETTINGS_BUTTON)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def cancel_keyboard():
    """Keyboard with cancel button"""
    keyboard = [[KeyboardButton(CANCEL_BUTTON)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def skip_keyboard():
    """Keyboard with skip and cancel buttons"""
    keyboard = [
        [KeyboardButton(SKIP_BUTTON)],
        [KeyboardButton(CANCEL_BUTTON)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ===== INLINE KEYBOARDS =====
def wish_actions_keyboard(wish_id: int):
    """Inline keyboard for wish actions (edit/delete)"""
    keyboard = [
        [
            InlineKeyboardButton(EDIT_BUTTON, callback_data=f"edit_{wish_id}"),
            InlineKeyboardButton(DELETE_BUTTON, callback_data=f"delete_{wish_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirm_delete_keyboard(wish_id: int):
    """Inline keyboard for delete confirmation"""
    keyboard = [
        [
            InlineKeyboardButton(CONFIRM_DELETE_BUTTON, callback_data=f"confirm_delete_{wish_id}"),
            InlineKeyboardButton(CANCEL_BUTTON, callback_data="cancel_delete")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
