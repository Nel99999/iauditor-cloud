/**
 * Offline Storage using IndexedDB
 * Provides offline-first data persistence for the PWA
 */

import { openDB, DBSchema, IDBPDatabase } from 'idb';

interface OpsPlatformDB extends DBSchema {
    inspections: {
        key: string;
        value: any;
        indexes: { 'by-status': string; 'by-date': string };
    };
    tasks: {
        key: string;
        value: any;
        indexes: { 'by-status': string; 'by-assignee': string };
    };
    checklists: {
        key: string;
        value: any;
        indexes: { 'by-status': string };
    };
    syncQueue: {
        key: number;
        value: {
            id: number;
            type: 'create' | 'update' | 'delete';
            resource: string;
            data: any;
            timestamp: number;
            retryCount: number;
        };
        indexes: { 'by-timestamp': number };
    };
    metadata: {
        key: string;
        value: any;
    };
}

class OfflineStorage {
    private dbPromise: Promise<IDBPDatabase<OpsPlatformDB>>;
    private readonly DB_NAME = 'opsplatform-offline';
    private readonly DB_VERSION = 1;

    constructor() {
        this.dbPromise = this.initDB();
    }

    private async initDB(): Promise<IDBPDatabase<OpsPlatformDB>> {
        return openDB<OpsPlatformDB>(this.DB_NAME, this.DB_VERSION, {
            upgrade(db) {
                // Inspections store
                if (!db.objectStoreNames.contains('inspections')) {
                    const inspectionStore = db.createObjectStore('inspections', { keyPath: '_id' });
                    inspectionStore.createIndex('by-status', 'status');
                    inspectionStore.createIndex('by-date', 'created_at');
                }

                // Tasks store
                if (!db.objectStoreNames.contains('tasks')) {
                    const taskStore = db.createObjectStore('tasks', { keyPath: '_id' });
                    taskStore.createIndex('by-status', 'status');
                    taskStore.createIndex('by-assignee', 'assigned_to');
                }

                // Checklists store
                if (!db.objectStoreNames.contains('checklists')) {
                    const checklistStore = db.createObjectStore('checklists', { keyPath: '_id' });
                    checklistStore.createIndex('by-status', 'status');
                }

                // Sync queue
                if (!db.objectStoreNames.contains('syncQueue')) {
                    const syncStore = db.createObjectStore('syncQueue', { keyPath: 'id', autoIncrement: true });
                    syncStore.createIndex('by-timestamp', 'timestamp');
                }

                // Metadata store for last sync times, etc.
                if (!db.objectStoreNames.contains('metadata')) {
                    db.createObjectStore('metadata', { keyPath: 'key' });
                }
            },
        });
    }

    // Generic CRUD operations
    async get<T extends keyof OpsPlatformDB>(
        storeName: T,
        key: OpsPlatformDB[T]['key']
    ): Promise<OpsPlatformDB[T]['value'] | undefined> {
        const db = await this.dbPromise;
        return db.get(storeName, key);
    }

    async getAll<T extends keyof OpsPlatformDB>(
        storeName: T
    ): Promise<Array<OpsPlatformDB[T]['value']>> {
        const db = await this.dbPromise;
        return db.getAll(storeName);
    }

    async put<T extends keyof OpsPlatformDB>(
        storeName: T,
        value: OpsPlatformDB[T]['value']
    ): Promise<OpsPlatformDB[T]['key']> {
        const db = await this.dbPromise;
        return db.put(storeName, value);
    }

    async delete<T extends keyof OpsPlatformDB>(
        storeName: T,
        key: OpsPlatformDB[T]['key']
    ): Promise<void> {
        const db = await this.dbPromise;
        return db.delete(storeName, key);
    }

    async clear<T extends keyof OpsPlatformDB>(storeName: T): Promise<void> {
        const db = await this.dbPromise;
        return db.clear(storeName);
    }

    // Sync Queue Management
    async addToSyncQueue(operation: {
        type: 'create' | 'update' | 'delete';
        resource: string;
        data: any;
    }): Promise<number> {
        const db = await this.dbPromise;
        return db.add('syncQueue', {
            ...operation,
            timestamp: Date.now(),
            retryCount: 0,
            id: 0 // Will be auto-incremented
        });
    }

    async getSyncQueue(): Promise<Array<OpsPlatformDB['syncQueue']['value']>> {
        const db = await this.dbPromise;
        return db.getAll('syncQueue');
    }

    async removeSyncQueueItem(id: number): Promise<void> {
        const db = await this.dbPromise;
        return db.delete('syncQueue', id);
    }

    async incrementSyncRetry(id: number): Promise<void> {
        const db = await this.dbPromise;
        const item = await db.get('syncQueue', id);
        if (item) {
            item.retryCount += 1;
            await db.put('syncQueue', item);
        }
    }

    // Metadata operations
    async getLastSyncTime(resource: string): Promise<number | null> {
        const db = await this.dbPromise;
        const meta = await db.get('metadata', `last-sync-${resource}`);
        return meta?.value || null;
    }

    async setLastSyncTime(resource: string, timestamp: number): Promise<void> {
        const db = await this.dbPromise;
        await db.put('metadata', {
            key: `last-sync-${resource}`,
            value: timestamp
        });
    }

    // Batch operations for better performance
    async batchPut<T extends keyof OpsPlatformDB>(
        storeName: T,
        items: Array<OpsPlatformDB[T]['value']>
    ): Promise<void> {
        const db = await this.dbPromise;
        const tx = db.transaction(storeName, 'readwrite');
        await Promise.all([
            ...items.map(item => tx.store.put(item)),
            tx.done
        ]);
    }

    // Search by index
    async getAllByIndex<T extends keyof OpsPlatformDB>(
        storeName: T,
        indexName: string,
        query?: IDBKeyRange | IDBValidKey
    ): Promise<Array<OpsPlatformDB[T]['value']>> {
        const db = await this.dbPromise;
        return db.getAllFromIndex(storeName as any, indexName, query);
    }

    // Cleanup old data
    async cleanupOldData(storeName: keyof OpsPlatformDB, maxAge: number): Promise<void> {
        const db = await this.dbPromise;
        const cutoffTime = Date.now() - maxAge;

        const tx = db.transaction(storeName, 'readwrite');
        let cursor = await tx.store.openCursor();

        while (cursor) {
            const item = cursor.value as any;
            if (item.created_at && new Date(item.created_at).getTime() < cutoffTime) {
                await cursor.delete();
            }
            cursor = await cursor.continue();
        }

        await tx.done;
    }
}

// Singleton instance
export const offlineStorage = new OfflineStorage();

// Utility functions for common operations
export async function cacheInspections(inspections: any[]): Promise<void> {
    await offlineStorage.batchPut('inspections', inspections);
    await offlineStorage.setLastSyncTime('inspections', Date.now());
}

export async function cacheTasks(tasks: any[]): Promise<void> {
    await offlineStorage.batchPut('tasks', tasks);
    await offlineStorage.setLastSyncTime('tasks', Date.now());
}

export async function cacheChecklists(checklists: any[]): Promise<void> {
    await offlineStorage.batchPut('checklists', checklists);
    await offlineStorage.setLastSyncTime('checklists', Date.now());
}

export async function getPendingSyncOperationsCount(): Promise<number> {
    const queue = await offlineStorage.getSyncQueue();
    return queue.length;
}

export async function clearAllOfflineData(): Promise<void> {
    await offlineStorage.clear('inspections');
    await offlineStorage.clear('tasks');
    await offlineStorage.clear('checklists');
    await offlineStorage.clear('syncQueue');
    await offlineStorage.clear('metadata');
}
