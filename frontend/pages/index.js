import React, { useState } from 'react'; 
import EncodeForm from '../components/EncodeForm';
import AudioForm from '../components/AudioForm';
import FileInImageForm from '../components/FileInImageForm';
import VideoForm from '../components/VideoForm';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState('image');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'image':
        return <EncodeForm />;
      case 'audio':
        return <AudioForm />;
      case 'file':
        return <FileInImageForm />;
      case 'video':
        return <VideoForm />;
      default:
        return null;
    }
  };

  return (
    <main>
      <h1>Steganography Web App</h1>

      <div className="tab-container">
        <button
          className={`tab-button ${activeTab === 'image' ? 'active' : ''}`}
          onClick={() => setActiveTab('image')}
        >
          Image Steganography
        </button>
        <button
          className={`tab-button ${activeTab === 'audio' ? 'active' : ''}`}
          onClick={() => setActiveTab('audio')}
        >
          Audio Steganography
        </button>
        <button
          className={`tab-button ${activeTab === 'file' ? 'active' : ''}`}
          onClick={() => setActiveTab('file')}
        >
          File-in-Image Steganography
        </button>
        <button
          className={`tab-button ${activeTab === 'video' ? 'active' : ''}`}
          onClick={() => setActiveTab('video')}
        >
          Video Steganography
        </button>
      </div>

      <div className="content-container">
        {renderTabContent()}
      </div>
    </main>
  );
}
