import React from 'react';
import { motion } from 'framer-motion';
import type { CardProps } from '../../types';
import './Card.css';

interface ExtendedCardProps extends CardProps {
  hover?: boolean;
  onClick?: () => void;
}

const Card: React.FC<ExtendedCardProps> = ({
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

  const CardComponent = hover || onClick ? motion.div : 'div';
  const motionProps = hover || onClick ? {
    whileHover: { y: -4 },
    transition: {
      duration: 0.2,
      ease: [0.2, 0, 0, 1]
    }
  } : {};

  return React.createElement(
    CardComponent,
    {
      className: classNames,
      onClick,
      style,
      ...motionProps,
      ...props
    },
    children
  );
};

export default Card;
