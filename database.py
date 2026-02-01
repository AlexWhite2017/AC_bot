import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name="ac_bot.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()
    
    def init_db(self):
        """Инициализация таблиц базы данных"""
        # Таблица пользователей
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица для отслеживания отправленных новостей
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id TEXT,
                user_id INTEGER,
                sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Таблица запросов подбора
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                area REAL,
                calculated_btu INTEGER,
                result_count INTEGER,
                request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        self.conn.commit()
        logger.info("Database initialized")
    
    def add_user(self, user_id, username, first_name, last_name):
        """Добавление нового пользователя"""
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_active)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, first_name, last_name, datetime.now()))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
    
    def update_user_activity(self, user_id):
        """Обновление времени последней активности"""
        try:
            self.cursor.execute("""
                UPDATE users SET last_active = ? WHERE user_id = ?
            """, (datetime.now(), user_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error updating activity: {e}")
    
    def get_all_users(self):
        """Получение всех пользователей"""
        self.cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in self.cursor.fetchall()]
    
    def log_news_sent(self, news_id, user_id):
        """Логирование отправленных новостей"""
        try:
            self.cursor.execute("""
                INSERT INTO news_log (news_id, user_id) VALUES (?, ?)
            """, (news_id, user_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error logging news: {e}")
    
    def log_calculation(self, user_id, area, calculated_btu, result_count):
        """Логирование запросов подбора"""
        try:
            self.cursor.execute("""
                INSERT INTO calculations (user_id, area, calculated_btu, result_count)
                VALUES (?, ?, ?, ?)
            """, (user_id, area, calculated_btu, result_count))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error logging calculation: {e}")
    
    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()

# Глобальный экземпляр базы данных
db = Database()
