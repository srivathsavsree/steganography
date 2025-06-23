import React, { useState } from 'react';
import EncodeForm from '../components/EncodeForm';
import AudioForm from '../components/AudioForm';
import FileInImageForm from '../components/FileInImageForm';

const tabList = [
  { label: 'Image Steganography', value: 'image' },
  { label: 'Audio Steganography', value: 'audio' },
  { label: 'File-in-Image Steganography', value: 'fileinimage' },
  { label: 'Video Steganography', value: 'video' },
];

export default function Home() {
  const [tab, setTab] = useState('image');

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #23243a 0%, #1a1b2e 100%)',
      padding: 0,
      margin: 0,
      width: '100vw',
      boxSizing: 'border-box',
      overflowX: 'hidden',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <div style={{
        maxWidth: 700,
        minHeight: 500,
        width: '95vw',
        margin: '40px auto',
        padding: 32,
        background: 'rgba(30, 32, 60, 0.98)',
        borderRadius: 18,
        boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.25)',
        fontFamily: 'Segoe UI, Arial, sans-serif',
        border: '1px solid #23243a',
        position: 'relative',
        color: '#e3e6f3',
        boxSizing: 'border-box',
      }}>
        <h1 style={{
          fontSize: 38,
          fontWeight: 800,
          marginBottom: 32,
          color: '#fff',
          letterSpacing: '-1px',
          textAlign: 'center',
          fontFamily: 'Segoe UI, Arial, sans-serif',
        }}>
          Steganography Web App
        </h1>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 32, gap: 0 }}>
          {tabList.map((t, idx) => (
            <button
              key={t.value}
              onClick={() => setTab(t.value)}
              style={{
                background: tab === t.value
                  ? 'linear-gradient(90deg, #5c6bc0 0%, #3949ab 100%)'
                  : 'rgba(44, 47, 80, 0.7)',
                color: tab === t.value ? '#fff' : '#b0b3c7',
                border: 'none',
                borderBottom: tab === t.value ? '3px solid #ffb300' : '3px solid transparent',
                fontWeight: 700,
                fontSize: 18,
                padding: '14px 36px',
                borderRadius: idx === 0
                  ? '14px 0 0 0'
                  : idx === tabList.length - 1
                  ? '0 14px 0 0'
                  : '0',
                margin: 0,
                cursor: 'pointer',
                transition: 'all 0.2s',
                outline: 'none',
                boxShadow: tab === t.value ? '0 2px 12px 0 rgba(92,107,192,0.18)' : 'none',
                minWidth: 200,
                letterSpacing: '0.5px',
                textShadow: tab === t.value ? '0 2px 8px #28359344' : 'none',
                fontFamily: 'inherit',
              }}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div style={{ minHeight: 260, display: 'flex', alignItems: 'flex-start', justifyContent: 'center', width: '100%' }}>
          {tab === 'image' && (
            <section style={{ width: '100%' }}>
              <EncodeForm />
            </section>
          )}
        </div>
        <div style={{ minHeight: 260, display: 'flex', alignItems: 'flex-start', justifyContent: 'center', width: '100%' }}>
          {tab === 'audio' && (
            <section style={{ width: '100%' }}>
              <AudioForm />
            </section>
          )}
        </div>
        <div style={{ minHeight: 260, display: 'flex', alignItems: 'flex-start', justifyContent: 'center', width: '100%' }}>
          {tab === 'fileinimage' && (
            <section style={{ width: '100%' }}>
              <FileInImageForm />
            </section>
          )}
        </div>
        <div style={{ minHeight: 260, display: 'flex', alignItems: 'flex-start', justifyContent: 'center', width: '100%' }}>
          {tab === 'video' && (
            <section style={{ width: '100%', color: '#b0b3c7', textAlign: 'center', fontSize: 20, fontWeight: 500 }}>
              <div style={{ padding: 40 }}>
                Video steganography coming soon...
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
