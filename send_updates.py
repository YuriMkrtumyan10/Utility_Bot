import re
import sqlite3
from telegram import Bot
from datetime import datetime
from dotenv import load_dotenv
import asyncio
import os
from bot.utils.utils import get_districts
from bot.utils.translate import translate_from_armenian
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

💡 <b>«Հայաստանի էլեկտրական ցանցեր» ընկերությունը տեղեկացնում է, որ ժամանակավորապես</b>
⏰ {time}
📅 {date} 
<b>կդադարեցվի հետևյալ հասցեների էլեկտրամատակարարումը՝</b>
   📍 {addresses}

  """,
        "category": 3
    }

def get_water_utilities(address):
    # normalized_address = unidecode(address).lower()

    cursor.execute("""
        SELECT id, full_message FROM outages_water 
        WHERE streets LIKE '%' || ? || '%'
    """, (address['address'],))
    #  AND `date` >= date('now', '+4 hours')
    outages = cursor.fetchall()
    print(outages)
    r = []
    for i in outages:
        r.append(format_water(i))
    return r

def get_gas_utilities(address):
    cursor.execute("""
        SELECT id, streets FROM outages_gas
        WHERE LOWER(streets) LIKE '%' || LOWER(?) || '%' AND `date` >= date('now', '+4 hours')

    """,
    (address['province'],))
    outages = cursor.fetchall()
    r = []
    for i in outages:
        r.append(format_gas(i))
    return r

def get_elect_utilities(address):
    print(address)
    cursor.execute("""
        SELECT id, streets, date, time FROM outages_elect
        WHERE LOWER(streets) LIKE '%' || LOWER(?) || '%'  AND `date` >= date('now', '+4 hours')
    """, (address['address'],))
    
    outages = cursor.fetchall()
    print(outages)
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
    cursor.execute("SELECT user_id, address_hy, province, language_code FROM user_addresses LEFT JOIN users ON user_addresses.user_id = users.id")

    user_addresses = cursor.fetchall()

    user_to_addresses = {}
    for user_id, address, province, language_code in user_addresses:
        if user_id not in user_to_addresses:
            user_to_addresses[user_id] = []
        tmp = {}
        tmp['address'] = address.replace('.', '').replace('։', '')
        tmp['province'] = get_districts("hy")[province]
        tmp['language_code'] = language_code
        user_to_addresses[user_id].append(tmp)

    notifications = {}
    for user_id, addresses in user_to_addresses.items():
        notifications[user_id] = []
        for address in addresses:
            outages = get_utilities(address)
            if (outages):
                # notifications[user_id].append(outages)
                for outage in outages:
                    if not(message_not_sended(user_id, outage)):
                        print('sended')
                        await bot.send_message(chat_id=user_id, text=translate_from_armenian(outage["message"], address['language_code']), parse_mode='HTML')
                    mark_as_sent(user_id, outage["diff"], outage["category"])


    # for user_id, info in notifications.items():
       
def start():
    asyncio.run(send_updates_to_users())
    conn.close()

if __name__ == '__main__':
    start()
