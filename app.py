from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/photos"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.secret_key = "your-secret-key-here"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

DATA_FILE = "places_data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        places_data = json.load(f)
else:
    places_data = []


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            print("Получен POST запрос")  # Отладочное сообщение
            print("Form data:", request.form)  # Отладочное сообщение
            print("Files:", request.files)  # Отладочное сообщение

            # Собираем данные согласно новой структуре
            place = {
                "title": request.form.get("title", "").strip(),
                "url": request.form.get("url", "").strip(),
                "description": request.form.get("description", "").strip(),
                "entity_types": request.form.getlist("entity_types"),
                "atmosphere_tags": request.form.getlist("atmosphere_tags"),
                "purpose_tags": request.form.getlist("purpose_tags"),
                "budget_level": request.form.get("budget_level", "").strip(),
                "features": request.form.getlist("features"),
                "best_time": request.form.get("best_time", "").strip(),
                "opening_hours": request.form.get("opening_hours", "").strip(),
                "working_days": request.form.getlist("working_days"),
                "is_24_7": bool(request.form.get("is_24_7")),
            }

            print("Собранные данные:", place)  # Отладочное сообщение

            # Обрабатываем числовые поля
            overall_rating = request.form.get("overall_rating", "").strip()
            review_count = request.form.get("review_count", "").strip()

            if overall_rating:
                place["overall_rating"] = float(overall_rating)
            if review_count:
                place["review_count"] = int(review_count)

            # Обработка фотографий
            photos = request.files.getlist("photo")
            photo_paths = []

            for photo in photos:
                if photo and photo.filename:
                    print(f"Обработка файла: {photo.filename}")  # Отладочное сообщение
                    if allowed_file(photo.filename):
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S_%f")
                        filename = secure_filename(f"{timestamp}_{photo.filename}")
                        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                        photo.save(filepath)
                        photo_paths.append(filepath)
                        print(f"Файл сохранен: {filepath}")  # Отладочное сообщение
                    else:
                        print(
                            f"Недопустимый формат файла: {photo.filename}"
                        )  # Отладочное сообщение

            if photo_paths:
                place["photo"] = photo_paths[0]  # Первое фото как основное
                if len(photo_paths) > 1:
                    place["additional_photos"] = photo_paths[
                        1:
                    ]  # Остальные как дополнительные

            # Проверяем обязательные поля
            if not place.get("title"):
                flash("Название места обязательно для заполнения", "error")
                return render_template("index.html")

            # Добавляем timestamp
            place["created_at"] = datetime.now().isoformat()

            # Сохраняем в список
            places_data.append(place)
            print(
                f"Добавлено место. Всего мест: {len(places_data)}"
            )  # Отладочное сообщение

            # Сохраняем в JSON
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(places_data, f, ensure_ascii=False, indent=2)

            print(f"Данные сохранены в {DATA_FILE}")  # Отладочное сообщение

            flash("Место успешно добавлено!", "success")
            return redirect(url_for("index"))

        except Exception as e:
            print(f"Ошибка: {str(e)}")  # Отладочное сообщение
            flash(f"Произошла ошибка: {str(e)}", "error")

    return render_template("index.html")


@app.route("/data")
def show_data():
    """Страница для просмотра сохраненных данных"""
    print(f"Загружено мест: {len(places_data)}")  # Отладочное сообщение
    return render_template("data.html", places=places_data)


@app.route("/api/places")
def api_places():
    """API endpoint для получения данных в JSON формате"""
    return json.dumps(places_data, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Изменим порт на случай конфликтов
