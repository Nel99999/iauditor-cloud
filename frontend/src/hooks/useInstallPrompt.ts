/**
 * useInstallPrompt Hook
 * Manages PWA installation prompt
 */

import { useState, useEffect, useCallback } from 'react';

interface BeforeInstallPromptEvent extends Event {
    prompt: () => Promise<void>;
    userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export function useInstallPrompt() {
    const [installPromptEvent, setInstallPromptEvent] = useState<BeforeInstallPromptEvent | null>(null);
    const [isInstallable, setIsInstallable] = useState(false);
    const [isInstalled, setIsInstalled] = useState(false);

    useEffect(() => {
        // Check if already installed
        if (window.matchMedia('(display-mode: standalone)').matches) {
            setIsInstalled(true);
            return;
        }

        const handleBeforeInstallPrompt = (e: Event) => {
            e.preventDefault();
            setInstallPromptEvent(e as BeforeInstallPromptEvent);
            setIsInstallable(true);
        };

        const handleAppInstalled = () => {
            setIsInstalled(true);
            setIsInstallable(false);
            setInstallPromptEvent(null);
        };

        window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
        window.addEventListener('appinstalled', handleAppInstalled);

        return () => {
            window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
            window.removeEventListener('appinstalled', handleAppInstalled);
        };
    }, []);

    const promptInstall = useCallback(async () => {
        if (!installPromptEvent) {
            return false;
        }

        installPromptEvent.prompt();
        const choice = await installPromptEvent.userChoice;

        if (choice.outcome === 'accepted') {
            setIsInstallable(false);
            setInstallPromptEvent(null);
            return true;
        }

        return false;
    }, [installPromptEvent]);

    // Check iOS
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream;
    const isInStandaloneMode = window.matchMedia('(display-mode: standalone)').matches;

    return {
        isInstallable,
        isInstalled,
        isIOS,
        canInstall: isInstallable && !isInstalled,
        showIOSInstructions: isIOS && !isInStandaloneMode,
        promptInstall
    };
}
