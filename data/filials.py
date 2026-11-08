"""Информация о филиалах сети Пиворама"""

FILIALS = {
    "nevskiy": {
        "name": "Пиворама на пл. Александра Невского",
        "address": "Пл. Александра Невского 2, отель «Москва», 2 этаж",
        "phone": "+7 921-945-10-52",
        "work_hours": {
            "вс": "12:00-23:00",
            "пн-чт": "12:00-23:00",
            "пт-сб": "12:00-24:00"
        },
        "halls": {
            "big": {"name": "Большой зал", "capacity": 110},
            "vip": {"name": "VIP зал", "capacity": 10}
        },
        "banquet_menus": [
            {"price": 3500, "description": "Базовое меню"},
            {"price": 4500, "description": "Расширенное меню"},
            {"price": 5500, "description": "Премиум меню"}
        ],
        "has_delivery": False
    },
    "kolpino": {
        "name": "Пиворама в Колпино",
        "address": "Колпино, Октябрьская 10, ТРК «Ока», 2 этаж",
        "phone": "905-88-34",
        "work_hours": {
            "вс-чт": "12:00-23:00",
            "пт-сб": "12:00-24:00"
        },
        "halls": {
            "floor1": {"name": "Зал 1 этаж", "capacity": 70},
            "big": {"name": "Большой зал 2 этаж", "capacity": 120},
            "vip": {"name": "VIP зал", "capacity": 30}
        },
        "banquet_menus": [
            {"price": 3800, "description": "Базовое меню"},
            {"price": 4900, "description": "Расширенное меню"}
        ],
        "has_delivery": True
    },
    "komendant": {
        "name": "Пиворама на Комендантской площади",
        "address": "Комендантская площадь 1, ТРК «Атмосфера», 5 этаж",
        "phone": "965-92-22",
        "work_hours": {
            "вс-чт": "12:00-23:00",
            "пт-сб": "12:00-24:00"
        },
        "halls": {
            "big": {"name": "Большой зал 1 этаж", "capacity": 100},
            "small": {"name": "Малый зал", "capacity": 12},
            "floor2": {"name": "Общий зал 2 этаж", "capacity": 80}
        },
        "banquet_menus": [
            {"price": 3500, "description": "Базовое меню"},
            {"price": 4500, "description": "Расширенное меню"},
            {"price": 5500, "description": "Премиум меню"}
        ],
        "has_delivery": False
    },
    "bely_kuna": {
        "name": "Пиворама на Белы Куна",
        "address": "Улица Белы Куна 3, ТРК «Международный», 4 этаж",
        "phone": "940-53-46",
        "work_hours": {
            "вс-чт": "12:00-23:00",
            "пт-сб": "12:00-24:00"
        },
        "halls": {
            "big": {"name": "Большой зал", "capacity": 80},
            "medium": {"name": "Средний зал", "capacity": 34},
            "small": {"name": "Малый зал", "capacity": 20},
            "terrace": {"name": "Панорамная терраса", "capacity": 42},
            "vip": {"name": "VIP зал", "capacity": 24}
        },
        "banquet_menus": [
            {"price": 3500, "description": "Базовое меню"},
            {"price": 4500, "description": "Расширенное меню"}
        ],
        "has_delivery": False
    }
}

def get_filial_name(filial_id: str) -> str:
    """Получить название филиала по ID"""
    return FILIALS.get(filial_id, {}).get("name", "Неизвестный филиал")

def get_filial_info(filial_id: str) -> dict:
    """Получить полную информацию о филиале"""
    return FILIALS.get(filial_id, {})