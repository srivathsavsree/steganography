import React, { useState } from "react";

const EncodeForm = () => {
  const [image, setImage] = useState(null);
  const [message, setMessage] = useState("");
  const [resultUrl, setResultUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [decodeImage, setDecodeImage] = useState(null);
  const [decodedMessage, setDecodedMessage] = useState("");
  const [decoding, setDecoding] = useState(false);

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image || !message) {
      alert("Please select an image and enter a message.");
      return;
    }
    setLoading(true);
    setResultUrl("");
    const formData = new FormData();
    formData.append("image", image);
    formData.append("message", message);
    const response = await fetch("http://localhost:8000/encode/image", {
      method: "POST",
      body: formData,
    });
    if (response.ok) {
      const data = await response.json();
      setResultUrl(data.url);
    } else {
      alert("Encoding failed.");
    }
    setLoading(false);
  };

  const handleDecodeImageChange = (e) => {
    setDecodeImage(e.target.files[0]);
  };

  const handleDecode = async (e) => {
    e.preventDefault();
    if (!decodeImage) {
      alert("Please select a PNG image to decode.");
      return;
    }
    setDecoding(true);
    setDecodedMessage("");
    const formData = new FormData();
    formData.append("image", decodeImage);
    const response = await fetch("http://localhost:8000/decode/image", {
      method: "POST",
      body: formData,
    });
    if (response.ok) {
      const data = await response.json();
      setDecodedMessage(data.message);
    } else {
      alert("Decoding failed.");
    }
    setDecoding(false);
  };

  return (
    <div style={{ width: '100%' }}>
      <form onSubmit={handleSubmit} style={{
        marginBottom: 28,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        background: 'rgba(44, 47, 80, 0.7)',
        padding: 24,
        borderRadius: 12,
        boxShadow: '0 2px 8px 0 rgba(92,107,192,0.10)',
      }}>
        <input type="file" accept="image/png" onChange={handleImageChange} style={{
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
          {loading ? "Encoding..." : "Encode Image"}
        </button>
        {resultUrl && (
          <div style={{ marginTop: 8 }}>
            <a href={resultUrl} target="_blank" rel="noopener noreferrer" style={{ color: '#ffb300', fontWeight: 600 }}>
              Download Encoded Image
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
        <input type="file" accept="image/png" onChange={handleDecodeImageChange} style={{
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
          {decoding ? "Decoding..." : "Decode Image"}
        </button>
        {decodedMessage && (
          <div style={{ marginTop: 8, color: '#ffb300', fontWeight: 600, wordBreak: 'break-word', textAlign: 'center' }}>
            Decoded Message: {decodedMessage}
          </div>
        )}
      </form>
    </div>
  );
};

export default EncodeForm;
