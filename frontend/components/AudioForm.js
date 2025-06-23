import React, { useState } from "react";

const AudioForm = () => {
  const [audio, setAudio] = useState(null);
  const [message, setMessage] = useState("");
  const [resultUrl, setResultUrl] = useState("");
  const [decoded, setDecoded] = useState("");
  const [loading, setLoading] = useState(false);
  const [decoding, setDecoding] = useState(false);

  const handleAudioChange = (e) => {
    setAudio(e.target.files[0]);
  };

  const handleEncode = async (e) => {
    e.preventDefault();
    if (!audio || !message) {
      alert("Please select an audio file and enter a message.");
      return;
    }
    setLoading(true);
    setResultUrl("");
    const formData = new FormData();
    formData.append("audio", audio);
    formData.append("message", message);
    const response = await fetch("http://localhost:8000/audio/encode/audio", {
      method: "POST",
      body: formData,
    });
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      setResultUrl(url);
    } else {
      alert("Encoding failed.");
    }
    setLoading(false);
  };

  const handleDecode = async (e) => {
    e.preventDefault();
    if (!audio) {
      alert("Please select an audio file.");
      return;
    }
    setDecoding(true);
    setDecoded("");
    const formData = new FormData();
    formData.append("audio", audio);
    const response = await fetch("http://localhost:8000/audio/decode/audio", {
      method: "POST",
      body: formData,
    });
    if (response.ok) {
      const data = await response.json();
      setDecoded(data.message);
    } else {
      alert("Decoding failed.");
    }
    setDecoding(false);
  };

  return (
    <div style={{ width: '100%' }}>
      <form onSubmit={handleEncode} style={{
        marginBottom: 28,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        background: 'rgba(44, 47, 80, 0.7)',
        padding: 24,
        borderRadius: 12,
        boxShadow: '0 2px 8px 0 rgba(92,107,192,0.10)',
      }}>
        <input type="file" accept="audio/wav,audio/mp3" onChange={handleAudioChange} style={{
          marginBottom: 16,
          background: '#23243a',
          color: '#e3e6f3',
          border: 'none',
          fontSize: 16,
        }} />
        <input
          type="text"
          placeholder="Enter message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          style={{
            marginBottom: 16,
            width: '100%',
            maxWidth: 340,
            padding: '12px 16px',
            borderRadius: 8,
            border: '1px solid #3949ab',
            background: '#23243a',
            color: '#e3e6f3',
            fontSize: 16,
            outline: 'none',
          }}
        />
        <button type="submit" disabled={loading} style={{
          width: '100%',
          maxWidth: 340,
          padding: '14px 0',
          borderRadius: 8,
          background: 'linear-gradient(90deg, #5c6bc0 0%, #3949ab 100%)',
          color: '#fff',
          fontWeight: 700,
          fontSize: 18,
          border: 'none',
          cursor: 'pointer',
          marginBottom: 8,
          boxShadow: '0 2px 8px 0 rgba(92,107,192,0.10)',
          letterSpacing: '0.5px',
        }}>
          {loading ? "Encoding..." : "Encode Audio"}
        </button>
        {resultUrl && (
          <div style={{ marginTop: 8 }}>
            <a href={resultUrl} download="encoded.wav" style={{ color: '#ffb300', fontWeight: 600 }}>
              Download Encoded Audio
            </a>
          </div>
        )}
      </form>
      <form onSubmit={handleDecode} style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        background: 'rgba(44, 47, 80, 0.7)',
        padding: 24,
        borderRadius: 12,
        boxShadow: '0 2px 8px 0 rgba(92,107,192,0.10)',
      }}>
        <input type="file" accept="audio/wav,audio/mp3" onChange={handleAudioChange} style={{
          marginBottom: 16,
          background: '#23243a',
          color: '#e3e6f3',
          border: 'none',
          fontSize: 16,
        }} />
        <button type="submit" disabled={decoding} style={{
          width: '100%',
          maxWidth: 340,
          padding: '14px 0',
          borderRadius: 8,
          background: 'linear-gradient(90deg, #5c6bc0 0%, #3949ab 100%)',
          color: '#fff',
          fontWeight: 700,
          fontSize: 18,
          border: 'none',
          cursor: 'pointer',
          marginBottom: 8,
          boxShadow: '0 2px 8px 0 rgba(92,107,192,0.10)',
          letterSpacing: '0.5px',
        }}>
          {decoding ? "Decoding..." : "Decode Audio"}
        </button>
        {decoded && (
          <div style={{ marginTop: 8, color: '#ffb300', fontWeight: 600, wordBreak: 'break-word', textAlign: 'center' }}>
            Decoded Message: {decoded}
          </div>
        )}
      </form>
    </div>
  );
};

export default AudioForm;
