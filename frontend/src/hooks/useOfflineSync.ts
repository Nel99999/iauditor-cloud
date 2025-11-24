/**
 * useOfflineSync Hook
 * Manages offline/online state and automatic synchronization
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { offlineStorage } from '../utils/offlineStorage';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

interface SyncStatus {
    isOnline: boolean;
    isSyncing: boolean;
    pendingCount: number;
    lastSyncTime: number | null;
    error: string | null;
}

export function useOfflineSync() {
    const [status, setStatus] = useState<SyncStatus>({
        isOnline: navigator.onLine,
        isSyncing: false,
        pendingCount: 0,
        lastSyncTime: null,
        error: null
    });

    const syncInProgress = useRef(false);

    // Update pending count
    const updatePendingCount = useCallback(async () => {
        const queue = await offlineStorage.getSyncQueue();
        setStatus(prev => ({ ...prev, pendingCount: queue.length }));
    }, []);

    // Sync pending operations
    const syncPendingOperations = useCallback(async () => {
        if (syncInProgress.current || !navigator.onLine) {
            return;
        }

        syncInProgress.current = true;
        setStatus(prev => ({ ...prev, isSyncing: true, error: null }));

        try {
            const queue = await offlineStorage.getSyncQueue();

            for (const operation of queue) {
                try {
                    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
                    const headers = { Authorization: `Bearer ${token}` };

                    switch (operation.type) {
                        case 'create':
                            await axios.post(`${API}/${operation.resource}`, operation.data, { headers });
                            break;
                        case 'update':
                            await axios.put(`${API}/${operation.resource}/${operation.data._id}`, operation.data, { headers });
                            break;
                        case 'delete':
                            await axios.delete(`${API}/${operation.resource}/${operation.data._id}`, { headers });
                            break;
                    }

                    // Remove from queue on success
                    await offlineStorage.removeSyncQueueItem(operation.id);
                } catch (error: any) {
                    console.error('Sync operation failed:', error);

                    // Increment retry count
                    await offlineStorage.incrementSyncRetry(operation.id);

                    // Remove if too many retries
                    if (operation.retryCount >= 3) {
                        await offlineStorage.removeSyncQueueItem(operation.id);
                    }
                }
            }

            setStatus(prev => ({
                ...prev,
                lastSyncTime: Date.now(),
                error: null
            }));
        } catch (error: any) {
            setStatus(prev => ({
                ...prev,
                error: error.message || 'Sync failed'
            }));
        } finally {
            syncInProgress.current = false;
            setStatus(prev => ({ ...prev, isSyncing: false }));
            await updatePendingCount();
        }
    }, [updatePendingCount]);

    // Handle online/offline events
    useEffect(() => {
        const handleOnline = () => {
            setStatus(prev => ({ ...prev, isOnline: true }));
            // Automatically sync when coming online
            syncPendingOperations();
        };

        const handleOffline = () => {
            setStatus(prev => ({ ...prev, isOnline: false }));
        };

        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        // Initial pending count
        updatePendingCount();

        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, [syncPendingOperations, updatePendingCount]);

    // Listen for service worker sync events
    useEffect(() => {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.addEventListener('message', (event) => {
                if (event.data && event.data.type === 'SYNC_TRIGGERED') {
                    syncPendingOperations();
                }
            });
        }
    }, [syncPendingOperations]);

    // Periodic sync check (every 30 seconds when online)
    useEffect(() => {
        if (!status.isOnline) return;

        const interval = setInterval(() => {
            if (status.pendingCount > 0) {
                syncPendingOperations();
            }
        }, 30000);

        return () => clearInterval(interval);
    }, [status.isOnline, status.pendingCount, syncPendingOperations]);

    return {
        ...status,
        syncNow: syncPendingOperations,
        refreshPendingCount: updatePendingCount
    };
}

// Hook for optimistic updates
export function useOptimisticUpdate<T>(
    resource: string,
    onlineAction: (data: T) => Promise<any>
) {
    const [isUpdating, setIsUpdating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const executeOptimistically = useCallback(
        async (data: T, optimisticUpdate: () => void, rollback: () => void) => {
            setIsUpdating(true);
            setError(null);

            // Apply optimistic update immediately
            optimisticUpdate();

            try {
                if (navigator.onLine) {
                    // Try online action
                    await onlineAction(data);
                } else {
                    // Queue for later sync
                    await offlineStorage.addToSyncQueue({
                        type: 'update',
                        resource,
                        data
                    });
                }
            } catch (err: any) {
                // Rollback on failure
                rollback();
                setError(err.message || 'Update failed');

                // Still queue for retry if offline
                if (!navigator.onLine) {
                    await offlineStorage.addToSyncQueue({
                        type: 'update',
                        resource,
                        data
                    });
                }
            } finally {
                setIsUpdating(false);
            }
        },
        [resource, onlineAction]
    );

    return {
        isUpdating,
        error,
        executeOptimistically
    };
}
