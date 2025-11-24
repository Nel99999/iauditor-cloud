

const STORAGE_KEYS = {
    TEMPLATES: 'offline_templates',
    INSPECTIONS: 'offline_inspections',
    TASKS: 'offline_tasks',
    QUEUE: 'sync_queue',
};

export interface OfflineInspection {
    id: string;
    template_id: string;
    answers: any[];
    status: 'in_progress' | 'completed';
    created_at: string;
    updated_at: string;
    synced: boolean;
    notes?: string;
    findings?: string[];
}

class OfflineStorageService {
    // --- Templates ---
    saveTemplate(template: any): void {
        const templates = this.getTemplates();
        templates[template.id] = template;
        localStorage.setItem(STORAGE_KEYS.TEMPLATES, JSON.stringify(templates));
    }

    getTemplate(id: string): any | null {
        const templates = this.getTemplates();
        return templates[id] || null;
    }

    getTemplates(): Record<string, any> {
        const data = localStorage.getItem(STORAGE_KEYS.TEMPLATES);
        return data ? JSON.parse(data) : {};
    }

    // --- Inspections ---
    saveOfflineInspection(inspection: OfflineInspection): void {
        const inspections = this.getOfflineInspections();
        // Update existing or add new
        const index = inspections.findIndex((i) => i.id === inspection.id);

        if (index >= 0) {
            inspections[index] = { ...inspections[index], ...inspection, updated_at: new Date().toISOString() };
        } else {
            inspections.push({ ...inspection, created_at: new Date().toISOString(), updated_at: new Date().toISOString() });
        }

        localStorage.setItem(STORAGE_KEYS.INSPECTIONS, JSON.stringify(inspections));
    }

    getOfflineInspections(): OfflineInspection[] {
        const data = localStorage.getItem(STORAGE_KEYS.INSPECTIONS);
        return data ? JSON.parse(data) : [];
    }

    getOfflineInspection(id: string): OfflineInspection | undefined {
        return this.getOfflineInspections().find((i) => i.id === id);
    }

    deleteOfflineInspection(id: string): void {
        const inspections = this.getOfflineInspections().filter((i) => i.id !== id);
        localStorage.setItem(STORAGE_KEYS.INSPECTIONS, JSON.stringify(inspections));
    }

    // --- Tasks ---
    saveTasks(tasks: any[]): void {
        localStorage.setItem(STORAGE_KEYS.TASKS, JSON.stringify(tasks));
    }

    getOfflineTasks(): any[] {
        const data = localStorage.getItem(STORAGE_KEYS.TASKS);
        return data ? JSON.parse(data) : [];
    }

    // --- Utilities ---
    clearAll(): void {
        localStorage.removeItem(STORAGE_KEYS.TEMPLATES);
        localStorage.removeItem(STORAGE_KEYS.INSPECTIONS);
        localStorage.removeItem(STORAGE_KEYS.TASKS);
        localStorage.removeItem(STORAGE_KEYS.QUEUE);
    }

    isOnline(): boolean {
        return navigator.onLine;
    }
}

export default new OfflineStorageService();
