// Entry point for React application

import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import { CssBaseline } from '@mui/material';
import '@xyflow/react/dist/style.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <CssBaseline />
    <App />
  </React.StrictMode>
);
