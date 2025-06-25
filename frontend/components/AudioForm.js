import React, { useState } from "react";

const AudioForm = () => {
  const [audio, setAudio] = useState(null);
  const [message, setMessage] = useState("");
  const [resultUrl, setResultUrl] = useState("");
  const [decoded, setDecoded] = useState("");
  const [loading, setLoading] = useState(false);
  const [decoding, setDecoding] = useState(false);

  // Helper function to handle direct file responses
  const handleDirectFileResponse = async (response) => {
    try {
      console.log("Handling direct file response");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      setResultUrl(url);
      
      // Auto-download the file
      const a = document.createElement('a');
      a.href = url;
      a.download = 'encoded.wav';
      document.body.appendChild(a);
      a.click();
      a.remove();
      // Don't revoke URL as we need it for display
      
      console.log("Direct file processed successfully");
    } catch (error) {
      console.error("Error handling direct file response:", error);
      alert("Error processing the encoded audio");
    }
  };
  
  // Helper function to try the direct endpoint
  const tryDirectEndpoint = async () => {
    console.log("Trying direct endpoint...");
    
    // Reset form data
    const directFormData = new FormData();
    directFormData.append("audio", audio);
    directFormData.append("message", message);
    
    try {
      const directResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/audio/encode/direct`, {
        method: "POST",
        body: directFormData
      });
      
      if (directResponse.ok) {
        console.log("Direct encoding successful");
        await handleDirectFileResponse(directResponse);
        return true;
      } else {
        console.error("Direct encoding failed:", directResponse.status);
        return false;
      }
    } catch (directErr) {
      console.error("Error with direct encoding:", directErr);
      return false;
    }
  };

  const handleAudioChange = (e) => {
    const file = e.target.files[0];
    
    if (file) {
      // Validate file type
      if (!file.type.includes("audio/")) {
        alert('Please select an audio file. Other file types are not supported.');
        e.target.value = ''; // Clear the file input
        return;
      }
      
      // Check file size (limit to 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size exceeds 10MB. Please select a smaller audio file.');
        e.target.value = ''; // Clear the file input
        return;
      }
      
      setAudio(file);
      console.log("Audio selected:", file.name, "Type:", file.type, "Size:", file.size);
    }
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
    
    try {
      // Log the request details for debugging
      console.log("Encoding request to:", `${process.env.NEXT_PUBLIC_API_URL}/audio/encode`);
      console.log("Encoding file:", audio.name, "Type:", audio.type, "Size:", audio.size, "Message length:", message.length);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/audio/encode`, {
        method: "POST",
        body: formData,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      console.log("Response status:", response.status);
      
      if (response.ok) {
        // Check the content type of the response
        const contentType = response.headers.get("content-type");
        console.log("Response content type:", contentType);
        
        if (contentType && contentType.includes("application/json")) {
          // Handle JSON response (S3 URL)
          try {
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
                  a.download = 'encoded.wav';
                  document.body.appendChild(a);
                  a.click();
                  a.remove();
                  window.URL.revokeObjectURL(url);
                } else {
                  console.error("Failed to download encoded audio");
                }
              } catch (downloadErr) {
                console.error("Error during auto-download:", downloadErr);
              }
            } else {
              console.warn("Invalid server response:", data);
              alert("Invalid response from server.");
            }
          } catch (jsonErr) {
            console.error("Error parsing JSON response:", jsonErr);
            // The response might actually be a direct file despite the content-type
            await handleDirectFileResponse(response);
          }
        } else {
          // Handle direct file response (WAV data)
          console.log("Received direct file response");
          await handleDirectFileResponse(response);
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
              
              const directSuccess = await tryDirectEndpoint();
              
              if (!directSuccess) {
                alert("Encoding failed. Please try again later.");
              }
            } else if (errorData && errorData.detail) {
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
        alert('Request timed out after 2 minutes. The audio may be too large or the server is busy.');
      } else {
        alert(`Something went wrong while encoding: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
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
    
    try {
      console.log("Decoding request to:", `${process.env.NEXT_PUBLIC_API_URL}/audio/decode`);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 1 minute timeout
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/audio/decode`, {
        method: "POST",
        body: formData,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        try {
          const data = await response.json();
          if (data && data.message) {
            setDecoded(data.message);
          } else {
            alert("No message found in the audio.");
          }
        } catch (jsonErr) {
          console.error("Error parsing response JSON:", jsonErr);
          alert("Error parsing server response.");
        }
      } else {
        console.error("Server returned error status:", response.status);
        try {
          const errorText = await response.text();
          try {
            const errorData = JSON.parse(errorText);
            if (errorData && errorData.detail) {
              alert(`Decoding failed: ${errorData.detail}`);
            } else {
              alert(`Decoding failed. Server status: ${response.status}`);
            }
          } catch (jsonErr) {
            alert(`Decoding failed. Server status: ${response.status}`);
          }
        } catch (textErr) {
          alert(`Decoding failed. Server status: ${response.status}`);
        }
      }
    } catch (err) {
      console.error("Decoding error:", err);
      if (err.name === 'AbortError') {
        alert('Request timed out after 1 minute. The audio may be too large or the server is busy.');
      } else {
        alert(`Something went wrong while decoding: ${err.message}`);
      }
    } finally {
      setDecoding(false);
    }
  };

  return (
    <>
      <div className="steg-form">
        <div className="steg-section-title">Hide Message in Audio</div>
        <form onSubmit={handleEncode}>
          <label>Upload Audio File</label>
          <input type="file" accept="audio/wav,audio/mp3" onChange={handleAudioChange} className="steg-file-input" />
          
          <label>Message to Hide</label>
          <textarea 
            value={message} 
            onChange={(e) => setMessage(e.target.value)} 
            placeholder="Enter your secret message"
            className="steg-textarea"
          />
          
          <button type="submit" disabled={loading} className="steg-btn">
            {loading ? "Encoding..." : "Hide Message in Audio"}
          </button>
          
          {resultUrl && (
            <div style={{ marginTop: '1rem' }}>
              <a href={resultUrl} download="encoded.wav" className="steg-result-link">
                Download Encoded Audio
              </a>
            </div>
          )}
        </form>
      </div>
      
      <div className="steg-form">
        <div className="steg-section-title">Decode Hidden Message</div>
        <form onSubmit={handleDecode}>
          <label>Upload Encoded Audio</label>
          <input type="file" accept="audio/wav,audio/mp3" onChange={handleAudioChange} className="steg-file-input" />
          
          <button type="submit" disabled={decoding} className="steg-btn">
            {decoding ? "Decoding..." : "Extract Hidden Message"}
          </button>
          
          {decoded && (
            <div style={{ marginTop: '1rem' }} className="steg-result">
              <h4>Decoded Message:</h4>
              <div className="steg-decoded-message">{decoded}</div>
            </div>
          )}
        </form>
      </div>
    </>
  );
};

export default AudioForm;
