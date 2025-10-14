import React from 'react';
import { motion } from 'framer-motion';
import type { ButtonProps } from '../../types';
import './Button.css';

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  children,
  onClick,
  className = '',
  icon = null,
  type = 'button',
  fullWidth = false,
  ...props
}) => {
  const classNames = [
    'ds-button',
    `ds-button--${variant}`,
    `ds-button--${size}`,
    loading && 'ds-button--loading',
    disabled && 'ds-button--disabled',
    fullWidth && 'ds-button--full-width',
    className
  ].filter(Boolean).join(' ');

  return (
    <motion.button
      className={classNames}
      onClick={disabled || loading ? undefined : onClick}
      disabled={disabled || loading}
      type={type}
      whileHover={!disabled && !loading ? { scale: 1.02, y: -2 } : {}}
      whileTap={!disabled && !loading ? { scale: 0.98 } : {}}
      transition={{
        duration: 0.2,
        ease: [0.2, 0, 0, 1]
      }}
      {...props}
    >
      {loading && (
        <div className="ds-button__spinner" />
      )}
      {icon && !loading && (
        <span className="ds-button__icon">{icon}</span>
      )}
      {children}
    </motion.button>
  );
};

export default Button;
