// Entry point for React application

import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import { CssBaseline, ThemeProvider as MuiThemeProvider } from '@mui/material';
import { ThemeProvider, useTheme } from './ThemeContext';
import { lightTheme, darkTheme } from './theme';
import '@xyflow/react/dist/style.css';

const ThemedApp: React.FC = () => {
  const { mode } = useTheme();
  return (
    <MuiThemeProvider theme={mode === 'light' ? lightTheme : darkTheme}>
      <CssBaseline />
      <App />
    </MuiThemeProvider>
  );
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <ThemedApp />
    </ThemeProvider>
  </React.StrictMode>
);
