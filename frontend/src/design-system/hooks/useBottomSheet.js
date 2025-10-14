import { useState, useCallback } from 'react';

/**
 * Custom hook for managing BottomSheet state
 * 
 * @param {boolean} initialIsOpen - Initial open state (default: false)
 * @param {string} initialSnapPoint - Initial snap point: 'peek' | 'half' | 'full' (default: 'half')
 * @returns {object} - { isOpen, snapPoint, open, close, toggle, setSnapPoint }
 * 
 * @example
 * const { isOpen, open, close, snapPoint, setSnapPoint } = useBottomSheet();
 * 
 * <Button onClick={open}>Open Sheet</Button>
 * <BottomSheet isOpen={isOpen} onClose={close} snapPoint={snapPoint}>
 *   <p>Content here</p>
 * </BottomSheet>
 */
const useBottomSheet = (initialIsOpen = false, initialSnapPoint = 'half') => {
  const [isOpen, setIsOpen] = useState(initialIsOpen);
  const [snapPoint, setSnapPoint] = useState(initialSnapPoint);

  const open = useCallback((newSnapPoint) => {
    if (newSnapPoint) {
      setSnapPoint(newSnapPoint);
    }
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  const toggle = useCallback((newSnapPoint) => {
    if (!isOpen && newSnapPoint) {
      setSnapPoint(newSnapPoint);
    }
    setIsOpen((prev) => !prev);
  }, [isOpen]);

  return {
    isOpen,
    snapPoint,
    open,
    close,
    toggle,
    setSnapPoint,
  };
};

export default useBottomSheet;
