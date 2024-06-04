import sqlite3
import datetime

conn = sqlite3.connect('utility_project.db')
cursor = conn.cursor()

def upsert(item):
    cursor.execute("SELECT 1 FROM outages WHERE post_id = ?", (item['post_id'],))
    exists = cursor.fetchone()

    current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if exists:
        cursor.execute("""UPDATE outages SET 
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
        cursor.execute("""INSERT INTO outages 
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
