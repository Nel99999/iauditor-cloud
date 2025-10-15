import { useState, useCallback } from 'react';

// Types
type SnapPoint = 'peek' | 'half' | 'full';

interface UseBottomSheetReturn {
  isOpen: boolean;
  snapPoint: SnapPoint;
  open: (newSnapPoint?: SnapPoint) => void;
  close: () => void;
  toggle: (newSnapPoint?: SnapPoint) => void;
  setSnapPoint: (snapPoint: SnapPoint) => void;
}

/**
 * Custom hook for managing BottomSheet state
 * 
 * @param initialIsOpen - Initial open state (default: false)
 * @param initialSnapPoint - Initial snap point: 'peek' | 'half' | 'full' (default: 'half')
 * @returns { isOpen, snapPoint, open, close, toggle, setSnapPoint }
 * 
 * @example
 * const { isOpen, open, close, snapPoint, setSnapPoint } = useBottomSheet();
 * 
 * <Button onClick={open}>Open Sheet</Button>
 * <BottomSheet isOpen={isOpen} onClose={close} snapPoint={snapPoint}>
 *   <p>Content here</p>
 * </BottomSheet>
 */
const useBottomSheet = (initialIsOpen: boolean = false, initialSnapPoint: SnapPoint = 'half'): UseBottomSheetReturn => {
  const [isOpen, setIsOpen] = useState<boolean>(initialIsOpen);
  const [snapPoint, setSnapPoint] = useState<SnapPoint>(initialSnapPoint);

  const open = useCallback((newSnapPoint?: SnapPoint): void => {
    if (newSnapPoint) {
      setSnapPoint(newSnapPoint);
    }
    setIsOpen(true);
  }, []);

  const close = useCallback((): void => {
    setIsOpen(false);
  }, []);

  const toggle = useCallback((newSnapPoint?: SnapPoint): void => {
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
