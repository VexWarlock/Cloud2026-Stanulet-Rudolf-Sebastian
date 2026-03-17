import React, { useEffect, useState } from "react";

function App() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/library")
      .then(res => res.json())
      .then(data => setData(data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>📚 Library App</h1>

      {data.length === 0 && <p>Loading books...</p>}

      {data.map((item) => (
        <div
          key={item.book.id}
          style={{
            border: "1px solid gray",
            borderRadius: "8px",
            margin: "10px 0",
            padding: "15px",
            boxShadow: "1px 1px 5px rgba(0,0,0,0.2)"
          }}
        >
          <h2>{item.book.title}</h2>
          <p><b>Author:</b> {item.author?.name || "Unknown"}</p>
          <p><b>Year:</b> {item.book.year || "Unknown"}</p>
          <p><b>First Published:</b> {item.external_book_data?.first_publish_year || "Unknown"}</p>
          <p><b>Bio:</b> {item.external_author_data?.bio || "No bio available"}</p>
          {item.external_author_data?.image && (
            <img
              src={item.external_author_data.image}
              width="100"
              alt={item.author?.name || "Author"}
              style={{ marginTop: "10px", borderRadius: "4px" }}
            />
          )}
        </div>
      ))}
    </div>
  );
}

export default App;
