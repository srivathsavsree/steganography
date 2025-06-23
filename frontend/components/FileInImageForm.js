import React, { useState } from "react";

const FileInImageForm = () => {
  const [image, setImage] = useState(null);
  const [file, setFile] = useState(null);
  const [resultUrl, setResultUrl] = useState("");
  const [decodedFileUrl, setDecodedFileUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [decoding, setDecoding] = useState(false);

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleEncode = async (e) => {
    e.preventDefault();
    if (!image || !file) {
      alert("Please select a PNG image and a file to hide.");
      return;
    }
    setLoading(true);
    setResultUrl("");
    const formData = new FormData();
    formData.append("image", image);
    formData.append("file", file);
    const response = await fetch("http://localhost:8000/image-file/encode/image-file", {
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
    if (!image) {
      alert("Please select a PNG image.");
      return;
    }
    setDecoding(true);
    setDecodedFileUrl("");
    const formData = new FormData();
    formData.append("image", image);
    const response = await fetch("http://localhost:8000/image-file/decode/image-file", {
      method: "POST",
      body: formData,
    });
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      setDecodedFileUrl(url);
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
        <input type="file" accept="image/png" onChange={handleImageChange} style={{
          marginBottom: 16,
          background: '#23243a',
          color: '#e3e6f3',
          border: 'none',
          fontSize: 16,
        }} />
        <input type="file" onChange={handleFileChange} style={{
          marginBottom: 16,
          background: '#23243a',
          color: '#e3e6f3',
          border: 'none',
          fontSize: 16,
        }} />
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
          {loading ? "Encoding..." : "Hide File in Image"}
        </button>
        {resultUrl && (
          <div style={{ marginTop: 8 }}>
            <a href={resultUrl} download="encoded_with_file.png" style={{ color: '#ffb300', fontWeight: 600 }}>
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
        <input type="file" accept="image/png" onChange={handleImageChange} style={{
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
          {decoding ? "Decoding..." : "Extract File from Image"}
        </button>
        {decodedFileUrl && (
          <div style={{ marginTop: 8 }}>
            <a href={decodedFileUrl} download style={{ color: '#ffb300', fontWeight: 600 }}>
              Download Extracted File
            </a>
          </div>
        )}
      </form>
    </div>
  );
};

export default FileInImageForm;
