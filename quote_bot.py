import random
import os
import pandas as pd
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import ReplyKeyboardMarkup

file_path = 'data/df_quotes.csv'
df_quotes = pd.read_csv(file_path)
favorites = {}
last_sent_quotes = {}

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        ["/stop", "/start"],
        ["/quote", "/save_favorite"],
        ["/view_favorites", "/clear_favorites"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hi! I'm a quote bot. Here are some commands you can use:",
        reply_markup=reply_markup
    )

# choosing a random string
def get_random_quote():
    random_row = df_quotes.sample(n=1).iloc[0]
    return f"\"{random_row['quote']}\" — {random_row['author']}"

# favorites
def save_favorites_to_file():
    with open("favorites.json", "w") as f:
        json.dump(favorites, f)

def load_favorites_from_file():
    global favorites
    if os.path.exists("favorites.json") and os.path.getsize("favorites.json") > 0:
        with open("favorites.json", "r") as f:
            favorites = json.load(f)
    else:
        favorites = {}

        
# /quote command handler
async def send_quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    quote = get_random_quote()

    last_sent_quotes[user_id] = quote
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=quote
    )
    
# /save_favorite command handler
async def save_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id

    if user_id in last_sent_quotes:
        quote = last_sent_quotes[user_id]
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="First, get a quote using the /quote command."
        )
        return

    if user_id not in favorites:
        favorites[user_id] = []

    favorites[user_id].append(quote)

    save_favorites_to_file()

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Congrats! Quote added to favorites:\n{quote}"
    )


# /view_favorites command handler
async def view_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id

    if user_id in favorites and favorites[user_id]:
        response = "Favorite quotes:\n\n" + "\n\n".join(favorites[user_id])
    else:
        response = "You don't have any favorite quotes yet."

    await context.bot.send_message(chat_id=chat_id, text=response)

# /clear_favorites command handler
async def clear_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id

    if user_id in favorites:
        favorites[user_id] = [] 
        save_favorites_to_file()
        response = "Your list of favorites has been cleared."
    else:
        response = "You don't have any favorite quotes to delete yet."

    await context.bot.send_message(chat_id=chat_id, text=response)
    
# /stop command handler
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    await context.bot.send_message(
        chat_id=chat_id,
        text="Goodbye! Hope to see you again soon 🤞"
    )
    
def main():
    load_favorites_from_file()

    application = Application.builder().token("TOKEN_FROM_BOTFATHER").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quote", send_quote))
    application.add_handler(CommandHandler("save_favorite", save_favorite))
    application.add_handler(CommandHandler("view_favorites", view_favorites))
    application.add_handler(CommandHandler("clear_favorites", clear_favorites))
    application.add_handler(CommandHandler("stop", stop))

    application.run_polling()


if __name__ == '__main__':
    main()