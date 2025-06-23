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
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/audio/encode/audio`, {
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
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/audio/decode/audio`, {
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
      <div className="steg-section-title">Audio Steganography</div>
      <form onSubmit={handleEncode} className="steg-form">
        <label>Upload Audio File</label>
        <input type="file" accept="audio/wav,audio/mp3" onChange={handleAudioChange} className="steg-file-input" />
        <label>Message to Hide</label>
        <input type="text" placeholder="Enter message" value={message} onChange={(e) => setMessage(e.target.value)} className="steg-input" />
        <button type="submit" disabled={loading} className="steg-btn">{loading ? "Encoding..." : "Encode Audio"}</button>
        {resultUrl && (
          <div style={{ marginTop: 8 }}>
            <a href={resultUrl} download="encoded.wav" className="steg-result-link">Download Encoded Audio</a>
          </div>
        )}
      </form>
      <form onSubmit={handleDecode} className="steg-form">
        <label>Decode Audio File</label>
        <input type="file" accept="audio/wav,audio/mp3" onChange={handleAudioChange} className="steg-file-input" />
        <button type="submit" disabled={decoding} className="steg-btn">{decoding ? "Decoding..." : "Decode Audio"}</button>
        {decoded && (
          <div className="steg-decoded-message">Decoded Message: {decoded}</div>
        )}
      </form>
    </div>
  );
};

export default AudioForm;
