import requests
import json
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = "7986de53-5751-49b3-8ba5-52e0a8f575c0"


def enhanced_convert_2gis_to_target_format(place_data):
    """Улучшенная конвертация данных из 2ГИС"""

    converted_place = {
        "title": "",
        "url": "",
        "description": "",
        "entity_types": [],
        "atmosphere_tags": [],
        "purpose_tags": [],
        "budget_level": "",
        "features": [],
        "best_time": "",
        "opening_hours": "",
        "working_days": [],
        "is_24_7": False,
        "overall_rating": 0.0,
        "photo": "",
        "created_at": datetime.now().isoformat(),
    }

    if "name" in place_data:
        converted_place["title"] = place_data["name"]

    if "external_content" in place_data:
        converted_place["url"] = place_data["external_content"].get("url", "")

    if "description" in place_data and place_data["description"]:
        converted_place["description"] = place_data["description"]

    # МАППИНГ ТИПОВ
    if "rubrics" in place_data:
        for rubric in place_data["rubrics"]:
            rubric_name = rubric.get("name", "").lower()

            rubric_mapping = {
                "ресторан": "ресторан",
                "кафе": "кафе",
                "бар": "бар",
                "паб": "бар",
                "кофейня": "кофейня",
                "чайная": "чайный домик",
                "столовая": "кафе",
                "бистро": "кафе",
                "пиццерия": "ресторан",
                "суши": "ресторан",
                "бургерная": "ресторан",
                "шашлычная": "ресторан",
                "блинная": "кафе",
                "пельменная": "кафе",
                "гриль-бар": "ресторан",
                "трактир": "ресторан",
                "винный бар": "бар",
                "пивной": "бар",
                "лаунж-бар": "бар",
                "спорт-бар": "бар",
                "караоке-бар": "бар",
                "кондитерская": "кондитерская",
                "пекарня": "пекарня",
                "мороженое": "кафе",
                "шоколад": "кондитерская",
                "музей": "музей",
                "галерея": "галерея",
                "кинотеатр": "кинотеатр",
                "театр": "театр",
                "клуб": "клуб",
                "ночной клуб": "клуб",
                "бильярд": "клуб",
                "боулинг": "клуб",
                "антикафе": "антикафе",
                "парк": "парк",
                "сквер": "парк",
                "сад": "парк",
                "набережная": "набережная",
                "площадь": "площадь",
                "смотровая": "смотровая площадка",
                "бутик": "бутик",
                "магазин": "бутик",
                "торговый центр": "бутик",
                "сувенир": "сувенирный магазин",
                "винтажный": "винтажный магазин",
                "книжный": "книжный магазин",
                "отель": "отель",
                "гостиница": "отель",
                "хостел": "отель",
                "сауна": "студия",
                "спа": "студия",
                "баня": "студия",
                "фитнес": "студия",
                "йога": "студия",
                "храм": "храм",
                "собор": "кафедральный собор",
                "церковь": "храм",
                "памятник": "памятник",
                "фонтан": "скульптура",
            }

            for key, value in rubric_mapping.items():
                if key in rubric_name:
                    if value not in converted_place["entity_types"]:
                        converted_place["entity_types"].append(value)

    # Если типы не определились - определяем по названию
    if not converted_place["entity_types"] and converted_place["title"]:
        title_lower = converted_place["title"].lower()
        title_mapping = {
            "ресторан": "ресторан",
            "кафе": "кафе",
            "бар": "бар",
            "паб": "бар",
            "кофейня": "кофейня",
            "кофе": "кофейня",
            "чай": "чайный домик",
            "музей": "музей",
            "галерея": "галерея",
            "кино": "кинотеатр",
            "театр": "театр",
            "клуб": "клуб",
            "отель": "отель",
            "гостиница": "отель",
            "бутик": "бутик",
            "магазин": "бутик",
            "салон": "бутик",
            "спорт": "студия",
            "фитнес": "студия",
            "йога": "студия",
            "храм": "храм",
            "собор": "кафедральный собор",
            "церковь": "храм",
            "памятник": "памятник",
            "парк": "парк",
            "сквер": "парк",
            "сад": "парк",
            "набережная": "набережная",
            "площадь": "площадь",
        }

        for key, value in title_mapping.items():
            if key in title_lower:
                converted_place["entity_types"].append(value)
                break

    if not converted_place["entity_types"]:
        converted_place["entity_types"] = ["кафе"]

    # АТМОСФЕРА
    atmosphere_by_type = {
        "ресторан": ["элегантный", "премиум", "романтичный"],
        "кафе": ["уютный", "домашний", "непринужденный"],
        "бар": ["энергичный", "шумный", "вечерний", "дружеский"],
        "кофейня": ["уютный", "тихий", "дневной", "рабочий"],
        "чайный домик": ["спокойный", "уютный", "дневной", "медитативный"],
        "кондитерская": ["уютный", "сладкий", "дневной", "семейный"],
        "пекарня": ["уютный", "домашний", "дневной", "ароматный"],
        "музей": ["спокойный", "тихий", "культурный", "образовательный"],
        "галерея": ["богемный", "артхаусный", "тихий", "вдохновляющий"],
        "кинотеатр": ["популярный", "вечерний", "развлекательный"],
        "театр": ["элегантный", "культурный", "вечерний", "торжественный"],
        "клуб": ["энергичный", "шумный", "ночной", "молодежный"],
        "парк": ["спокойный", "дневной", "семейный", "природный"],
        "набережная": ["романтичный", "спокойный", "вечерний", "живописный"],
        "бутик": ["элегантный", "премиум", "стильный"],
        "отель": ["элегантный", "премиум", "комфортный"],
        "храм": ["спокойный", "духовный", "тихий", "возвышенный"],
    }

    for entity_type in converted_place["entity_types"]:
        if entity_type in atmosphere_by_type:
            converted_place["atmosphere_tags"].extend(atmosphere_by_type[entity_type])

    converted_place["atmosphere_tags"] = list(set(converted_place["atmosphere_tags"]))[
        :4
    ]

    # НАЗНАЧЕНИЕ
    purpose_by_type = {
        "ресторан": ["ужин", "свидание", "бизнес", "празднование", "деловой обед"],
        "кафе": ["обед", "друзья", "работа", "быстрый визит", "перекус"],
        "бар": ["друзья", "вечеринка", "алкоголь", "знакомства", "релакс"],
        "кофейня": ["работа", "учеба", "встреча", "наедине", "чтение"],
        "чайный домик": ["встреча", "наедине", "релаксация", "беседа"],
        "кондитерская": ["десерт", "перекус", "празднование", "сладкий перерыв"],
        "пекарня": ["завтрак", "перекус", "быстрый визит", "кофе с выпечкой"],
        "музей": [
            "осмотр достопримечательностей",
            "образование",
            "культура",
            "экскурсия",
        ],
        "галерея": [
            "осмотр достопримечательностей",
            "культура",
            "фотосъемка",
            "вдохновение",
        ],
        "кинотеатр": ["развлечения", "свидание", "друзья", "отдых"],
        "театр": ["культура", "свидание", "развлечения", "искусство"],
        "клуб": ["танцы", "вечеринка", "знакомства", "отдых"],
        "парк": ["прогулки", "отдых", "спорт", "семья", "пикник"],
        "набережная": ["прогулки", "свидание", "фотосъемка", "медитация"],
        "бутик": ["шоппинг", "подарки", "мода", "обновление гардероба"],
        "отель": ["отдых", "бизнес", "путешествия", "ночевка"],
    }

    for entity_type in converted_place["entity_types"]:
        if entity_type in purpose_by_type:
            converted_place["purpose_tags"].extend(purpose_by_type[entity_type])

    converted_place["purpose_tags"] = list(set(converted_place["purpose_tags"]))[:5]

    # БЮДЖЕТ
    budget_by_type = {
        "ресторан": "средний",
        "кафе": "бюджетный",
        "бар": "средний",
        "кофейня": "бюджетный",
        "чайный домик": "средний",
        "кондитерская": "средний",
        "пекарня": "бюджетный",
        "музей": "бюджетный",
        "галерея": "бюджетный",
        "кинотеатр": "средний",
        "театр": "средний",
        "клуб": "дорогой",
        "парк": "бюджетный",
        "набережная": "бюджетный",
        "бутик": "дорогой",
        "отель": "дорогой",
        "храм": "бюджетный",
    }

    for entity_type in converted_place["entity_types"]:
        if entity_type in budget_by_type:
            converted_place["budget_level"] = budget_by_type[entity_type]
            break

    # ОСОБЕННОСТИ
    features_by_type = {
        "ресторан": ["бронирование", "алкоголь", "вегетарианец", "живая музыка"],
        "кафе": ["Wi-Fi", "вегетарианец", "еда на вынос", "доступная среда"],
        "бар": ["алкоголь", "живая музыка", "танцы", "караоке"],
        "кофейня": ["Wi-Fi", "вегетарианец", "работа", "книги"],
        "чайный домик": ["чайная церемония", "восточная атмосфера", "релакс"],
        "кондитерская": ["свежая выпечка", "авторские десерты", "подарки"],
        "пекарня": ["свежий хлеб", "выпечка", "кофе", "быстрый перекус"],
        "музей": ["экскурсии", "культура", "история", "образовательные программы"],
        "парк": ["бесплатный вход", "прогулки", "природа", "детские площадки"],
    }

    for entity_type in converted_place["entity_types"]:
        if entity_type in features_by_type:
            converted_place["features"].extend(features_by_type[entity_type])

    converted_place["features"] = list(set(converted_place["features"]))[:4]

    # Описание
    if not converted_place["description"]:
        entity_names = ", ".join(converted_place["entity_types"])
        atmosphere_names = ", ".join(converted_place["atmosphere_tags"][:2])
        converted_place["description"] = (
            f"{converted_place['title']} - {entity_names} с {atmosphere_names} атмосферой в самом сердце Москвы"
        )

    # Рейтинг
    if "reviews" in place_data and "rating" in place_data["reviews"]:
        converted_place["overall_rating"] = float(place_data["reviews"]["rating"])
    else:
        default_ratings = {
            "ресторан": 4.5,
            "кафе": 4.3,
            "бар": 4.2,
            "кофейня": 4.6,
            "музей": 4.7,
            "парк": 4.8,
            "отель": 4.4,
        }
        for entity_type in converted_place["entity_types"]:
            if entity_type in default_ratings:
                converted_place["overall_rating"] = default_ratings[entity_type]
                break

    return converted_place


