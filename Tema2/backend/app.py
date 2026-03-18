from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

BASE_API = "http://localhost:8182"  # REST API local
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

weather_cache = {}  # cache pentru orașe

def get_authors():
    try:
        res = requests.get(f"{BASE_API}/authors", timeout=5)
        res.raise_for_status()
        authors = res.json()
        for author in authors:
            if "city" not in author:
                author["city"] = "Unknown"
        return authors
    except requests.exceptions.RequestException as e:
        print("Authors error:", e)
        return None  # indică eroare pentru status 500

def get_books():
    try:
        res = requests.get(f"{BASE_API}/books", timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print("Books error:", e)
        return None

def get_book_info(title):
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}&key={GOOGLE_API_KEY}"
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        if "items" in data and len(data["items"]) > 0:
            info = data["items"][0]["volumeInfo"]
            return {
                "description": info.get("description", "No description"),
                "pages": info.get("pageCount", "Unknown")
            }
    except requests.exceptions.RequestException as e:
        print("Google Books error:", e)
    return {"description": "No description", "pages": "Unknown"}

def get_weather(city):
    if city in weather_cache:
        return weather_cache[city]
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={WEATHER_API_KEY}"
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        result = {"temperature": data["main"]["temp"], "weather": data["weather"][0]["description"]}
        weather_cache[city] = result
        return result
    except requests.exceptions.RequestException as e:
        print(f"Weather error for {city}:", e)
        result = {"temperature": "Unknown", "weather": "Unknown"}
        weather_cache[city] = result
        return result

# =========================
# Aggregated endpoint
# =========================
@app.route("/library", methods=["GET"])
def get_full_library():
    authors = get_authors()
    if authors is None:
        return jsonify({"error": "Failed to fetch authors from REST API"}), 500

    books = get_books()
    if books is None:
        return jsonify({"error": "Failed to fetch books from REST API"}), 500

    result = []
    for book in books:
        author = next((a for a in authors if a["id"] == book["authorId"]), None)
        if not author:
            # Carte fără autor valid
            continue

        book_info = get_book_info(book["title"])
        weather = get_weather(author["city"])

        result.append({
            "book": book,
            "author": author,
            "external_book_data": book_info,
            "external_weather": weather
        })

    if not result:
        return jsonify({"error": "No books found"}), 404

    return jsonify(result), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)

# API-uri folosite
# Google Books API:
# https://developers.google.com/books/docs/v1/using
# OpenWeather API:
# https://openweathermap.org/api
