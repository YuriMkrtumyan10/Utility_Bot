import sqlite3
import datetime
import difflib
import time

DB_PATH = '/opt/Utility_Bot/utility_project.db'
RETRIES = 5
RETRY_DELAY = 5  # seconds

def get_connection():
    return sqlite3.connect(DB_PATH)

def upsert_water(item):
    for _ in range(RETRIES):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM outages_water WHERE post_id = ?", (item['post_id'],))
            exists = cursor.fetchone()

            current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if exists:
                cursor.execute("""UPDATE outages_water SET 
                                  state = ?, 
                                  city = ?, 
                                  province = ?, 
                                  streets = ?, 
                                  type = ?, 
                                  full_message = ?, 
                                  date = ? 
                                  WHERE post_id = ?""", (
                    item['state'], 
                    item['city'], 
                    item['province'], 
                    item['streets'], 
                    item['type'], 
                    item['full_message'],
                    current_timestamp,
                    item['post_id']
                ))
            else:
                cursor.execute("""INSERT INTO outages_water 
                                  (state, city, province, streets, post_id, type, full_message, date) VALUES 
                                  (?, ?, ?, ?, ?, ?, ?, ?);""", (
                    item['state'], 
                    item['city'], 
                    item['province'], 
                    item['streets'], 
                    item['post_id'], 
                    item['type'], 
                    item['full_message'],
                    current_timestamp
                ))

            conn.commit()
            conn.close()
            break
        except sqlite3.OperationalError:
            time.sleep(RETRY_DELAY)

def upsert_elect(date, time, streets, city):
    for _ in range(RETRIES):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM outages_elect WHERE date = ? AND time = ? AND streets = ?", (date, time, streets))
            existing_row = cursor.fetchone()
            
            if existing_row:
                existing_id, existing_streets, existing_time, existing_date, existing_city = existing_row
                if existing_streets != streets or existing_time != time:
                    cursor.execute("UPDATE outages_elect SET streets=?, time=?, city=? WHERE id=?", (streets, time, city, existing_id))
                    conn.commit()
            else:
                cursor.execute("INSERT INTO outages_elect (streets, time, date, city) VALUES (?, ?, ?, ?)", (streets, time, date, city))
                conn.commit()
            
            conn.close()
            break
        except sqlite3.OperationalError:
            time.sleep(RETRY_DELAY)

def upsert_gas(date, streets, city):
    for _ in range(RETRIES):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM outages_gas WHERE date = ? AND streets = ?", (date, streets))
            existing_row = cursor.fetchone()
            
            if existing_row:
                existing_id, existing_streets, existing_date, existing_city = existing_row
                if existing_streets != streets:
                    cursor.execute("UPDATE outages_gas SET streets=?, city=? WHERE id=?", (streets, city, existing_id))
                    conn.commit()
            else:
                cursor.execute("INSERT INTO outages_gas (streets, date, city) VALUES (?, ?, ?)", (streets, date, city))
                conn.commit()
            
            conn.close()
            break
        except sqlite3.OperationalError:
            time.sleep(RETRY_DELAY)

