import React from 'react';
import { motion } from 'framer-motion';
import './Skeleton.css';

const Skeleton = ({ width = '100%', height = '20px', variant = 'text', className = '' }) => {
  const variants = {
    text: 'skeleton--text',
    circular: 'skeleton--circular',
    rectangular: 'skeleton--rectangular',
  };

  const classNames = [
    'skeleton',
    variants[variant],
    className
  ].filter(Boolean).join(' ');

  return (
    <motion.div
      className={classNames}
      style={{ width, height }}
      animate={{
        opacity: [0.5, 1, 0.5],
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: 'easeInOut'
      }}
    />
  );
};

export default Skeleton;