"""Меню ресторана Пиворама"""

MENU_CATEGORIES = {
    "snacks": {
        "name": "🥨 Закуски",
        "items": [
            {"id": "snack_1", "name": "Сухарики ржаные", "price": 150, "weight": "100г"},
            {"id": "snack_2", "name": "Колбаски охотничьи", "price": 350, "weight": "150г"},
            {"id": "snack_3", "name": "Сырная тарелка", "price": 450, "weight": "200г"},
            {"id": "snack_4", "name": "Рыбная тарелка", "price": 550, "weight": "250г"}
        ]
    },
    "salads": {
        "name": "🥗 Салаты",
        "items": [
            {"id": "salad_1", "name": "Цезарь с курицей", "price": 380, "weight": "200г"},
            {"id": "salad_2", "name": "Греческий", "price": 320, "weight": "180г"},
            {"id": "salad_3", "name": "Оливье", "price": 280, "weight": "200г"}
        ]
    },
    "hot_dishes": {
        "name": "🍖 Горячие блюда",
        "items": [
            {"id": "hot_1", "name": "Свиная рулька", "price": 850, "weight": "500г"},
            {"id": "hot_2", "name": "Куриные крылышки BBQ", "price": 450, "weight": "300г"},
            {"id": "hot_3", "name": "Ребрышки в медовом соусе", "price": 650, "weight": "400г"}
        ]
    },
    "beer": {
        "name": "🍺 Пиво",
        "items": [
            {"id": "beer_1", "name": "Пиворама Светлое (0.5л)", "price": 250, "weight": "0.5л"},
            {"id": "beer_2", "name": "Пиворама Темное (0.5л)", "price": 280, "weight": "0.5л"},
            {"id": "beer_3", "name": "Heineken (0.5л)", "price": 320, "weight": "0.5л"}
        ]
    },
    "drinks": {
        "name": "🥤 Напитки",
        "items": [
            {"id": "drink_1", "name": "Кока-Кола (0.5л)", "price": 150, "weight": "0.5л"},
            {"id": "drink_2", "name": "Морс клюквенный", "price": 180, "weight": "0.3л"},
            {"id": "drink_3", "name": "Чай", "price": 120, "weight": "0.4л"}
        ]
    }
}

def get_all_items() -> list:
    """Получить все блюда из меню"""
    all_items = []
    for category in MENU_CATEGORIES.values():
        all_items.extend(category["items"])
    return all_items

def get_item_by_id(item_id: str) -> dict:
    """Найти блюдо по ID"""
    for category in MENU_CATEGORIES.values():
        for item in category["items"]:
            if item["id"] == item_id:
                return item
    return None

def get_category_by_id(category_id: str) -> dict:
    """Получить категорию по ID"""
    return MENU_CATEGORIES.get(category_id, {})