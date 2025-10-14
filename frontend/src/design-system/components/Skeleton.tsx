import React from 'react';
import { motion } from 'framer-motion';
import './Skeleton.css';

type SkeletonVariant = 'text' | 'circular' | 'rectangular';

interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  variant?: SkeletonVariant;
  className?: string;
}

const Skeleton: React.FC<SkeletonProps> = ({ 
  width = '100%', 
  height = '20px', 
  variant = 'text', 
  className = '' 
}) => {
  const variants: Record<SkeletonVariant, string> = {
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
