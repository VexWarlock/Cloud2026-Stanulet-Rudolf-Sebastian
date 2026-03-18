from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

PORT = 8182
AUTHORS_FILE = "authors.json"
BOOKS_FILE = "books.json"

# =========================
# Persistence helpers
# =========================
def load_data(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return json.load(f)

def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

authors = load_data(AUTHORS_FILE)
books = load_data(BOOKS_FILE)

# =========================
# REST Handler
# =========================
class SimpleRESTHandler(BaseHTTPRequestHandler):

    def send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if data is not None:
            self.wfile.write(json.dumps(data).encode())

    def parse_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        return json.loads(body)

    # -------------------------
    # GET
    # -------------------------
    def do_GET(self):
        global authors, books
        if self.path == "/authors":
            self.send_json(200, authors)
        elif self.path == "/books":
            self.send_json(200, books)
        elif self.path.startswith("/authors/"):
            try:
                author_id = int(self.path.split("/")[-1])
            except:
                self.send_json(400, {"error":"Invalid ID"})
                return
            for author in authors:
                if author["id"] == author_id:
                    self.send_json(200, author)
                    return
            self.send_json(404, {"error":"Author not found"})
        elif self.path.startswith("/books/"):
            try:
                book_id = int(self.path.split("/")[-1])
            except:
                self.send_json(400, {"error":"Invalid ID"})
                return
            for book in books:
                if book["id"] == book_id:
                    self.send_json(200, book)
                    return
            self.send_json(404, {"error":"Book not found"})
        else:
            self.send_json(404, {"error":"Not found"})

    # -------------------------
    # POST
    # -------------------------
    def do_POST(self):
        global authors, books
        if self.path == "/authors":
            data = self.parse_body()
            new_id = 1 if not authors else authors[-1]["id"] + 1
            author = {
                "id": new_id,
                "name": data["name"],
                "birthYear": data["birthYear"],
                "city": data.get("city", "Unknown")
            }
            authors.append(author)
            save_data(AUTHORS_FILE, authors)
            self.send_json(201, author)

        elif self.path == "/books":
            data = self.parse_body()
            if not any(a["id"] == data["authorId"] for a in authors):
                self.send_json(400, {"error":"Author does not exist"})
                return
            new_id = 1 if not books else books[-1]["id"] + 1
            book = {"id": new_id, "title": data["title"], "authorId": data["authorId"], "year": data["year"]}
            books.append(book)
            save_data(BOOKS_FILE, books)
            self.send_json(201, book)
        else:
            self.send_json(404, {"error":"Not found"})

def run():
    server = HTTPServer(('', PORT), SimpleRESTHandler)
    print(f"REST API started on port {PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
