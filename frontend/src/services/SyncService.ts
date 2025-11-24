import axios from 'axios';
import OfflineStorageService from './OfflineStorageService';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

class SyncService {
    async syncPendingInspections(): Promise<{ synced: number; errors: number }> {
        if (!navigator.onLine) {
            return { synced: 0, errors: 0 };
        }

        const inspections = OfflineStorageService.getOfflineInspections();
        const pending = inspections.filter((i) => !i.synced && i.status === 'completed');

        let syncedCount = 0;
        let errorCount = 0;

        for (const inspection of pending) {
            try {
                // 1. Create execution on backend if it doesn't exist (or we generated a local ID)
                // For simplicity, we'll assume we need to create a new one or update an existing one
                // If the ID is a UUID v4 (local), we likely need to create it.

                // Check if it's a local ID (simple check, real app might use a prefix)
                const isLocalId = inspection.id.length > 24; // MongoDB IDs are 24 hex chars

                let backendId = inspection.id;

                if (isLocalId) {
                    // Create new execution
                    const createRes = await axios.post(`${API}/inspections/executions`, {
                        template_id: inspection.template_id,
                        location: null, // TODO: Add location if captured
                    });
                    backendId = createRes.data.id;
                }

                // 2. Submit answers
                await axios.put(`${API}/inspections/executions/${backendId}`, {
                    answers: inspection.answers,
                    notes: inspection.notes,
                });

                // 3. Complete it
                await axios.post(`${API}/inspections/executions/${backendId}/complete`, {
                    answers: inspection.answers,
                    findings: inspection.findings || [],
                    notes: inspection.notes,
                });

                // 4. Remove from offline storage on success
                OfflineStorageService.deleteOfflineInspection(inspection.id);
                syncedCount++;

            } catch (error) {
                console.error(`Failed to sync inspection ${inspection.id}`, error);
                errorCount++;
            }
        }

        return { synced: syncedCount, errors: errorCount };
    }

    async downloadRequiredTemplates(): Promise<void> {
        if (!navigator.onLine) return;

        try {
            // Get all templates (or just assigned ones in a real app)
            const response = await axios.get(`${API}/inspections/templates`);
            const templates = response.data;

            for (const template of templates) {
                OfflineStorageService.saveTemplate(template);
            }
            console.log(`Cached ${templates.length} templates for offline use.`);
        } catch (error) {
            console.error("Failed to download templates:", error);
        }
    }

    async downloadMyTasks(): Promise<void> {
        if (!navigator.onLine) return;

        try {
            const response = await axios.get(`${API}/tasks`);
            OfflineStorageService.saveTasks(response.data);
            console.log(`Cached ${response.data.length} tasks.`);
        } catch (error) {
            console.error("Failed to download tasks:", error);
        }
    }
}

export default new SyncService();