def search_2gis_aggressive(category, city="москва", page_size=50, page=1):
    """Агрессивный поиск с обработкой ошибок"""

    url = "https://catalog.api.2gis.ru/3.0/items"
    params = {
        "q": category,
        "region": city,
        "key": API_KEY,
        "page_size": page_size,
        "page": page,
        "fields": "items.name,items.rubrics,items.reviews,items.contacts,items.external_content,items.description,items.point",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка API: {response.status_code} для {category}")
    except Exception as e:
        print(f"Ошибка запроса: {e} для {category}")

    return None


def is_in_kitai_gorod(place):
    """Проверяет, находится ли место в Китай-городе"""
    kitai_gorod_bounds = {
        "sw_lat": 55.7470,
        "sw_lon": 37.6100,  # Расширили границы
        "ne_lat": 55.7650,
        "ne_lon": 37.6500,
    }

    if "point" in place:
        lat = place["point"].get("lat", 0)
        lon = place["point"].get("lon", 0)

        return (
            kitai_gorod_bounds["sw_lat"] <= lat <= kitai_gorod_bounds["ne_lat"]
            and kitai_gorod_bounds["sw_lon"] <= lon <= kitai_gorod_bounds["ne_lon"]
        )

    return False


def mass_search_kitai_gorod():
    """Массовый поиск мест в Китай-городе"""

    # ОСНОВНЫЕ КАТЕГОРИИ ДЛЯ ПОИСКА
    primary_categories = [
        "ресторан",
        "кафе",
        "бар",
        "кофейня",
        "паб",
        "столовая",
        "бистро",
        "пиццерия",
        "суши",
        "бургерная",
        "шашлычная",
        "блинная",
        "пельменная",
        "пекарня",
        "кондитерская",
        "мороженое",
        "шоколад",
        "булочная",
        "чайная",
        "гриль-бар",
        "винный бар",
        "пивной бар",
        "лаунж-бар",
    ]

    # ДОПОЛНИТЕЛЬНЫЕ КАТЕГОРИИ
    secondary_categories = [
        "музей",
        "галерея",
        "кинотеатр",
        "театр",
        "клуб",
        "ночной клуб",
        "караоке",
        "бильярд",
        "боулинг",
        "антикафе",
        "парк",
        "сквер",
        "сад",
        "набережная",
        "площадь",
        "смотровая площадка",
        "бутик",
        "магазин",
        "торговый центр",
        "сувениры",
        "книжный магазин",
        "отель",
        "гостиница",
        "хостел",
        "сауна",
        "спа",
        "баня",
        "фитнес",
        "йога",
        "храм",
        "собор",
        "церковь",
        "памятник",
        "фонтан",
    ]

    # УЛИЦЫ КИТАЙ-ГОРОДА
    kitai_gorod_streets = [
        "Варварка",
        "Ильинка",
        "Никольская",
        "Маросейка",
        "Покровка",
        "Мясницкая",
        "Лубянка",
        "Рождественка",
        "Кузнецкий Мост",
        "Петровка",
        "Неглинная",
        "Тверская",
        "Охотный Ряд",
        "Моховая",
        "Театральный проезд",
        "Китайгородский проезд",
        "Старая площадь",
        "Новая площадь",
    ]

    all_converted_places = []
    processed_titles = set()

    print("🚀 ЗАПУСК МАССОВОГО ПОИСКА В КИТАЙ-ГОРОДЕ")
    print("=" * 50)

    # ПОИСК ПО ОСНОВНЫМ КАТЕГОРИЯМ (много страниц)
    print("\n📋 ПОИСК ПО ОСНОВНЫМ КАТЕГОРИЯМ...")
    for category in primary_categories:
        print(f"\n🔍 Ищем: {category.upper()}")

        for page in range(1, 6):  # По 5 страниц на категорию
            print(f"   Страница {page}...", end=" ")

            data = search_2gis_aggressive(category, page_size=50, page=page)
            if data and "result" in data and "items" in data["result"]:
                places = data["result"]["items"]

                # Фильтруем по Китай-городу
                kitai_gorod_places = [p for p in places if is_in_kitai_gorod(p)]

                # Конвертируем и добавляем
                for place in kitai_gorod_places:
                    if place.get("name") not in processed_titles:
                        converted = enhanced_convert_2gis_to_target_format(place)
                        all_converted_places.append(converted)
                        processed_titles.add(place.get("name"))
                        print(f"✓", end="")

                print(f" | Найдено: {len(kitai_gorod_places)}")

                # Если меньше 10 мест на странице - переходим к следующей категории
                if len(places) < 10:
                    break
            else:
                print("✗ Нет данных")
                break

            time.sleep(0.2)  # Короткая задержка

    # ПОИСК ПО ДОПОЛНИТЕЛЬНЫМ КАТЕГОРИЯМ
    print("\n📋 ПОИСК ПО ДОПОЛНИТЕЛЬНЫМ КАТЕГОРИЯМ...")
    for category in secondary_categories:
        print(f"🔍 Ищем: {category}...", end=" ")

        data = search_2gis_aggressive(category, page_size=30, page=1)
        if data and "result" in data and "items" in data["result"]:
            places = data["result"]["items"]
            kitai_gorod_places = [p for p in places if is_in_kitai_gorod(p)]

            for place in kitai_gorod_places:
                if place.get("name") not in processed_titles:
                    converted = enhanced_convert_2gis_to_target_format(place)
                    all_converted_places.append(converted)
                    processed_titles.add(place.get("name"))

            print(f"✓ Найдено: {len(kitai_gorod_places)}")
        else:
            print("✗ Нет данных")

        time.sleep(0.2)

    # ПОИСК ПО УЛИЦАМ
    print("\n📋 ПОИСК ПО УЛИЦАМ КИТАЙ-ГОРОДА...")
    for street in kitai_gorod_streets:
        print(f"📍 Ищем на: {street}...", end=" ")

        data = search_2gis_aggressive(street, page_size=40, page=1)
        if data and "result" in data and "items" in data["result"]:
            places = data["result"]["items"]

            for place in places:
                if place.get("name") not in processed_titles and is_in_kitai_gorod(
                    place
                ):
                    converted = enhanced_convert_2gis_to_target_format(place)
                    all_converted_places.append(converted)
                    processed_titles.add(place.get("name"))

            print(f"✓ Найдено: {len([p for p in places if is_in_kitai_gorod(p)])}")
        else:
            print("✗ Нет данных")

        time.sleep(0.2)

    # ПОИСК ПО КЛЮЧЕВЫМ СЛОВАМ
    print("\n📋 ПОИСК ПО КЛЮЧЕВЫМ СЛОВАМ...")
    keywords = [
        "итальянская кухня",
        "японская кухня",
        "европейская кухня",
        "русская кухня",
        "французская кухня",
        "кофе с собой",
        "завтрак",
        "бизнес-ланч",
        "ужин",
        "крафтовое пиво",
        "коктейли",
        "живая музыка",
        "веранда",
        "терраса",
        "панорамный вид",
        "исторический",
        "старинный",
        "атмосферный",
    ]

    for keyword in keywords:
        print(f"🔑 Ищем: '{keyword}'...", end=" ")

        data = search_2gis_aggressive(keyword, page_size=20, page=1)
        if data and "result" in data and "items" in data["result"]:
            places = data["result"]["items"]
            kitai_gorod_places = [p for p in places if is_in_kitai_gorod(p)]

            for place in kitai_gorod_places:
                if place.get("name") not in processed_titles:
                    converted = enhanced_convert_2gis_to_target_format(place)
                    all_converted_places.append(converted)
                    processed_titles.add(place.get("name"))

            print(f"✓ Найдено: {len(kitai_gorod_places)}")
        else:
            print("✗ Нет данных")

        time.sleep(0.2)

    # ФИНАЛЬНЫЙ РЕЗУЛЬТАТ
    print("\n" + "=" * 50)
    print(f"🎉 ПОИСК ЗАВЕРШЕН!")
    print(f"📊 Всего найдено мест: {len(all_converted_places)}")

    # Статистика по типам
    type_stats = {}
    for place in all_converted_places:
        for entity_type in place["entity_types"]:
            type_stats[entity_type] = type_stats.get(entity_type, 0) + 1

    print("\n📈 СТАТИСТИКА ПО ТИПАМ:")
    for entity_type, count in sorted(
        type_stats.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"   {entity_type}: {count} мест")

    # Сохраняем результаты
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"kitai_gorod_massive_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_converted_places, f, ensure_ascii=False, indent=2)

    # Добавляем в основную базу
    try:
        with open("places_data.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except:
        existing_data = []

    # Убираем дубликаты при объединении
    existing_titles = {p["title"] for p in existing_data}
    new_places = [p for p in all_converted_places if p["title"] not in existing_titles]

    existing_data.extend(new_places)

    with open("places_data.json", "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 ДАННЫЕ СОХРАНЕНЫ:")
    print(f"   Основной файл: places_data.json (всего {len(existing_data)} мест)")
    print(f"   Отдельный файл: {filename}")
    print(f"   Новых мест добавлено: {len(new_places)}")

    return all_converted_places


# ЗАПУСК
if __name__ == "__main__":
    start_time = time.time()

    try:
        results = mass_search_kitai_gorod()

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n⏱️  Время выполнения: {duration:.1f} секунд")
        print(f"📦 Средняя скорость: {len(results) / duration:.1f} мест/секунду")

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback

        traceback.print_exc()
