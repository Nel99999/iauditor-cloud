import React from 'react';
import { motion } from 'framer-motion';
import type { CardProps } from '../../types';
import './Card.css';

const Card: React.FC<CardProps> = ({
  children,
  hover = false,
  padding = 'md',
  className = '',
  onClick,
  style,
  ...props
}) => {
  const classNames = [
    'ds-card',
    `ds-card--padding-${padding}`,
    hover && 'ds-card--hover',
    onClick && 'ds-card--clickable',
    className
  ].filter(Boolean).join(' ');

  if (hover || onClick) {
    return (
      <motion.div
        className={classNames}
        onClick={onClick}
        style={style}
        whileHover={{ y: -4 }}
        transition={{
          duration: 0.2,
          ease: [0.2, 0, 0, 1] as any
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

export default Card;
