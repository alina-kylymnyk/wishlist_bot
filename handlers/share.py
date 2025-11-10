from telegram import Update
from telegram.ext import ContextTypes
import hashlib
from database import get_user, get_user_wishes
from handlers.wishlist import send_wish_detail
from keyboards import main_menu_keyboard


def generate_share_code(user_id: int) -> str:
    """Generate a unique share code based on user_id"""
    hash_object = hashlib.md5(str(user_id).encode())
    return hash_object.hexdigest()[:8]


async def share_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Share your wishlist via a link"""
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ Error: user not found")
        return
    
    wishes = get_user_wishes(user_id)
    
    if not wishes:
        await update.message.reply_text(
            "📝 <b>Your wishlist is empty</b>\n\n"
            "Add some wishes first before sharing!",
            parse_mode='HTML',
            reply_markup=main_menu_keyboard()
        )
        return
    
    # Generate a unique share code
    share_code = generate_share_code(user_id)
    
    # Get bot username
    bot_username = (await context.bot.get_me()).username
    
    # Build the share link
    share_link = f"https://t.me/{bot_username}?start=view_{share_code}"
    
    message = (
        f"🔗 <b>Your wishlist link</b>\n\n"
        f"Share this link with friends and family so they can see "
        f"what gifts you’d love to receive!\n\n"
        f"📋 Total wishes: {len(wishes)}\n\n"
        f"<code>{share_link}</code>\n\n"
        f"Just copy and send this link!"
    )
    
    await update.message.reply_text(
        message,
        parse_mode='HTML',
        reply_markup=main_menu_keyboard()
    )


async def view_shared_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View someone else's wishlist via shared link"""
    # Extract argument after /start
    if not context.args or not context.args[0].startswith('view_'):
        return
    
    share_code = context.args[0].replace('view_', '')
    
    from database import get_db
    from models import User
    
    db = get_db()
    try:
        users = db.query(User).all()
        target_user = None
        
        # Match share_code to user
        for user in users:
            if generate_share_code(user.user_id) == share_code:
                target_user = user
                break
        
        if not target_user:
            await update.message.reply_text(
                "❌ Wishlist not found or link expired"
            )
            return
        
        # Check if the wishlist is public
        if not target_user.is_public:
            await update.message.reply_text(
                "🔒 This wishlist is private"
            )
            return
        
        # Get wishes
        wishes = get_user_wishes(target_user.user_id)
        
        if not wishes:
            await update.message.reply_text(
                f"📝 {target_user.first_name}'s wishlist is empty"
            )
            return
        
        # Show the wishlist
        viewer_name = update.effective_user.first_name
        
        await update.message.reply_text(
            f"👋 Hi, {viewer_name}!\n\n"
            f"🎁 <b>{target_user.first_name}'s wishlist</b>\n"
            f"📋 Total wishes: {len(wishes)}\n\n"
            f"Here’s what they’d like to receive:",
            parse_mode='HTML'
        )
        
        # Send each wish (without edit/delete buttons)
        for wish in wishes:
            await send_wish_detail(update, wish, show_actions=False)
        
        await update.message.reply_text(
            "💡 <b>Tip:</b> Save or note down what you plan to gift!",
            parse_mode='HTML'
        )
    
    finally:
        db.close()
