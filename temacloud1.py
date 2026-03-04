from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

PORT = 8182

AUTHORS_FILE = "authors.json"
BOOKS_FILE = "books.json"


#asiguram persistenta datelor pe disk
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

#rest handler
class SimpleRESTHandler(BaseHTTPRequestHandler):

    #trimitere json
    def send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if data is not None:
            self.wfile.write(json.dumps(data).encode())

    #parse json body
    def parse_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        return json.loads(body)

#GET
    def do_GET(self):

    #GET ALL AUTHORS
        if self.path == "/authors":
            self.send_json(200, authors)

    #GET ALL BOOKS
        elif self.path == "/books":
            self.send_json(200, books)

    #GET AUTHOR BY ID
        elif self.path.startswith("/authors/"):
            try:
                author_id = int(self.path.split("/")[-1])
            except:
                self.send_json(400, {"error": "Invalid ID"})
                return

            for author in authors:
                if author["id"] == author_id:
                    self.send_json(200, author)
                    return

            self.send_json(404, {"error": "Author not found"})

    #GET BOOK BY ID
        elif self.path.startswith("/books/"):
            try:
                book_id = int(self.path.split("/")[-1])
            except:
                self.send_json(400, {"error": "Invalid ID"})
                return

            for book in books:
                if book["id"] == book_id:
                    self.send_json(200, book)
                    return

            self.send_json(404, {"error": "Book not found"})

        else:
            self.send_json(404, {"error": "Not found"})

#POST
    def do_POST(self):

    #CREATE AUTHOR
        if self.path == "/authors":
            data = self.parse_body()

            new_id = 1 if not authors else authors[-1]["id"] + 1

            author = {
                "id": new_id,
                "name": data["name"],
                "birthYear": data["birthYear"]
            }

            authors.append(author)
            save_data(AUTHORS_FILE, authors)

            self.send_json(201, author)

    #CREATE BOOK
        elif self.path == "/books":
            data = self.parse_body()

    #Verificam daca exista autor
            if not any(a["id"] == data["authorId"] for a in authors):
                self.send_json(400, {"error": "Author does not exist"})
                return

            new_id = 1 if not books else books[-1]["id"] + 1

            book = {
                "id": new_id,
                "title": data["title"],
                "authorId": data["authorId"],
                "year": data["year"]
            }

            books.append(book)
            save_data(BOOKS_FILE, books)

            self.send_json(201, book)

        else:
            self.send_json(404, {"error": "Not found"})

#PUT
    def do_PUT(self):

    #UPDATE AUTOR
        if self.path.startswith("/authors/"):
            try:
                author_id = int(self.path.split("/")[-1])
            except:
                self.send_json(400, {"error": "Invalid ID"})
                return

            data = self.parse_body()

            for author in authors:
                if author["id"] == author_id:
                    author["name"] = data["name"]
                    author["birthYear"] = data["birthYear"]

                    save_data(AUTHORS_FILE, authors)
                    self.send_json(200, author)
                    return

            self.send_json(404, {"error": "Author not found"})

    #UPDATE BOOK
        elif self.path.startswith("/books/"):
            try:
                book_id = int(self.path.split("/")[-1])
            except:
                self.send_json(400, {"error": "Invalid ID"})
                return

            data = self.parse_body()

            #verificare existenta autor
            if not any(a["id"] == data["authorId"] for a in authors):
                self.send_json(400, {"error": "Author does not exist"})
                return

            for book in books:
                if book["id"] == book_id:
                    book["title"] = data["title"]
                    book["authorId"] = data["authorId"]
                    book["year"] = data["year"]

                    save_data(BOOKS_FILE, books)
                    self.send_json(200, book)
                    return

            self.send_json(404, {"error": "Book not found"})

        else:
            self.send_json(404, {"error": "Not found"})

#DELETE
    def do_DELETE(self):
        global authors, books

    #DELETE AUTHOR
        if self.path.startswith("/authors/"):
            try:
                author_id = int(self.path.split("/")[-1])
            except:
                self.send_json(400, {"error": "Invalid ID"})
                return

            if not any(a["id"] == author_id for a in authors):
                self.send_json(404, {"error": "Author not found"})
                return

            authors = [a for a in authors if a["id"] != author_id]
            save_data(AUTHORS_FILE, authors)

            self.send_json(204, None)

    #DELETE BOOK
        elif self.path.startswith("/books/"):
            try:
                book_id = int(self.path.split("/")[-1])
            except:
                self.send_json(400, {"error": "Invalid ID"})
                return

            if not any(b["id"] == book_id for b in books):
                self.send_json(404, {"error": "Book not found"})
                return

            books = [b for b in books if b["id"] != book_id]
            save_data(BOOKS_FILE, books)

            self.send_json(204, None)

        else:
            self.send_json(404, {"error": "Not found"})





#START SERVER
def run():
    server = HTTPServer(('', PORT), SimpleRESTHandler)
    print(f"Server started.PORT: {PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
