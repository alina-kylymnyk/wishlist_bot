from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_menu_keyboard
from database import get_or_create_user

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command"""
    user = update.effective_user

    # Get or create the user in the database
    db_user = get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    welcome_message = f"""
    👋 Hi, {user.first_name}!

    I'm your personal wishlist bot 🎁

    ✨ What I can do:
    - Save your wishes with descriptions, photos, and prices
    - Help you share your wishlist with friends and family
    - Edit or delete existing wishes

    Choose an action from the menu below 👇
"""
    await update.message.reply_text(
        welcome_message,
        reply_markup=main_menu_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /help command"""
    help_text = """
📖 <b>Help Menu</b>

<b>Available commands:</b>
/start - Start the bot
/help - Show this help message
/mywishlist - View your wishlist
/add - Add a new wish
/share - Get a shareable link to your wishlist

<b>How to use:</b>
1️⃣ Tap "➕ Add wish"
2️⃣ Enter your wish details
3️⃣ View your list under "📝 My wishlist"
4️⃣ Share your wishlist using "🔗 Share"

Need help? Type /help
"""

    await update.message.reply_text(
        help_text,
        parse_mode='HTML',
        reply_markup=main_menu_keyboard()
    )