import React from 'react';
import { Button, GlassCard } from '@/design-system/components';
import { useTheme } from '@/contexts/ThemeContext';
import { Sun, Moon, Laptop } from 'lucide-react';
import { motion } from 'framer-motion';
import './ThemeShowcase.css';

const ThemeShowcase = () => {
  const { theme, setTheme } = useTheme();

  return (
    <div className="theme-showcase">
      <div className="theme-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
      </div>

      <div className="theme-container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="theme-header"
        >
          <h1 className="theme-title">Theme Settings</h1>
          <p className="theme-subtitle">
            Choose your preferred color scheme. Dark mode reduces eye strain in low-light conditions.
          </p>
        </motion.div>

        <div className="theme-options">
          {/* Light Theme */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <GlassCard
              hover
              onClick={() => setTheme('light')}
              className={`theme-card ${theme === 'light' ? 'theme-card--active' : ''}`}
            >
              <div className="theme-preview theme-preview--light">
                <div className="preview-header"></div>
                <div className="preview-sidebar"></div>
                <div className="preview-content">
                  <div className="preview-card"></div>
                  <div className="preview-card"></div>
                </div>
              </div>
              <div className="theme-info">
                <Sun size={24} className="theme-icon" />
                <div>
                  <h3 className="theme-name">Light Mode</h3>
                  <p className="theme-desc">Clean and bright interface</p>
                </div>
              </div>
              {theme === 'light' && (
                <motion.div
                  className="active-badge"
                  layoutId="activeBadge"
                  transition={{ duration: 0.3 }}
                >
                  Active
                </motion.div>
              )}
            </GlassCard>
          </motion.div>

          {/* Dark Theme */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <GlassCard
              hover
              onClick={() => setTheme('dark')}
              className={`theme-card ${theme === 'dark' ? 'theme-card--active' : ''}`}
            >
              <div className="theme-preview theme-preview--dark">
                <div className="preview-header"></div>
                <div className="preview-sidebar"></div>
                <div className="preview-content">
                  <div className="preview-card"></div>
                  <div className="preview-card"></div>
                </div>
              </div>
              <div className="theme-info">
                <Moon size={24} className="theme-icon" />
                <div>
                  <h3 className="theme-name">Dark Mode</h3>
                  <p className="theme-desc">Reduces eye strain at night</p>
                </div>
              </div>
              {theme === 'dark' && (
                <motion.div
                  className="active-badge"
                  layoutId="activeBadge"
                  transition={{ duration: 0.3 }}
                >
                  Active
                </motion.div>
              )}
            </GlassCard>
          </motion.div>
        </div>

        {/* Current Theme Demo */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <GlassCard padding="lg" className="demo-section">
            <h2 className="section-title">Preview Current Theme</h2>
            <div className="demo-content">
              <div className="demo-cards">
                <GlassCard padding="md" className="demo-card">
                  <h4 className="demo-card-title">Card Title</h4>
                  <p className="demo-card-text">
                    This is how cards look in the current theme. Notice the colors and contrast.
                  </p>
                  <Button variant="primary" size="sm">Action</Button>
                </GlassCard>
                <GlassCard padding="md" className="demo-card">
                  <h4 className="demo-card-title">Another Card</h4>
                  <p className="demo-card-text">
                    The glassmorphism effect adapts beautifully to both themes.
                  </p>
                  <Button variant="accent" size="sm">Action</Button>
                </GlassCard>
              </div>
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </div>
  );
};

export default ThemeShowcase;
