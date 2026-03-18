import React, { useEffect, useState } from "react";

function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5000/library")
      .then(res => {
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        return res.json();
      })
      .then(data => {
        setData(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setErrorMsg(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>📚 Library App</h1>
      {loading && <p>Loading books...</p>}
      {errorMsg && <p style={{color:"red"}}>Error: {errorMsg}</p>}
      {!loading && data.length === 0 && <p>No books found</p>}

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
          <p><b>City:</b> {item.author?.city || "Unknown"}</p>
          <p><b>Year:</b> {item.book.year || "Unknown"}</p>

          <p><b>Description:</b> {item.external_book_data?.description || "No description"}</p>
          <p><b>Pages:</b> {item.external_book_data?.pages || "Unknown"}</p>

          <p><b>Weather:</b> {item.external_weather?.weather || "Unknown"}</p>
          <p><b>Temperature:</b> {item.external_weather?.temperature || "Unknown"} °C</p>
        </div>
      ))}
    </div>
  );
}

export default App;
