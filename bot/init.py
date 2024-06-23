from bot.db.database_manager import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, firstname TEXT, username TEXT, language_code TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS user_addresses (id INTEGER PRIMARY KEY, address TEXT, address_number INT, user_id INT)')
conn.commit()
