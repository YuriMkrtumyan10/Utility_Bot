import re
import sqlite3
from telegram import Bot
from datetime import datetime
from dotenv import load_dotenv
from unidecode import unidecode

import os

load_dotenv()

# Initialize your bot with the token
bot = Bot(token=os.getenv('TG_TOKEN'))
conn = sqlite3.connect('utility_project.db')
cursor = conn.cursor()

def get_new_info_for_user(address):
    # Connect to your SQLite database

    # Query to find new info for the address
    cursor.execute("""
        SELECT id, info FROM new_info 
        WHERE address = ? AND id NOT IN (
            SELECT info_id FROM sent_notifications WHERE user_id = ?
        )
    """, (address,))
    
    new_info = cursor.fetchall()
    return new_info

def format_water(el):
    addresses = re.sub(r',\s*(?=[^\d\s])', ',\n   • ', el[1])
    return {
        "diff": el[1],
        "message":
                f"""Բարև Ձեզ, հարգելի օգտատեր:

        🚰«Վեոլիա Ջուր» ընկերությունը տեղեկացնում է, որ վթարային աշխատանքներով պայմանավորված կդադարեցվի հետևյալ հասցեների ջրամատակարարումը
   • {addresses}""",
        "category": 1 
    }

def format_gas(el):
    addresses = re.sub(r',\s*(?=[^\d\s])', ',\n   • ', el[1])
    return {
        "diff": el[1],
        "message":  
                f"""Բարև Ձեզ, հարգելի օգտատեր:

        🔥«Գազպրոմ Արմենիա» ՓԲԸ» ընկերությունը տեղեկացնում է, որ պլանային աշխատանքներ իրականացնելու նպատակով կդադարեցվի հետևյալ հասցեների գազամատակարարումը՝
   • {addresses}""",
        "category": 2 
    }

def format_elect(el):
    addresses = re.sub(r',\s*(?=[^\d\sև])', ',\n   • ', el[1])
    return {
        "diff": el[1],
         "message": f"""Բարև Ձեզ, հարգելի օգտատեր: 🙋🏼‍♂️

    ⚡️«Հայաստանի էլեկտրական ցանցեր» ընկերությունը տեղեկացնում է, որ ժամանակավորապես կդադարեցվի հետևյալ հասցեների էլեկտրամատակարարումը՝
   • {addresses}""",
        "category": 3
    }

def get_water_utilities(address):
    # normalized_address = unidecode(address).lower()

    cursor.execute("""
        SELECT id, streets FROM outages_water 
        WHERE streets LIKE '%' || ? || '%'  AND `date` >= date('now')
    """, (address.title(),))

    outages = cursor.fetchall()
    r = []
    for i in outages:
        r.append(format_water(i))
    return r

def get_gas_utilities(address):
    cursor.execute("""
        SELECT id, streets FROM outages_gas
        WHERE LOWER(streets) LIKE '%' || LOWER(?) || '%'  AND `date` >= date('now')
    """, (address.title(),))
    
    outages = cursor.fetchall()
    r = []
    for i in outages:
        r.append(format_gas(i))
    return r

def get_elect_utilities(address):
    cursor.execute("""
        SELECT id, streets FROM outages_elect
        WHERE LOWER(streets) LIKE '%' || LOWER(?) || '%'  AND `date` >= date('now')
    """, (address.title(),))
    
    outages = cursor.fetchall()
    r = []
    for i in outages:
        r.append(format_elect(i))
    return r

def get_utilities(address):
    utilities = []
    utilities = utilities + get_water_utilities(address)
    utilities = utilities + get_gas_utilities(address)
    utilities = utilities + get_elect_utilities(address)

    return utilities

def mark_as_sent(user_id, info, category):
    cursor.execute("""
        INSERT INTO sent_notifications (user_id, diff, sent_at, category)
        VALUES (?, ?, ?, ?)
    """, (user_id, info, datetime.now(), category))

    conn.commit()


def message_not_sended(user_id, el):
    cursor.execute("""
        SELECT EXISTS(
            SELECT 1
            FROM sent_notifications
            WHERE user_id = ? AND diff = ? AND category = ?
        )
    """, (user_id, el["diff"], el["category"]))

    result = cursor.fetchone()[0]
    return bool(result)

async def send_updates_to_users():
    cursor = conn.cursor()

    cursor.execute("SELECT `user_id`, address FROM user_addresses")
    user_addresses = cursor.fetchall()

    user_to_addresses = {}
    for user_id, address in user_addresses:
        if user_id not in user_to_addresses:
            user_to_addresses[user_id] = []
        user_to_addresses[user_id].append(address)

    notifications = {}

    for user_id, addresses in user_to_addresses.items():
        notifications[user_id] = []
        for address in addresses:
            outages = get_utilities(address)
            if (outages):
                notifications[user_id].append(outages)

    for user_id, info in notifications.items():
        for i in info:
            for j in i:
                if not(message_not_sended(user_id, j)):
                    print('sended')
                    await bot.send_message(chat_id=user_id, text=j["message"])
                mark_as_sent(user_id, j["diff"], j["category"])


if __name__ == "__main__":
    import asyncio
    asyncio.run(send_updates_to_users())
    conn.close()
