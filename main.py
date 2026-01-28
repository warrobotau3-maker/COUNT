import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# --- CONFIGURATION ---
TOKEN = "8357868286:AAEdyNticdQvDY8Eqhp9bUnJalZl7nSVe_M" 

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- DATA STORAGE (In-Memory) ---
# Format: { user_id: { "name": "User Name", "word_count": 0 } }
user_data = {}

# --- FUNCTIONS ---

async def count_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Runs on every text message. 
    Calculates number of words and adds to user total.
    """
    if not update.message or not update.message.from_user or not update.message.text:
        return

    user = update.message.from_user
    user_id = user.id
    user_name = user.first_name
    
    # Calculate words in this specific message
    # .split() breaks the sentence by spaces
    text = update.message.text
    num_words = len(text.split())

    # Initialize user if not exists
    if user_id not in user_data:
        user_data[user_id] = {"name": user_name, "word_count": 0}
    
    # Add words to total
    user_data[user_id]["word_count"] += num_words
    
    # Update name in case they changed it
    user_data[user_id]["name"] = user_name

async def my_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command: /mystats
    Shows the total WORD count for the user.
    """
    user = update.message.from_user
    user_id = user.id

    if user_id in user_data:
        count = user_data[user_id]["word_count"]
        await update.message.reply_text(f"📝 {user.first_name}, you have typed **{count}** words.", parse_mode='Markdown')
    else:
        await update.message.reply_text("You haven't typed anything yet!")

async def top_yappers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command: /top
    Shows the top 5 users by word count.
    """
    if not user_data:
        await update.message.reply_text("No words tracked yet.")
        return

    # Sort users by word_count (highest first)
    sorted_users = sorted(user_data.items(), key=lambda item: item[1]['word_count'], reverse=True)
    
    # Get top 5
    top_5 = sorted_users[:5]
    
    message = "🏆 **Top Yappers (Word Count)** 🏆\n\n"
    for rank, (uid, data) in enumerate(top_5, 1):
        message += f"{rank}. {data['name']}: {data['word_count']} words\n"

    await update.message.reply_text(message, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am listening! I will count how many WORDS everyone types.\nUse /mystats to see your count or /top to see the leaderboard.")

# --- MAIN EXECUTION ---

if __name__ == '__main__':
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable not set.")
        exit(1)

    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    start_handler = CommandHandler('start', start)
    stats_handler = CommandHandler('mystats', my_stats)
    top_handler = CommandHandler('top', top_yappers)
    
    # Filters text messages only (no photos/stickers)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), count_words)

    application.add_handler(start_handler)
    application.add_handler(stats_handler)
    application.add_handler(top_handler)
    application.add_handler(message_handler)
    
    print("Bot is running...")
    application.run_polling()
