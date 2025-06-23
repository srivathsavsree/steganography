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
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/encode/image`, {
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
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/decode/image`, {
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

  // Add this function for downloading the image
  const handleDownload = async () => {
    const response = await fetch(resultUrl);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'encoded.png';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div style={{ width: '100%' }}>
      <div className="steg-section-title">Image Steganography</div>
      <form onSubmit={handleSubmit} className="steg-form">
        <label>Upload PNG Image</label>
        <input type="file" accept="image/png" onChange={handleImageChange} className="steg-file-input" />
        <label>Message to Hide</label>
        <input
          type="text"
          placeholder="Enter message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="steg-input"
        />
        <button type="submit" disabled={loading} className="steg-btn">
          {loading ? "Encoding..." : "Encode Image"}
        </button>
        {resultUrl && (
          <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <a href={resultUrl} target="_blank" rel="noopener noreferrer" className="steg-result-link">View Encoded Image</a>
            <button type="button" onClick={handleDownload} className="steg-btn">Download Image</button>
          </div>
        )}
      </form>
      <form onSubmit={handleDecode} className="steg-form">
        <label>Decode PNG Image</label>
        <input type="file" accept="image/png" onChange={handleDecodeImageChange} className="steg-file-input" />
        <button type="submit" disabled={decoding} className="steg-btn">
          {decoding ? "Decoding..." : "Decode Image"}
        </button>
        {decodedMessage && (
          <div className="steg-decoded-message">Decoded Message: {decodedMessage}</div>
        )}
      </form>
    </div>
  );
};

export default EncodeForm;
