# Wishlist Telegram Bot

A Telegram bot that helps you create, manage, and share your wishlist with friends and family. Perfect for birthdays, holidays, or any special occasion!

## Features

- **Add Wishes**: Create detailed wish items with:
  - Title (required)
  - Description (optional)
  - Product URL (optional)
  - Price (optional)
  - Photo (optional)

- **Manage Wishlist**: View, edit, and delete your wishes
- **Share Wishlist**: Generate shareable links to let others see what you want
- **User-Friendly Interface**: Interactive keyboard menu and inline buttons
- **Privacy Control**: Toggle between public and private wishlists

## Technologies Used

- **Python 3.x**
- **python-telegram-bot 20.7** - Telegram Bot API wrapper
- **SQLAlchemy 2.0.23** - Database ORM
- **SQLite** - Default database (configurable)
- **python-dotenv** - Environment variable management

## Project Structure

```
wishlist_telegram_bot/
├── bot.py                  # Main bot application and conversation handlers
├── config.py              # Configuration and environment variables
├── database.py            # Database operations and queries
├── models.py              # SQLAlchemy database models (User, Wish)
├── keyboards.py           # Telegram keyboard layouts
├── handlers/
│   ├── __init__.py
│   ├── start.py           # /start and /help command handlers
│   ├── wishlist.py        # Wishlist management handlers
│   └── share.py           # Wishlist sharing functionality
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in repo)
└── wishlist.db           # SQLite database (auto-generated)
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd wishlist_telegram_bot
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   DATABASE_URL=sqlite:///wishlist.db
   ```

   To get a bot token:
   - Talk to [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` command
   - Follow the instructions to create your bot
   - Copy the token provided

5. **Run the bot**
   ```bash
   python bot.py
   ```

## Usage

### Available Commands

- `/start` - Start the bot and see the main menu
- `/help` - Display help information
- `/mywishlist` - View your wishlist
- `/add` - Add a new wish
- `/share` - Get a shareable link to your wishlist

### Menu Buttons

- **📝 My wishlist** - View all your saved wishes
- **➕ Add wish** - Start adding a new wish
- **🔗 Share** - Generate a shareable link
- **⚙️ Settings** - Manage bot settings (in development)

### Adding a Wish

1. Click "➕ Add wish" or send `/add`
2. Follow the step-by-step process:
   - **Step 1**: Enter wish title
   - **Step 2**: Add description (or skip)
   - **Step 3**: Add product URL (or skip)
   - **Step 4**: Enter price (or skip)
   - **Step 5**: Send photo (or skip)
3. Your wish is saved!

### Managing Wishes

When viewing your wishlist, each wish has action buttons:
- **✏️ Edit** - Modify wish details
- **🗑 Delete** - Remove wish from list

### Sharing Your Wishlist

1. Click "🔗 Share" or send `/share`
2. Copy the generated link
3. Share it with friends and family
4. They can view your wishlist by clicking the link

**Note**: Your wishlist must be set to public for others to view it.

## Database Schema

### Users Table
- `user_id` (Primary Key) - Telegram user ID
- `username` - Telegram username
- `first_name` - User's first name
- `is_public` - Wishlist visibility (default: True)
- `created_at` - Account creation timestamp

### Wishes Table
- `wish_id` (Primary Key) - Auto-incremented ID
- `user_id` (Foreign Key) - Reference to user
- `title` - Wish title (required)
- `description` - Detailed description
- `url` - Product link
- `price` - Price as text (flexible format)
- `image_file_id` - Telegram file ID for photo
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## Configuration

Edit `config.py` to customize:

```python
BOT_TOKEN = os.getenv('BOT_TOKEN')           # Your bot token
DATABASE_URL = os.getenv('DATABASE_URL')     # Database connection string
DB_ECHO = False                              # SQLAlchemy logging
```

### Using PostgreSQL (Optional)

To use PostgreSQL instead of SQLite:

1. Install psycopg2:
   ```bash
   pip install psycopg2-binary
   ```

2. Update `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/wishlist_db
   ```

## Development

### Adding New Features

The bot uses the `python-telegram-bot` library with ConversationHandlers for multi-step interactions:

- **Handlers** are organized in the `handlers/` directory
- **Keyboards** are defined in `keyboards.py`
- **Database operations** are in `database.py`
- **Models** are defined in `models.py`

### Current Conversation States

**Add Wish Flow**: TITLE → DESCRIPTION → URL → PRICE → IMAGE

**Edit Wish Flow**: EDIT_CHOICE → EDIT_TITLE/EDIT_DESCRIPTION/EDIT_URL/EDIT_PRICE/EDIT_IMAGE

## Troubleshooting

**Bot doesn't start**
- Check that `BOT_TOKEN` is set correctly in `.env`
- Ensure all dependencies are installed
- Verify Python version is 3.x

**Database errors**
- Delete `wishlist.db` and restart (will reset all data)
- Check `DATABASE_URL` in `.env`

**Bot doesn't respond**
- Ensure the bot is running (`python bot.py`)
- Check bot permissions with BotFather
- Review logs for error messages

## Future Enhancements

- [ ] Settings menu functionality
- [ ] Wish categories and filtering
- [ ] Notifications when someone views your wishlist
- [ ] Multi-language support
- [ ] Export wishlist to PDF
- [ ] Reserve wishes (mark as "bought" for gift-givers)
- [ ] Search functionality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Contact

For questions or suggestions, please open an issue on GitHub.

---

Made with ❤️ using Python and python-telegram-bot
