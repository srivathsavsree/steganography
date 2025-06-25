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
    const file = e.target.files[0];
    
    if (file) {
      // Validate file type
      if (file.type !== 'image/png') {
        alert('Please select a PNG image. Other image formats are not supported.');
        e.target.value = ''; // Clear the file input
        return;
      }
      
      // Check file size (limit to 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('File size exceeds 5MB. Please select a smaller image.');
        e.target.value = ''; // Clear the file input
        return;
      }
      
      setImage(file);
      console.log("Image selected:", file.name, "Type:", file.type, "Size:", file.size);
    }
  };

  const handleDecodeImageChange = (e) => {
    const file = e.target.files[0];
    
    if (file) {
      // Validate file type
      if (file.type !== 'image/png') {
        alert('Please select a PNG image. Other image formats are not supported for decoding.');
        e.target.value = ''; // Clear the file input
        return;
      }
      
      setDecodeImage(file);
      console.log("Decode image selected:", file.name, "Type:", file.type, "Size:", file.size);
    }
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

    try {
      // Log the request details for debugging
      console.log("Encoding request to:", `${process.env.NEXT_PUBLIC_API_URL}/encode/image`);
      console.log("Encoding file:", image.name, "Type:", image.type, "Size:", image.size, "Message length:", message.length);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/encode/image`, {
        method: "POST",
        body: formData,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      console.log("Response status:", response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log("Encode response data:", data);
        
        if (data && data.url) {
          setResultUrl(data.url);
          
          // Auto-download the file
          try {
            const downloadResponse = await fetch(data.url);
            if (downloadResponse.ok) {
              const blob = await downloadResponse.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = 'encoded.png';
              document.body.appendChild(a);
              a.click();
              a.remove();
              window.URL.revokeObjectURL(url);
            } else {
              console.error("Failed to download encoded image");
            }
          } catch (downloadErr) {
            console.error("Error during auto-download:", downloadErr);
          }
        } else {
          console.warn("Invalid server response:", data);
          alert("Invalid response from server.");
        }
      } else {
        // Detailed error handling for non-OK responses
        console.error("Server returned error status:", response.status);
        
        try {
          const errorText = await response.text();
          console.error("Error response:", errorText);
          
          try {
            const errorData = JSON.parse(errorText);
            
            if (errorData && errorData.detail && errorData.detail.includes("Error uploading to S3")) {
              // If there's an S3 upload error, try the direct endpoint as fallback
              console.log("S3 upload failed, trying direct endpoint...");
              
              // Reset form data
              const directFormData = new FormData();
              directFormData.append("image", image);
              directFormData.append("message", message);
              
              try {
                const directResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/encode/image/direct`, {
                  method: "POST",
                  body: directFormData
                });
                
                if (directResponse.ok) {
                  console.log("Direct encoding successful");
                  
                  // Get the blob directly
                  const blob = await directResponse.blob();
                  const url = window.URL.createObjectURL(blob);
                  
                  setResultUrl(url);
                  
                  // Auto-download the file
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = 'encoded.png';
                  document.body.appendChild(a);
                  a.click();
                  a.remove();
                  window.URL.revokeObjectURL(url);
                  
                  return; // Exit the function after successful direct encoding
                } else {
                  console.error("Direct encoding also failed:", directResponse.status);
                }
              } catch (directErr) {
                console.error("Error with direct encoding:", directErr);
              }
            }
            
            if (errorData && errorData.detail) {
              alert(`Encoding failed: ${errorData.detail}`);
            } else {
              alert(`Encoding failed. Server status: ${response.status}`);
            }
          } catch (jsonErr) {
            console.error("Could not parse error response as JSON:", jsonErr);
            alert(`Encoding failed. Server status: ${response.status}\nResponse: ${errorText.substring(0, 100)}${errorText.length > 100 ? '...' : ''}`);
          }
        } catch (textErr) {
          console.error("Could not read error response text:", textErr);
          alert(`Encoding failed. Server status: ${response.status}`);
        }
      }
    } catch (err) {
      console.error("Encoding network error:", err);
      if (err.name === 'AbortError') {
        alert('Request timed out after 2 minutes. The image may be too large or the server is busy.');
      } else {
        alert(`Something went wrong while encoding: ${err.message}`);
      }
    }

    setLoading(false);
  };

  const handleDecode = async (e) => {
    e.preventDefault();
    if (!decodeImage) {
      alert("Please select a PNG image to decode.");
      return;
    }

    setDecoding(true);
    setDecodedMessage("");

    // Log file info for debugging
    console.log("Decoding file:", decodeImage.name, "Type:", decodeImage.type, "Size:", decodeImage.size);

    const formData = new FormData();
    formData.append("image", decodeImage);

    try {
      // Log the API URL
      console.log("API URL:", `${process.env.NEXT_PUBLIC_API_URL}/decode/image`);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 1 minute timeout
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/decode/image`, {
        method: "POST",
        body: formData,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      console.log("Response status:", response.status);
      
      if (response.ok) {
        try {
          const data = await response.json();
          console.log("Decode response data:", data);
          
          if (data && data.message) {
            setDecodedMessage(data.message);
          } else {
            console.warn("No message found in response:", data);
            alert("No message found in the image.");
          }
        } catch (jsonErr) {
          console.error("Error parsing response JSON:", jsonErr);
          alert("Error parsing server response.");
        }
      } else {
        console.error("Server returned error status:", response.status);
        
        try {
          const errorText = await response.text();
          console.error("Error response:", errorText);
          
          try {
            const errorData = JSON.parse(errorText);
            if (errorData && errorData.detail) {
              alert(`Decoding failed: ${errorData.detail}`);
            } else {
              alert(`Decoding failed. Server status: ${response.status}`);
            }
          } catch (jsonErr) {
            console.error("Could not parse error response as JSON:", jsonErr);
            alert(`Decoding failed. Server status: ${response.status}`);
          }
        } catch (textErr) {
          console.error("Could not read error response text:", textErr);
          alert(`Decoding failed. Server status: ${response.status}`);
        }
      }
    } catch (err) {
      console.error("Decoding network error:", err);
      if (err.name === 'AbortError') {
        alert('Request timed out after 1 minute. The image may be too large or the server is busy.');
      } else {
        alert(`Something went wrong while decoding: ${err.message}`);
      }
    }

    setDecoding(false);
  };

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
    <>
      <div className="steg-form">
        <div className="steg-section-title">Hide Message in Image</div>
        <form onSubmit={handleSubmit}>
          <label>Upload PNG Image <span className="steg-required">*</span></label>
          <input type="file" accept="image/png" onChange={handleImageChange} className="steg-file-input" required />
          {image && (
            <div className="steg-file-info">
              Selected: {image.name} ({(image.size / 1024).toFixed(2)} KB)
            </div>
          )}

          <label>Message to Hide <span className="steg-required">*</span></label>
          <input
            type="text"
            placeholder="Enter your secret message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="steg-input"
            required
          />
          {message && (
            <div className="steg-message-info">
              Message length: {message.length} characters
            </div>
          )}

          <button type="submit" disabled={loading} className="steg-btn">
            {loading ? (
              <>
                <span className="steg-loading-spinner"></span>
                Encoding...
              </>
            ) : (
              "Encode Image"
            )}
          </button>

          {resultUrl && (
            <div className="steg-result">
              <div className="steg-success">Encoding successful!</div>
              <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <a href={resultUrl} target="_blank" rel="noopener noreferrer" className="steg-result-link">
                  View Encoded Image
                </a>
                <button type="button" onClick={handleDownload} className="steg-btn">
                  Download Again
                </button>
              </div>
            </div>
          )}
        </form>
      </div>

      <div className="steg-form">
        <div className="steg-section-title">Decode Hidden Message</div>
        <form onSubmit={handleDecode}>
          <label>Upload Encoded PNG Image <span className="steg-required">*</span></label>
          <input type="file" accept="image/png" onChange={handleDecodeImageChange} className="steg-file-input" required />
          {decodeImage && (
            <div className="steg-file-info">
              Selected: {decodeImage.name} ({(decodeImage.size / 1024).toFixed(2)} KB)
            </div>
          )}

          <button type="submit" disabled={decoding} className="steg-btn">
            {decoding ? (
              <>
                <span className="steg-loading-spinner"></span>
                Decoding...
              </>
            ) : (
              "Decode Image"
            )}
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

export default EncodeForm;
