import React from 'react';
import { motion } from 'framer-motion';
import './Card.css';

const Card = ({
  children,
  hover = false,
  padding = 'md',
  className = '',
  onClick,
  ...props
}) => {
  const classNames = [
    'ds-card',
    `ds-card--padding-${padding}`,
    hover && 'ds-card--hover',
    onClick && 'ds-card--clickable',
    className
  ].filter(Boolean).join(' ');

  const CardComponent = hover || onClick ? motion.div : 'div';
  const motionProps = hover || onClick ? {
    whileHover: { y: -4 },
    transition: {
      duration: 0.2,
      ease: [0.2, 0, 0, 1]
    }
  } : {};

  return (
    <CardComponent
      className={classNames}
      onClick={onClick}
      {...motionProps}
      {...props}
    >
      {children}
    </CardComponent>
  );
};

export default Card;