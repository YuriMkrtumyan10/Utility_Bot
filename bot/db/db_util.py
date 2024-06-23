from .database_manager import DatabaseManager

def get_cursor():
    db = DatabaseManager()
    conn = db.get_connection()
    return conn.cursor()
