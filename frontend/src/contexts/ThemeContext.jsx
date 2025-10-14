import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const ThemeContext = createContext(null);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');
  const [accentColor, setAccentColor] = useState('#6366f1');
  const [viewDensity, setViewDensity] = useState('comfortable');
  const [fontSize, setFontSize] = useState('medium');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load theme from localStorage first for instant apply
    const savedTheme = localStorage.getItem('theme') || 'light';
    const savedAccent = localStorage.getItem('accentColor') || '#6366f1';
    const savedDensity = localStorage.getItem('viewDensity') || 'comfortable';
    const savedFontSize = localStorage.getItem('fontSize') || 'medium';
    
    setTheme(savedTheme);
    setAccentColor(savedAccent);
    setViewDensity(savedDensity);
    setFontSize(savedFontSize);
    applyTheme(savedTheme, savedAccent, savedDensity, savedFontSize);
    setLoading(false);

    // Then sync with backend
    loadThemeFromBackend();
  }, []);

  const loadThemeFromBackend = async () => {
    try {
      const response = await axios.get(`${API}/users/theme`);
      if (response.data) {
        const { theme: t, accent_color, view_density, font_size } = response.data;
        if (t) {
          setTheme(t);
          localStorage.setItem('theme', t);
        }
        if (accent_color) {
          setAccentColor(accent_color);
          localStorage.setItem('accentColor', accent_color);
        }
        if (view_density) {
          setViewDensity(view_density);
          localStorage.setItem('viewDensity', view_density);
        }
        if (font_size) {
          setFontSize(font_size);
          localStorage.setItem('fontSize', font_size);
        }
        applyTheme(t || theme, accent_color || accentColor, view_density || viewDensity, font_size || fontSize);
      }
    } catch (err) {
      console.log('Theme not loaded from backend, using local settings');
    }
  };

  const applyTheme = (newTheme, newAccent, newDensity, newFontSize) => {
    // Apply dark mode using data-theme attribute for token system
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // Also keep the dark class for Tailwind compatibility
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }

    // Apply accent color
    document.documentElement.style.setProperty('--accent-color', newAccent);

    // Apply view density
    const densityClasses = ['compact', 'comfortable', 'spacious'];
    densityClasses.forEach(d => document.body.classList.remove(`density-${d}`));
    document.body.classList.add(`density-${newDensity}`);

    // Apply font size
    const fontClasses = ['small', 'medium', 'large'];
    fontClasses.forEach(f => document.body.classList.remove(`font-${f}`));
    document.body.classList.add(`font-${newFontSize}`);
  };

  const toggleTheme = async () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme, accentColor, viewDensity, fontSize);
    
    // Save to backend
    try {
      await axios.put(`${API}/users/theme`, { theme: newTheme });
    } catch (err) {
      console.error('Failed to save theme:', err);
    }
  };

  const updateAccentColor = async (color) => {
    setAccentColor(color);
    localStorage.setItem('accentColor', color);
    applyTheme(theme, color, viewDensity, fontSize);
    
    try {
      await axios.put(`${API}/users/theme`, { accent_color: color });
    } catch (err) {
      console.error('Failed to save accent color:', err);
    }
  };

  const updateViewDensity = async (density) => {
    setViewDensity(density);
    localStorage.setItem('viewDensity', density);
    applyTheme(theme, accentColor, density, fontSize);
    
    try {
      await axios.put(`${API}/users/theme`, { view_density: density });
    } catch (err) {
      console.error('Failed to save view density:', err);
    }
  };

  const updateFontSize = async (size) => {
    setFontSize(size);
    localStorage.setItem('fontSize', size);
    applyTheme(theme, accentColor, viewDensity, size);
    
    try {
      await axios.put(`${API}/users/theme`, { font_size: size });
    } catch (err) {
      console.error('Failed to save font size:', err);
    }
  };

  const value = {
    theme,
    accentColor,
    viewDensity,
    fontSize,
    loading,
    toggleTheme,
    updateAccentColor,
    updateViewDensity,
    updateFontSize,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
