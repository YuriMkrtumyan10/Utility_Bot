import sqlite3
from sqlite3 import Connection
import os

class DatabaseManager:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect('utility_project.db')

    def get_connection(self) -> Connection:
        return self._connection

    def close_connection(self):
        if self._connection:
            self._connection.close()
            self._connection = None
