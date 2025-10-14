import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSwipeable } from 'react-swipeable';
import './BottomSheet.css';

const SNAP_POINTS = {
  peek: '25%',
  half: '50%',
  full: '90%',
};

/**
 * BottomSheet Component
 * A mobile-optimized modal that slides up from the bottom of the screen
 * 
 * @param {boolean} isOpen - Controls visibility of the bottom sheet
 * @param {function} onClose - Callback when bottom sheet is closed
 * @param {string} snapPoint - Initial height: 'peek' | 'half' | 'full'
 * @param {boolean} enableSwipe - Enable swipe gestures (default: true)
 * @param {boolean} showDragHandle - Show drag handle indicator (default: true)
 * @param {string} title - Optional title for the bottom sheet
 * @param {React.ReactNode} children - Content to display
 */
const BottomSheet = ({
  isOpen = false,
  onClose,
  snapPoint = 'half',
  enableSwipe = true,
  showDragHandle = true,
  title,
  children,
  className = '',
}) => {
  const [currentSnap, setCurrentSnap] = React.useState(snapPoint);
  const [isDragging, setIsDragging] = React.useState(false);
  const sheetRef = useRef(null);
  const startYRef = useRef(0);
  const currentYRef = useRef(0);

  // Lock body scroll when bottom sheet is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      // Reset snap point when opening
      setCurrentSnap(snapPoint);
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen, snapPoint]);

  // Handle ESC key press
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose?.();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Swipeable handlers
  const swipeHandlers = useSwipeable({
    onSwipeStart: (eventData) => {
      if (!enableSwipe) return;
      setIsDragging(true);
      startYRef.current = eventData.initial[1];
    },
    onSwiping: (eventData) => {
      if (!enableSwipe) return;
      const deltaY = eventData.deltaY;
      currentYRef.current = deltaY;
      
      // Only allow dragging down
      if (deltaY > 0 && sheetRef.current) {
        sheetRef.current.style.transform = `translateY(${deltaY}px)`;
      }
    },
    onSwiped: (eventData) => {
      if (!enableSwipe) return;
      setIsDragging(false);
      const deltaY = eventData.deltaY;
      const velocity = eventData.velocity;

      // Reset transform
      if (sheetRef.current) {
        sheetRef.current.style.transform = '';
      }

      // Close if swiped down significantly or with high velocity
      if (deltaY > 150 || velocity > 0.5) {
        onClose?.();
      } else if (deltaY < -100) {
        // Swipe up to expand
        if (currentSnap === 'peek') {
          setCurrentSnap('half');
        } else if (currentSnap === 'half') {
          setCurrentSnap('full');
        }
      } else if (deltaY > 50) {
        // Swipe down to collapse
        if (currentSnap === 'full') {
          setCurrentSnap('half');
        } else if (currentSnap === 'half') {
          setCurrentSnap('peek');
        }
      }
    },
    trackMouse: false,
    trackTouch: true,
  });

  const handleBackdropClick = () => {
    onClose?.();
  };

  const handleSheetClick = (e) => {
    e.stopPropagation();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="bottom-sheet-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={handleBackdropClick}
            aria-hidden="true"
          />

          {/* Bottom Sheet */}
          <motion.div
            ref={sheetRef}
            className={`bottom-sheet bottom-sheet--${currentSnap} ${className}`}
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{
              type: 'spring',
              damping: 30,
              stiffness: 300,
            }}
            onClick={handleSheetClick}
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? 'bottom-sheet-title' : undefined}
            style={{
              height: SNAP_POINTS[currentSnap],
            }}
            {...(enableSwipe ? swipeHandlers : {})}
          >
            {/* Drag Handle */}
            {showDragHandle && (
              <div className="bottom-sheet-handle-container">
                <div className="bottom-sheet-handle" />
              </div>
            )}

            {/* Content */}
            <div className="bottom-sheet-content">
              {title && (
                <div className="bottom-sheet-header">
                  <h2 id="bottom-sheet-title" className="bottom-sheet-title">
                    {title}
                  </h2>
                </div>
              )}
              <div className="bottom-sheet-body">
                {children}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default BottomSheet;
