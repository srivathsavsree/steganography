// pages/_app.js
import '../styles/global.css'; // ✅ move here
import React from 'react';

export default function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />;
}
