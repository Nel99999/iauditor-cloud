import React from 'react';
import { motion } from 'framer-motion';
import './Spinner.css';

type SpinnerSize = 'sm' | 'md' | 'lg' | 'xl';
type SpinnerColor = 'primary' | 'accent' | 'white';

interface SpinnerProps {
  size?: SpinnerSize;
  color?: SpinnerColor;
  className?: string;
}

const Spinner: React.FC<SpinnerProps> = ({ size = 'md', color = 'primary', className = '' }) => {
  const sizes: Record<SpinnerSize, number> = {
    sm: 16,
    md: 32,
    lg: 48,
    xl: 64,
  };

  const colors: Record<SpinnerColor, string> = {
    primary: 'var(--color-brand-primary)',
    accent: 'var(--color-brand-accent)',
    white: 'var(--color-brand-primary-contrast)',
  };

  const spinnerSize = sizes[size];
  const spinnerColor = colors[color];

  return (
    <div className={`spinner-container ${className}`}>
      <motion.svg
        width={spinnerSize}
        height={spinnerSize}
        viewBox="0 0 50 50"
        className="spinner"
        animate={{ rotate: 360 }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: 'linear'
        }}
      >
        <motion.circle
          cx="25"
          cy="25"
          r="20"
          fill="none"
          stroke={spinnerColor}
          strokeWidth="4"
          strokeLinecap="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: [0, 0.8, 0] }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
        />
      </motion.svg>
    </div>
  );
};

export default Spinner;
