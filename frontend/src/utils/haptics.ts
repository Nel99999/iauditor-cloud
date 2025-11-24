/**
 * Haptic Feedback Utilities for Mobile Devices
 * Provides tactile feedback for touch interactions
 */

export type HapticPattern = 'light' | 'medium' | 'heavy' | 'success' | 'warning' | 'error';

/**
 * Check if haptic feedback is supported
 */
export const isHapticSupported = (): boolean => {
    return 'vibrate' in navigator;
};

/**
 * Trigger haptic feedback with specified pattern
 * @param pattern - Type of haptic feedback
 */
export const triggerHaptic = (pattern: HapticPattern = 'light'): void => {
    if (!isHapticSupported()) return;

    const patterns: Record<HapticPattern, number | number[]> = {
        light: 10,
        medium: 20,
        heavy: 40,
        success: [10, 50, 10],
        warning: [20, 100, 20],
        error: [40, 100, 40, 100, 40],
    };

    const vibrationPattern = patterns[pattern];

    try {
        if (Array.isArray(vibrationPattern)) {
            navigator.vibrate(vibrationPattern);
        } else {
            navigator.vibrate(vibrationPattern);
        }
    } catch (error) {
        // Silently fail if vibration API throws error
        console.debug('Haptic feedback not available:', error);
    }
};

/**
 * Hook for haptic feedback in React components
 */
export const useHaptic = () => {
    return {
        triggerHaptic,
        isSupported: isHapticSupported(),
    };
};

export default {
    triggerHaptic,
    isHapticSupported,
    useHaptic,
};
