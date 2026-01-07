import { useState } from "react";
import "./App.css";

export default function Genere() {
  const generos = ["Rock","Pop","Hip-Hop","Jazz","Clásica","Electrónica","Folk","Reggae","Urbano","Metal"];
  const [clickedSet, setClickedSet] = useState(() => new Set());

  const [track, setTrack] = useState(null);
  const [loadingGenero, setLoadingGenero] = useState(null);
  const [error, setError] = useState("");

  const toggle = (i) => {
    setClickedSet(prev => {
      const next = new Set(prev);
      next.has(i) ? next.delete(i) : next.add(i);
      return next;
    });
  };

  async function pedirCancion(genero) {
    setError("");
    setTrack(null);
    setLoadingGenero(genero);

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/lastfm/random?genre=${encodeURIComponent(genero)}`);
      const data = await res.json();

      if (!res.ok) throw new Error(data?.detail || "Error pidiendo canción");

      setTrack(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingGenero(null);
    }
  }

  const handleClick = (genero, index) => {
    toggle(index);
    pedirCancion(genero);
  };

  return (
    <div className="card">
      {generos.map((genero, index) => (
        <button
          key={index}
          onClick={() => handleClick(genero, index)}
          style={{ color: clickedSet.has(index) ? "green" : "black" }}
          disabled={loadingGenero === genero}
        >
          {loadingGenero === genero ? "Buscando..." : genero}
        </button>
      ))}

      <div style={{ marginTop: 16 }}>
        {error && <div style={{ color: "red" }}>{error}</div>}
        {track && (
          <div>
            <div><b>{track.name}</b> — {track.artist}</div>
            {track.url && (
              <a href={track.url} target="_blank" rel="noreferrer">
                Ver en Last.fm
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
