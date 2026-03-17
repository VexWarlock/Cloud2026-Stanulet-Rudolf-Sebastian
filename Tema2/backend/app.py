from flask import Flask, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_API = "http://localhost:8182"

# Helper pentru REST API
def get_authors():
    try:
        res = requests.get(f"{BASE_API}/authors")
        res.raise_for_status()
        return res.json()
    except:
        return []

def get_books():
    try:
        res = requests.get(f"{BASE_API}/books")
        res.raise_for_status()
        return res.json()
    except:
        return []

# Web Service extern 1: OpenLibrary
def get_book_info(title):
    try:
        res = requests.get(f"https://openlibrary.org/search.json?title={title}")
        data = res.json()
        if data.get("docs"):
            return {
                "first_publish_year": data["docs"][0].get("first_publish_year"),
                "isbn": data["docs"][0].get("isbn", [])
            }
    except:
        return None

# Web Service extern 2: Wikipedia
def get_author_info(name):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name.replace(' ','_')}"
        res = requests.get(url)
        data = res.json()
        return {
            "bio": data.get("extract"),
            "image": data.get("thumbnail", {}).get("source")
        }
    except:
        return None

# Aggregated endpoint
@app.route("/library", methods=["GET"])
def get_full_library():
    try:
        authors = get_authors()
        books = get_books()
        result = []

        for book in books:
            author = next((a for a in authors if a.get("id") == book.get("authorId")), None)
            try:
                book_info = get_book_info(book.get("title"))
                author_info = get_author_info(author.get("name")) if author else None
                result.append({
                    "book": book,
                    "author": author,
                    "external_book_data": book_info,
                    "external_author_data": author_info
                })
            except Exception as e:
                print(f"Error processing book {book.get('title')}: {e}")

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
