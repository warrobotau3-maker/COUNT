import logging
import os
import re
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
user_data = {}

# --- FUNCTIONS ---

async def count_letters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Counts actual letters/characters, excluding spaces.
    Example: 'Hi You' = 5 letters.
    """
    if not update.message or not update.message.from_user or not update.message.text:
        return

    user = update.message.from_user
    user_id = user.id
    user_name = user.first_name
    
    # 1. Get raw text
    text = update.message.text
    
    # 2. Remove spaces and punctuation to count only letters/numbers
    # This regex [^\w] removes anything that isn't a letter or number
    clean_text = re.sub(r'\s+', '', text) 
    letter_count = len(clean_text)

    # 3. Save to memory
    if user_id not in user_data:
        user_data[user_id] = {"name": user_name, "total_letters": 0}
    
    user_data[user_id]["total_letters"] += letter_count
    
    print(f"User {user_name} sent {letter_count} letters. Total: {user_data[user_id]['total_letters']}")

async def my_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_data:
        count = user_data[user_id]["total_letters"]
        await update.message.reply_text(f"🔤 You have typed **{count} letters** total.", parse_mode='Markdown')
    else:
        await update.message.reply_text("I haven't seen you type any letters yet!")

async def top_letters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not user_data:
        await update.message.reply_text("No data yet.")
        return

    # Sort by letter count
    sorted_users = sorted(user_data.items(), key=lambda item: item[1]['total_letters'], reverse=True)
    
    message = "🏆 **Letter Count Leaderboard** 🏆\n\n"
    for rank, (uid, data) in enumerate(sorted_users[:5], 1):
        message += f"{rank}. {data['name']}: {data['total_letters']} letters\n"

    await update.message.reply_text(message, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot active! I am now counting **LETTERS** (excluding spaces).")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('mystats', my_stats))
    application.add_handler(CommandHandler('top', top_letters))
    
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), count_letters))
    
    application.run_polling()
