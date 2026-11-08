import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_SHEETS_CREDENTIALS, GOOGLE_SHEET_ID
from datetime import datetime

def get_gsheets_client():
    """Получить клиент для работы с Google Sheets"""
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        GOOGLE_SHEETS_CREDENTIALS, scope)
    return gspread.authorize(creds)

def export_booking_to_sheet(booking_data: dict):
    """Экспорт бронирования в Google Sheets"""
    try:
        client = get_gsheets_client()
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet('Бронирования')
        
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            booking_data.get('username', ''),
            booking_data.get('filial_name', ''),
            booking_data.get('type', ''),
            booking_data.get('date', ''),
            booking_data.get('guests', ''),
            booking_data.get('details', ''),
            booking_data.get('phone', '')
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        print(f"Ошибка экспорта в Google Sheets: {e}")
        return False

def export_order_to_sheet(order_data: dict):
    """Экспорт заказа в Google Sheets"""
    try:
        client = get_gsheets_client()
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet('Заказы')
        
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            order_data.get('username', ''),
            order_data.get('filial_name', ''),
            order_data.get('items', ''),
            order_data.get('total_price', ''),
            order_data.get('phone', '')
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        print(f"Ошибка экспорта в Google Sheets: {e}")
        return False