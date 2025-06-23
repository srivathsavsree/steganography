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
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/image-file/encode/image-file`, {
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
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/image-file/decode/image-file`, {
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
      <div className="steg-section-title">File-in-Image Steganography</div>
      <form onSubmit={handleEncode} className="steg-form">
        <label>Upload PNG Image</label>
        <input type="file" accept="image/png" onChange={handleImageChange} className="steg-file-input" />
        <label>File to Hide</label>
        <input type="file" onChange={handleFileChange} className="steg-file-input" />
        <button type="submit" disabled={loading} className="steg-btn">{loading ? "Encoding..." : "Hide File in Image"}</button>
        {resultUrl && (
          <div style={{ marginTop: 8 }}>
            <a href={resultUrl} download="encoded_with_file.png" className="steg-result-link">Download Encoded Image</a>
          </div>
        )}
      </form>
      <form onSubmit={handleDecode} className="steg-form">
        <label>Decode PNG Image</label>
        <input type="file" accept="image/png" onChange={handleImageChange} className="steg-file-input" />
        <button type="submit" disabled={decoding} className="steg-btn">{decoding ? "Decoding..." : "Extract File from Image"}</button>
        {decodedFileUrl && (
          <div style={{ marginTop: 8 }}>
            <a href={decodedFileUrl} download className="steg-result-link">Download Extracted File</a>
          </div>
        )}
      </form>
    </div>
  );
};

export default FileInImageForm;
