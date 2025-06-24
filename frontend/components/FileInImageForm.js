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
    setResultUrl("");    const formData = new FormData();
    formData.append("image", image);
    formData.append("file", file);
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/image-file/encode`, {
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
    setDecodedFileUrl("");    const formData = new FormData();
    formData.append("image", image);
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/image-file/decode`, {
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
    <>
      <div className="steg-form">
        <div className="steg-section-title">Hide File in Image</div>
        <form onSubmit={handleEncode}>
          <label>Upload PNG Image</label>
          <input type="file" accept="image/png" onChange={handleImageChange} className="steg-file-input" />
          
          <label>File to Hide</label>
          <input type="file" onChange={handleFileChange} className="steg-file-input" />
          
          <button type="submit" disabled={loading} className="steg-btn">
            {loading ? "Encoding..." : "Hide File in Image"}
          </button>
          
          {resultUrl && (
            <div style={{ marginTop: '1rem' }}>
              <a href={resultUrl} download="encoded_with_file.png" className="steg-result-link">
                Download Encoded Image
              </a>
            </div>
          )}
        </form>
      </div>
      
      <div className="steg-form">
        <div className="steg-section-title">Extract Hidden File</div>
        <form onSubmit={handleDecode}>
          <label>Upload Encoded PNG Image</label>
          <input type="file" accept="image/png" onChange={handleImageChange} className="steg-file-input" />
          
          <button type="submit" disabled={decoding} className="steg-btn">
            {decoding ? "Extracting..." : "Extract File from Image"}
          </button>
          
          {decodedFileUrl && (
            <div style={{ marginTop: '1rem' }}>
              <a href={decodedFileUrl} download className="steg-result-link">
                Download Extracted File
              </a>
            </div>
          )}
        </form>
      </div>
    </>
  );
};

export default FileInImageForm;
