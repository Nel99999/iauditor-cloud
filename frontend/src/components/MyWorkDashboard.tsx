import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { GlassCard, Button, Spinner } from '@/design-system/components';
import { motion } from 'framer-motion';
import {
    CheckSquare,
    ClipboardCheck,
    Clock,
    AlertCircle,
    ArrowRight,
    Calendar
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

interface Task {
    id: string;
    title: string;
    status: string;
    priority: string;
    due_date: string;
}

interface Inspection {
    id: string;
    template_name: string;
    status: string;
    created_at: string;
}

const MyWorkDashboard = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [myTasks, setMyTasks] = useState<Task[]>([]);
    const [myInspections, setMyInspections] = useState<Inspection[]>([]);

    useEffect(() => {
        loadMyWork();
    }, []);

    const loadMyWork = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('access_token');
            const headers = { Authorization: `Bearer ${token}` };

            // Fetch tasks assigned to me
            // Note: In a real implementation, we would filter by assignee_id on the backend
            // For now, we'll fetch all and filter client-side or assume the endpoint returns relevant ones
            const tasksRes = await axios.get(`${API}/tasks`, { headers });
            const myPendingTasks = tasksRes.data
                .filter((t: any) => t.status !== 'completed')
                .slice(0, 5); // Top 5

            // Fetch my recent inspections
            const inspectionsRes = await axios.get(`${API}/inspections/executions`, { headers });
            const myActiveInspections = inspectionsRes.data
                .filter((i: any) => i.status !== 'completed')
                .slice(0, 5);

            setMyTasks(myPendingTasks);
            setMyInspections(myActiveInspections);
        } catch (error) {
            console.error("Failed to load my work:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh]">
                <Spinner size="xl" />
                <p className="mt-4 text-muted-foreground">Loading your workspace...</p>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-6xl mx-auto space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
            >
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                        Good Morning, {user?.name?.split(' ')[0]}! ☀️
                    </h1>
                    <p className="text-slate-600 dark:text-slate-400 mt-1">
                        You have <strong className="text-primary">{myTasks.length} tasks</strong> and <strong className="text-primary">{myInspections.length} inspections</strong> pending.
                    </p>
                </div>
                <Button onClick={() => navigate('/inspections')} size="lg" icon={<ClipboardCheck />}>
                    Start New Inspection
                </Button>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* My Tasks Section */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold flex items-center gap-2">
                            <CheckSquare className="text-blue-500" />
                            My Tasks
                        </h2>
                        <Button variant="ghost" size="sm" onClick={() => navigate('/tasks')}>
                            View All <ArrowRight className="ml-1 h-4 w-4" />
                        </Button>
                    </div>

                    <div className="space-y-3">
                        {myTasks.length > 0 ? (
                            myTasks.map((task) => (
                                <GlassCard
                                    key={task.id}
                                    hover
                                    className="cursor-pointer border-l-4 border-l-blue-500"
                                    onClick={() => navigate('/tasks')}
                                >
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h3 className="font-medium text-slate-900 dark:text-white">{task.title}</h3>
                                            <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                                                <span className="flex items-center gap-1">
                                                    <Clock className="h-3 w-3" /> {task.due_date || 'No due date'}
                                                </span>
                                                <span className={`px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 capitalize`}>
                                                    {task.priority}
                                                </span>
                                            </div>
                                        </div>
                                        <div className={`h-3 w-3 rounded-full ${task.priority === 'urgent' ? 'bg-red-500' :
                                                task.priority === 'high' ? 'bg-orange-500' : 'bg-green-500'
                                            }`} />
                                    </div>
                                </GlassCard>
                            ))
                        ) : (
                            <GlassCard className="text-center py-8">
                                <CheckSquare className="h-12 w-12 mx-auto text-slate-300 mb-3" />
                                <p className="text-muted-foreground">No pending tasks! 🎉</p>
                                <Button variant="outline" size="sm" className="mt-4" onClick={() => navigate('/tasks')}>
                                    Create Task
                                </Button>
                            </GlassCard>
                        )}
                    </div>
                </motion.div>

                {/* My Inspections Section */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold flex items-center gap-2">
                            <ClipboardCheck className="text-purple-500" />
                            Active Inspections
                        </h2>
                        <Button variant="ghost" size="sm" onClick={() => navigate('/inspections')}>
                            View All <ArrowRight className="ml-1 h-4 w-4" />
                        </Button>
                    </div>

                    <div className="space-y-3">
                        {myInspections.length > 0 ? (
                            myInspections.map((inspection) => (
                                <GlassCard
                                    key={inspection.id}
                                    hover
                                    className="cursor-pointer border-l-4 border-l-purple-500"
                                    onClick={() => navigate(`/inspections/${inspection.id}/execute`)} // Assuming this route exists or similar
                                >
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h3 className="font-medium text-slate-900 dark:text-white">
                                                {inspection.template_name || 'Untitled Inspection'}
                                            </h3>
                                            <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                                                <span className="flex items-center gap-1">
                                                    <Calendar className="h-3 w-3" /> {new Date(inspection.created_at).toLocaleDateString()}
                                                </span>
                                                <span className="px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300 capitalize">
                                                    {inspection.status}
                                                </span>
                                            </div>
                                        </div>
                                        <Button size="sm" variant="secondary" className="h-8">
                                            Continue
                                        </Button>
                                    </div>
                                </GlassCard>
                            ))
                        ) : (
                            <GlassCard className="text-center py-8">
                                <ClipboardCheck className="h-12 w-12 mx-auto text-slate-300 mb-3" />
                                <p className="text-muted-foreground">No active inspections.</p>
                                <Button variant="primary" size="sm" className="mt-4" onClick={() => navigate('/inspections')}>
                                    Start New
                                </Button>
                            </GlassCard>
                        )}
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default MyWorkDashboard;
