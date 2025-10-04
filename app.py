from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/screenshots"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.secret_key = "your-secret-key-here"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

DATA_FILE = "data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        places_data = json.load(f)
else:
    places_data = []


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Собираем данные в нужном формате
            place = {
                "название": request.form.get("name", "").strip(),
                "ссылка_2gis": request.form.get("link", "").strip(),
                "описание": request.form.get("description", "").strip(),
                # Категории в нужном формате
                "тип_места": request.form.getlist("entity"),
                "атмосфера": request.form.getlist("atmosphere"),
                "ситуации": request.form.getlist("context"),
                "услуги": request.form.getlist("features"),
                # Детали
                "аудитория": request.form.get("target_audience", "").strip(),
                "лучшее_время": request.form.get("best_time", "").strip(),
                "освещение": request.form.get("lighting", "").strip(),
                "бюджет": request.form.get("budget", "").strip(),
                # Дополнительные поля для разных типов мест
                "дополнительно": {},
            }

            # Обрабатываем дополнительные поля в зависимости от типа места
            selected_entities = request.form.getlist("entity")

            # Для заведений с едой/напитками
            if any(
                entity in ["Ресторан", "Кафе", "Бар / Паб", "Кофейня"]
                for entity in selected_entities
            ):
                place["дополнительно"]["кухня"] = request.form.get(
                    "cuisine_type", ""
                ).strip()
                place["дополнительно"]["время_работы"] = request.form.get(
                    "working_hours", ""
                ).strip()
                if request.form.get("wifi"):
                    place["услуги"].append("Wi-Fi")

            # Для парков и прогулочных мест
            if any(
                entity in ["Парк", "Набережная", "Сквер", "Смотровая площадка"]
                for entity in selected_entities
            ):
                if request.form.get("parking"):
                    place["услуги"].append("Парковка")
                if request.form.get("child_friendly"):
                    place["услуги"].append("Для детей")
                if request.form.get("picnic_zone"):
                    place["услуги"].append("Зона пикника")

            # Для культурных мест
            if any(
                entity in ["Музей", "Арт-центр / Галерея", "Кинотеатр"]
                for entity in selected_entities
            ):
                place["дополнительно"]["стоимость_билета"] = request.form.get(
                    "ticket_price", ""
                ).strip()
                place["дополнительно"]["режим_работы"] = request.form.get(
                    "schedule", ""
                ).strip()
                if request.form.get("excursions"):
                    place["услуги"].append("Экскурсии")

            # Для улиц/магазинов/клубов
            if any(
                entity in ["Улица", "Бутик", "Клуб / Лаунж"]
                for entity in selected_entities
            ):
                place["дополнительно"]["особенности"] = request.form.get(
                    "street_features", ""
                ).strip()
                if request.form.get("live_music"):
                    place["услуги"].append("Живая музыка")

            # Обработка скриншотов
            screenshots = request.files.getlist("screenshot")
            screenshot_paths = []

            for screenshot in screenshots:
                if screenshot and screenshot.filename:
                    if allowed_file(screenshot.filename):
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S_%f")
                        filename = secure_filename(f"{timestamp}_{screenshot.filename}")
                        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                        screenshot.save(filepath)
                        screenshot_paths.append(filepath)

            if screenshot_paths:
                place["фотографии"] = screenshot_paths

            # Удаляем пустые массивы и строки
            place = {
                k: v
                for k, v in place.items()
                if v and (v != [] if isinstance(v, list) else v != "")
            }

            # Если дополнительно пустой объект - удаляем его
            if not place.get("дополнительно"):
                place.pop("дополнительно", None)

            # Проверяем обязательные поля
            if not place.get("название"):
                flash("Название места обязательно для заполнения", "error")
                return render_template("index.html")

            # Добавляем timestamp
            place["дата_добавления"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Сохраняем в список
            places_data.append(place)

            # Сохраняем в JSON
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    places_data, f, ensure_ascii=False, indent=2, separators=(",", ": ")
                )

            flash("Место успешно добавлено!", "success")
            return redirect(url_for("index"))

        except Exception as e:
            flash(f"Произошла ошибка: {str(e)}", "error")

    return render_template("index.html")


@app.route("/data")
def show_data():
    """Страница для просмотра сохраненных данных"""
    return render_template("data.html", places=places_data)


if __name__ == "__main__":
    app.run(debug=True)
