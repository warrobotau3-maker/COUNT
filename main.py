import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- CONFIGURATION ---
# Replace 'YOUR_TOKEN_HERE' with your actual token if running locally, 
# but on Railway, we will use an Environment Variable.
import os
TOKEN = "8357868286:AAEdyNticdQvDY8Eqhp9bUnJalZl7nSVe_M" 

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- DATA STORAGE (In-Memory) ---
# Format: { user_id: { "name": "User Name", "count": 0 } }
user_counts = {}

# --- FUNCTIONS ---

async def count_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This function runs every time a text message is sent in the group.
    It increments the counter for that specific user.
    """
    if not update.message or not update.message.from_user:
        return

    user = update.message.from_user
    user_id = user.id
    user_name = user.first_name

    # Initialize user if not exists
    if user_id not in user_counts:
        user_counts[user_id] = {"name": user_name, "count": 0}
    
    # Increment count
    user_counts[user_id]["count"] += 1
    
    # Update name in case they changed it
    user_counts[user_id]["name"] = user_name

async def my_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command: /mystats
    Shows the message count for the user who sent the command.
    """
    user = update.message.from_user
    user_id = user.id

    if user_id in user_counts:
        count = user_counts[user_id]["count"]
        await update.message.reply_text(f"📊 {user.first_name}, you have sent **{count}** messages.", parse_mode='Markdown')
    else:
        await update.message.reply_text("You haven't sent any messages since I woke up!")

async def top_spammers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command: /top
    Shows the top 5 most active users in the chat.
    """
    if not user_counts:
        await update.message.reply_text("No messages tracked yet.")
        return

    # Sort users by count (highest first)
    sorted_users = sorted(user_counts.items(), key=lambda item: item[1]['count'], reverse=True)
    
    # Get top 5
    top_5 = sorted_users[:5]
    
    message = "🏆 **Top Chatters** 🏆\n\n"
    for rank, (uid, data) in enumerate(top_5, 1):
        message += f"{rank}. {data['name']}: {data['count']} msgs\n"

    await update.message.reply_text(message, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am listening! I will count how many messages everyone sends.\nUse /mystats to see your count or /top to see the leaderboard.")

# --- MAIN EXECUTION ---

if __name__ == '__main__':
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable not set.")
        exit(1)

    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    start_handler = CommandHandler('start', start)
    stats_handler = CommandHandler('mystats', my_stats)
    top_handler = CommandHandler('top', top_spammers)
    
    # This handler captures text messages to count them (filters out commands)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), count_messages)

    application.add_handler(start_handler)
    application.add_handler(stats_handler)
    application.add_handler(top_handler)
    application.add_handler(message_handler)
    
    print("Bot is running...")
    application.run_polling()
