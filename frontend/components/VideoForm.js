import React, { useState } from "react";

const VideoForm = () => {
  const [video, setVideo] = useState(null);
  const [message, setMessage] = useState("");
  const [resultUrl, setResultUrl] = useState("");
  const [decodedMessage, setDecodedMessage] = useState("");
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
      a.download = 'encoded_video.mp4';
      document.body.appendChild(a);
      a.click();
      a.remove();
      // Don't revoke URL as we need it for display
      
      console.log("Direct file processed successfully");
    } catch (error) {
      console.error("Error handling direct file response:", error);
      alert("Error processing the encoded video");
    }
  };
  
  // Helper function to try the direct endpoint
  const tryDirectEndpoint = async () => {
    console.log("Trying direct endpoint...");
    
    // Reset form data
    const directFormData = new FormData();
    directFormData.append("video", video);
    directFormData.append("message", message);
    
    try {
      const directResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/video/encode/direct`, {
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

  const handleVideoChange = (e) => {
    const file = e.target.files[0];
    
    if (file) {
      // Validate file type
      if (!file.type.startsWith('video/')) {
        alert('Please select a video file. Other file types are not supported.');
        e.target.value = ''; // Clear the file input
        return;
      }
      
      // Check file size (limit to 50MB)
      if (file.size > 50 * 1024 * 1024) {
        alert('File size exceeds 50MB. Please select a smaller video file.');
        e.target.value = ''; // Clear the file input
        return;
      }
      
      setVideo(file);
      console.log("Video selected:", file.name, "Type:", file.type, "Size:", file.size);
    }
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
    
    try {
      // Log the request details for debugging
      console.log("Encoding request to:", `${process.env.NEXT_PUBLIC_API_URL}/video/encode`);
      console.log("Encoding file:", video.name, "Type:", video.type, "Size:", video.size, "Message length:", message.length);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 180000); // 3 minute timeout for video (longer for large files)
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/video/encode`, {
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
                  a.download = 'encoded_video.mp4';
                  document.body.appendChild(a);
                  a.click();
                  a.remove();
                  window.URL.revokeObjectURL(url);
                } else {
                  console.error("Failed to download encoded video");
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
          // Handle direct file response (video data)
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
        alert('Request timed out after 3 minutes. The video may be too large or the server is busy.');
      } else {
        alert(`Something went wrong while encoding: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
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
    
    try {
      // Log the request details for debugging
      console.log("Decoding request to:", `${process.env.NEXT_PUBLIC_API_URL}/video/decode`);
      console.log("Decoding video:", video.name, "Type:", video.type, "Size:", video.size);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/video/decode`, {
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
            alert("No message found in the video.");
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
        alert('Request timed out after 2 minutes. The video may be too large or the server is busy.');
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
