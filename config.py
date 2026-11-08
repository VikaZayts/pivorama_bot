import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', 0))

# Настройки базы данных
DATABASE_PATH = 'pivorama.db'

# Настройки логирования
LOG_LEVEL = 'INFO'