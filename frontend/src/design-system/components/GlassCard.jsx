import React from 'react';
import { motion } from 'framer-motion';
import './GlassCard.css';

const GlassCard = ({
  children,
  hover = true,
  padding = 'md',
  className = '',
  onClick,
  ...props
}) => {
  const classNames = [
    'ds-glass-card',
    `ds-glass-card--padding-${padding}`,
    hover && 'ds-glass-card--hover',
    onClick && 'ds-glass-card--clickable',
    className
  ].filter(Boolean).join(' ');

  const GlassComponent = hover || onClick ? motion.div : 'div';
  const motionProps = hover || onClick ? {
    whileHover: { y: -6, scale: 1.01 },
    transition: {
      duration: 0.3,
      ease: [0.34, 1.56, 0.64, 1] // Spring easing
    }
  } : {};

  return (
    <GlassComponent
      className={classNames}
      onClick={onClick}
      {...motionProps}
      {...props}
    >
      {children}
    </GlassComponent>
  );
};

export default GlassCard;