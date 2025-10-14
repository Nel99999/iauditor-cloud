import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { FABProps, FABAction } from '../../types';
import './FAB.css';

/**
 * FAB (Floating Action Button) Component
 * A circular button that floats above content for primary actions
 * 
 * @param variant - 'simple' | 'speedDial' (default: 'simple')
 * @param position - 'bottom-right' | 'bottom-center' | 'bottom-left' (default: 'bottom-right')
 * @param icon - Icon component for simple FAB or main icon for speed dial
 * @param label - Accessible label for the button
 * @param onClick - Click handler for simple FAB
 * @param actions - Array of actions for speed dial
 * @param color - Color variant (default: 'primary')
 * @param size - Size variant (default: 'default')
 * @param className - Additional CSS classes
 */
const FAB: React.FC<FABProps> = ({
  variant = 'simple',
  position = 'bottom-right',
  icon,
  label = 'Action',
  onClick,
  actions = [],
  color = 'primary',
  size = 'default',
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const fabRef = useRef<HTMLDivElement>(null);

  // Close speed dial on outside click
  useEffect(() => {
    if (variant !== 'speedDial' || !isOpen) return;

    const handleClickOutside = (event: MouseEvent | TouchEvent) => {
      if (fabRef.current && !fabRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
    };
  }, [isOpen, variant]);

  // Close on ESC key
  useEffect(() => {
    if (variant !== 'speedDial' || !isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, variant]);

  const handleMainClick = () => {
    if (variant === 'simple') {
      onClick?.();
    } else {
      setIsOpen((prev) => !prev);
    }
  };

  const handleActionClick = (action: FABAction) => {
    action.onClick?.();
    setIsOpen(false);
  };

  return (
    <div
      ref={fabRef}
      className={`fab-container fab-container--${position} ${className}`}
      role="group"
      aria-label={label}
    >
      {/* Speed Dial Actions */}
      {variant === 'speedDial' && (
        <AnimatePresence>
          {isOpen && (
            <motion.div
              className="fab-actions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.2 }}
            >
              {actions.map((action, index) => (
                <motion.div
                  key={index}
                  className="fab-action-item"
                  initial={{ opacity: 0, scale: 0, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0, y: 20 }}
                  transition={{
                    delay: index * 0.05,
                    duration: 0.2,
                  }}
                >
                  <span className="fab-action-label">{action.label}</span>
                  <button
                    className={`fab-action-button fab-action-button--${action.color || 'primary'}`}
                    onClick={() => handleActionClick(action)}
                    aria-label={action.label}
                    type="button"
                  >
                    {action.icon}
                  </button>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      )}

      {/* Main FAB Button */}
      <motion.button
        className={`fab fab--${variant} fab--${color} fab--${size}`}
        onClick={handleMainClick}
        aria-label={label}
        aria-expanded={variant === 'speedDial' ? isOpen : undefined}
        type="button"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <motion.div
          className="fab-icon"
          animate={{
            rotate: variant === 'speedDial' && isOpen ? 45 : 0,
          }}
          transition={{ duration: 0.2 }}
        >
          {icon}
        </motion.div>
      </motion.button>
    </div>
  );
};

/**
 * DefaultIcons - Default icons for FAB
 */
export const DefaultIcons = {
  Plus: () => (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  ),
  Edit: () => (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  ),
  Task: () => (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M9 11l3 3L22 4" />
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
    </svg>
  ),
  Inspection: () => (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  ),
  Checklist: () => (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 12l2 2 4-4" />
      <path d="M3 6l2 2 4-4" />
      <path d="M3 18l2 2 4-4" />
      <line x1="13" y1="6" x2="21" y2="6" />
      <line x1="13" y1="12" x2="21" y2="12" />
      <line x1="13" y1="18" x2="21" y2="18" />
    </svg>
  ),
};

export default FAB;
