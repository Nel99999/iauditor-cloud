import React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import './EmptyState.css';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: LucideIcon;
  action?: React.ReactNode;
  className?: string;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon: Icon,
  action,
  className = ''
}) => {
  return (
    <motion.div
      className={`empty-state ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {Icon && (
        <motion.div
          className="empty-state__icon"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
        >
          <Icon size={64} />
        </motion.div>
      )}
      
      <h3 className="empty-state__title">{title}</h3>
      
      {description && (
        <p className="empty-state__description">{description}</p>
      )}
      
      {action && (
        <motion.div
          className="empty-state__action"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          {action}
        </motion.div>
      )}
    </motion.div>
  );
};

export default EmptyState;
