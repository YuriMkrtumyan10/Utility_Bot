from telegram import Bot, Update, ChatMember
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv('TG_TOKEN_GROUP') 

async def is_user_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    chat_member = await bot.get_chat_member(chat_id, user_id)
    return chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
async def block_messages(update: Update, context: CallbackContext) -> None:
    thread_id = update.message.message_thread_id
    chat_id=update.effective_chat.id
    user_id = update.effective_user.id

    if await is_user_admin(context.bot, chat_id, user_id):
        return
    if thread_id != 1 and thread_id is not None:  # Convert chat_id to string for comparison
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    else:
        pass

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

def main():
    app = Application.builder().token(bot_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, block_messages))
    app.add_error_handler(error)

    app.run_polling()

if __name__ == '__main__':
    main()
