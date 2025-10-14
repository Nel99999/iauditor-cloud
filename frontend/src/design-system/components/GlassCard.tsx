import React from 'react';
import { motion } from 'framer-motion';
import type { GlassCardProps } from '../../types';
import './GlassCard.css';

const GlassCard: React.FC<GlassCardProps> = ({
  children,
  hover = true,
  blur = 'md',
  padding = 'md',
  className = '',
  onClick,
  style,
  ...props
}) => {
  const classNames = [
    'ds-glass-card',
    `ds-glass-card--padding-${padding}`,
    `ds-glass-card--blur-${blur}`,
    hover && 'ds-glass-card--hover',
    onClick && 'ds-glass-card--clickable',
    className
  ].filter(Boolean).join(' ');

  if (hover || onClick) {
    return (
      <motion.div
        className={classNames}
        onClick={onClick}
        style={style}
        whileHover={{ y: -6, scale: 1.01 }}
        transition={{
          duration: 0.3,
          ease: [0.34, 1.56, 0.64, 1] as any // Spring easing
        }}
        {...props}
      >
        {children}
      </motion.div>
    );
  }

  return (
    <div
      className={classNames}
      onClick={onClick}
      style={style}
      {...props}
    >
      {children}
    </div>
  );
};

export default GlassCard;
