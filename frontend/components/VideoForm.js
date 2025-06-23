import React, { useState } from "react";

const VideoForm = () => {
  const [video, setVideo] = useState(null);
  const [message, setMessage] = useState("");
  const [resultUrl, setResultUrl] = useState("");
  const [decodedMessage, setDecodedMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [decoding, setDecoding] = useState(false);

  const handleVideoChange = (e) => {
    setVideo(e.target.files[0]);
  };

  const handleEncode = async (e) => {
    e.preventDefault();
    if (!video || !message) {
      alert("Please select a video file and enter a message.");
      return;
    }
    setLoading(true);
    setResultUrl("");
    const formData = new FormData();
    formData.append("video", video);
    formData.append("message", message);
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/video/encode/video`, {
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
    if (!video) {
      alert("Please select a video file.");
      return;
    }
    setDecoding(true);
    setDecodedMessage("");
    const formData = new FormData();
    formData.append("video", video);
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/video/decode/video`, {
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
      <div className="steg-section-title">Video Steganography</div>
      <form onSubmit={handleEncode} className="steg-form">
        <label>Upload Video File</label>
        <input type="file" accept="video/*" onChange={handleVideoChange} className="steg-file-input" />
        <label>Message to Hide</label>
        <input
          type="text"
          placeholder="Enter message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="steg-input"
        />
        <button type="submit" disabled={loading} className="steg-btn">
          {loading ? "Encoding..." : "Encode Video"}
        </button>
        {resultUrl && (
          <div style={{ marginTop: 8 }}>
            <a href={resultUrl} download="encoded_video.mp4" className="steg-result-link">
              Download Encoded Video
            </a>
          </div>
        )}
      </form>
      <form onSubmit={handleDecode} className="steg-form">
        <label>Decode Video File</label>
        <input type="file" accept="video/*" onChange={handleVideoChange} className="steg-file-input" />
        <button type="submit" disabled={decoding} className="steg-btn">
          {decoding ? "Decoding..." : "Decode Video"}
        </button>
        {decodedMessage && (
          <div className="steg-decoded-message">Decoded Message: {decodedMessage}</div>
        )}
      </form>
    </div>
  );
};

export default VideoForm;
