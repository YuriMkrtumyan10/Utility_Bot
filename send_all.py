import sqlite3
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
import os
import asyncio
load_dotenv()

# The message to send
message_text = f"""📢 Ծանուցում. Միացե՛ք մեր խմբին:\n
ℹ️ Տեղեկացեք կոմունալ ծառայությունների խափանումների մասին և կապ հաստատեք ուրիշների հետ. Միացե՛ք մեր խմբին հիմա! 🚀

📲 @komunal_anjatumner"""

# Initialize the bot
bot = Bot(token=os.getenv('TG_TOKEN'))

# Connect to SQLite Database
def get_user_ids():
    connection = sqlite3.connect('/opt/Utility_Bot/utility_project.db')  # Update with your database file path
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users")  # Assuming your table and column names. Adjust as necessary.
    user_ids = [row[0] for row in cursor.fetchall()]
    connection.close()
    return user_ids

# Function to send messages to all users
async def send_broadcast_message(user_ids, message):
    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=message)
            print(f"Message sent to {user_id}")
        except TelegramError as e:
            print(f"Failed to send message to {user_id}: {e}")

# Main function to orchestrate the broadcast
async def main():
    user_ids = get_user_ids()
    if user_ids:
        await send_broadcast_message(user_ids, message_text)
    else:
        print("No users found in the database.")

# Execute the program
if __name__ == "__main__":
    asyncio.run(main())
