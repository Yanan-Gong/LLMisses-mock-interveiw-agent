// src/index.tsx or src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import './index.css'; // Import the CSS file here
import App from './App';
import { BrowserRouter } from 'react-router-dom';


ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
  document.getElementById('root')
);