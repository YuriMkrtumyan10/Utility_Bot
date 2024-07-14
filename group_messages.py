import re
import sqlite3
from telegram import Bot
from dotenv import load_dotenv
import os
from bot.utils.translate import translate_from_armenian
from datetime import datetime
import asyncio
import logging
import time 
load_dotenv()

bot = Bot(token=os.getenv('TG_TOKEN_GROUP'))
conn = sqlite3.connect('/opt/Utility_Bot/utility_project.db')
cursor = conn.cursor()

def format_water(el):
    date = re.findall(r'\d{2}\.\d{2}\.\d{4}թ', el[1])
    full_message = el[1].split("«")[1].split("Ընկերությունը հայցում ")[0].replace("որվթարային", "որ վթարային").replace("շենքերիջրամատակարարումը", "շենքերի ջրամատակարարումը")
    return {
        "diff": el[1],
        "message":
                f"""🙋🏼‍♂️Հարգելի օգտատեր:

📅 {date[0]} 
🚰 «{full_message}""",
        "category": 1 
    }

def format_gas(el):
    addresses = el[1]
    addresses = re.sub(r"\b\w+\s+մարզի\b.*", "", addresses)
    return {
        "diff": el[1],
        "message":  
                f"""🙋🏼‍♂️Հարգելի օգտատեր:

🔥<b>«Գազպրոմ Արմենիա» ՓԲԸ» ընկերությունը տեղեկացնում է, որ պլանային աշխատանքներ իրականացնելու նպատակով կդադարեցվի հետևյալ հասցեների՝</b>
   📅{el[2]}
   🚨{addresses} 
<b>գազամատակարարումը</b>""",
        "category": 2 
    }

def format_elect(el):
    addresses = re.sub(r',\s*(?=[^\d\sև])', ',\n   📍 ', el[1])
    time = el[2]
    date = el[3]
    return {
        "diff": el[1],
         "message": f"""🙋🏼‍♂️Հարգելի օգտատեր: 

💡 <b> «Հայաստանի էլեկտրական ցանցեր» ընկերությունը տեղեկացնում է, որ ժամանակավորապես</b>
⏰ {time}
📅 {date} 
<b>կդադարեցվի հետևյալ հասցեների էլեկտրամատակարարումը՝</b>
   📍 {addresses}

  """,
        "category": 3
    }

def get_water_utilities():
    cursor.execute("""
        SELECT id, full_message FROM outages_water 
        WHERE `date` >= date('now', '+4 hours')
    """)
    outages = cursor.fetchall()
    r = []
    for i in outages:
        r.append(format_water(i))
    return r

def get_gas_utilities():
    cursor.execute("""
        SELECT id, streets, date FROM outages_gas
        WHERE `date` >= date('now', '+4 hours')
    """)
    outages = cursor.fetchall()
    r = []
    for i in outages:
        r.append(format_gas(i))
    return r

def get_elect_utilities():
    cursor.execute("""
        SELECT id, streets, date, time FROM outages_elect
        WHERE `date` >= date('now', '+4 hours')
    """)
    
    outages = cursor.fetchall()
    r = []
    for i in outages:
        r.append(format_elect(i))
    return r

def get_utilities():
    utilities = []
    utilities = utilities + get_water_utilities()
    utilities = utilities + get_gas_utilities()
    utilities = utilities + get_elect_utilities()

    return utilities

def mark_as_sent(user_id, info, category):
    cursor.execute("""
        INSERT INTO sent_notifications (user_id, diff, sent_at, category)
        VALUES (?, ?, ?, ?)
    """, (user_id, info, datetime.now(), category))

    conn.commit()


def message_not_sended(el):
    cursor.execute("""
        SELECT EXISTS(
            SELECT 1
            FROM sent_notifications
            WHERE user_id = ? AND diff = ? AND category = ?
        )
    """, ('group', el["diff"], el["category"]))

    result = cursor.fetchone()[0]
    return bool(result)

telegram_channel = '@komunal_anjatumner'

async def send_updates():
    outages = get_utilities()
    for outage in outages:
        if not(message_not_sended(outage)):
            await bot.send_message(chat_id=telegram_channel, text=(outage["message"]), parse_mode='HTML', message_thread_id=7)
            time.sleep(2)
            await bot.send_message(chat_id=telegram_channel, text=translate_from_armenian(outage["message"], "en"), parse_mode='HTML', message_thread_id=5)
            time.sleep(2)
            await bot.send_message(chat_id=telegram_channel, text=translate_from_armenian(outage["message"], "ru"), parse_mode='HTML', message_thread_id=4)
            time.sleep(2)
            mark_as_sent("group", outage["diff"], outage["category"])

def start():
    asyncio.run(send_updates())

if __name__ == '__main__':
    asyncio.run(start())
