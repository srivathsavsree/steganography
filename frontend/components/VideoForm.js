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
    <>
      <div className="steg-form">
        <div className="steg-section-title">Hide Message in Video</div>
        <form onSubmit={handleEncode}>
          <label>Upload Video File</label>
          <input type="file" accept="video/*" onChange={handleVideoChange} className="steg-file-input" />
          
          <label>Message to Hide</label>
          <input type="text" placeholder="Enter your secret message" value={message} onChange={(e) => setMessage(e.target.value)} className="steg-input" />
          
          <button type="submit" disabled={loading} className="steg-btn">
            {loading ? "Encoding..." : "Encode Video"}
          </button>
          
          {resultUrl && (
            <div style={{ marginTop: '1rem' }}>
              <a href={resultUrl} download="encoded_video.mp4" className="steg-result-link">
                Download Encoded Video
              </a>
            </div>
          )}
        </form>
      </div>
      
      <div className="steg-form">
        <div className="steg-section-title">Decode Hidden Message</div>
        <form onSubmit={handleDecode}>
          <label>Upload Encoded Video File</label>
          <input type="file" accept="video/*" onChange={handleVideoChange} className="steg-file-input" />
          
          <button type="submit" disabled={decoding} className="steg-btn">
            {decoding ? "Decoding..." : "Decode Video"}
          </button>
          
          {decodedMessage && (
            <div className="steg-decoded-message">
              <strong>Decoded Message:</strong> {decodedMessage}
            </div>
          )}
        </form>
      </div>
    </>
  );
};

export default VideoForm;
