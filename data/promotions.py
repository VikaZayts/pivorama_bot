"""Акции и специальные предложения"""

PROMOTIONS = {
    "ladies_day": {
        "name": "👩 Женский день",
        "description": "Скидка 30% для компаний от 4 дам по вторникам",
        "day_of_week": 1,  # 0=ПН, 1=ВТ, 2=СР, ...
        "min_girls": 4,
        "discount_percent": 30,
        "active": True
    },
    "happy_hours": {
        "name": "🍺 Happy Hours",
        "description": "Скидка 20% на все пиво с 12:00 до 16:00",
        "start_hour": 12,
        "end_hour": 16,
        "discount_percent": 20,
        "active": True
    },
    "birthday": {
        "name": "🎂 День рождения",
        "description": "Скидка 15% имениннику в день рождения",
        "discount_percent": 15,
        "active": True
    }
}

def get_active_promotions() -> list:
    """Получить список активных акций"""
    return [promo for promo in PROMOTIONS.values() if promo.get("active", False)]