import React, { useState } from "react";

const FileInImageForm = () => {
  const [image, setImage] = useState(null);
  const [file, setFile] = useState(null);
  const [resultUrl, setResultUrl] = useState("");
  const [decodedFileUrl, setDecodedFileUrl] = useState("");
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
      a.download = 'encoded_with_file.png';
      document.body.appendChild(a);
      a.click();
      a.remove();
      // Don't revoke URL as we need it for display
      
      console.log("Direct file processed successfully");
    } catch (error) {
      console.error("Error handling direct file response:", error);
      alert("Error processing the encoded image");
    }
  };
  
  // Helper function to try the direct endpoint
  const tryDirectEndpoint = async () => {
    console.log("Trying direct endpoint...");
    
    // Reset form data
    const directFormData = new FormData();
    directFormData.append("image", image);
    directFormData.append("file", file);
    
    try {
      const directResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/image-file/encode/direct`, {
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

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    
    if (file) {
      // Validate file type for image
      if (file.type !== 'image/png') {
        alert('Please select a PNG image. Other image formats are not supported.');
        e.target.value = ''; // Clear the file input
        return;
      }
      
      setImage(file);
      console.log("Image selected:", file.name, "Type:", file.type, "Size:", file.size);
    }
  };
  
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    
    if (selectedFile) {
      // Check file size (limit to 5MB)
      if (selectedFile.size > 5 * 1024 * 1024) {
        alert('File size exceeds 5MB. Please select a smaller file to hide.');
        e.target.value = ''; // Clear the file input
        return;
      }
      
      setFile(selectedFile);
      console.log("File selected:", selectedFile.name, "Type:", selectedFile.type, "Size:", selectedFile.size);
    }
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
    
    try {
      // Log the request details for debugging
      console.log("Encoding request to:", `${process.env.NEXT_PUBLIC_API_URL}/image-file/encode`);
      console.log("Encoding image:", image.name, "Type:", image.type, "Size:", image.size);
      console.log("File to hide:", file.name, "Type:", file.type, "Size:", file.size);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/image-file/encode`, {
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
                  a.download = 'encoded_with_file.png';
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
          } catch (jsonErr) {
            console.error("Error parsing JSON response:", jsonErr);
            // The response might actually be a direct file despite the content-type
            await handleDirectFileResponse(response);
          }
        } else {
          // Handle direct file response (PNG data)
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
        alert('Request timed out after 2 minutes. The image or file may be too large or the server is busy.');
      } else {
        alert(`Something went wrong while encoding: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
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
    
    try {
      // Log the request details for debugging
      console.log("Decoding request to:", `${process.env.NEXT_PUBLIC_API_URL}/image-file/decode`);
      console.log("Decoding image:", image.name, "Type:", image.type, "Size:", image.size);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 1 minute timeout
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/image-file/decode`, {
        method: "POST",
        body: formData,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      console.log("Response status:", response.status);
      
      if (response.ok) {
        try {
          // For file-in-image, we always expect a binary file back
          const contentDisposition = response.headers.get('content-disposition');
          const filename = contentDisposition ? 
            contentDisposition.split('filename=')[1].replace(/"/g, '') : 
            'extracted_file';
          
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          setDecodedFileUrl(url);
          
          // Auto-download the file
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          a.remove();
          // Don't revoke URL as we need it for display
          
          console.log("Successfully extracted and downloaded file:", filename);
        } catch (blobErr) {
          console.error("Error processing the extracted file:", blobErr);
          alert("Error processing the extracted file.");
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
    } finally {
      setDecoding(false);
    }
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
