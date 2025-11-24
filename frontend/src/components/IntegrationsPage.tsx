// @ts-nocheck
import { useState } from 'react';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Webhook, Key, Plus, Trash2, RefreshCw, Copy, CheckCircle, ShieldAlert } from 'lucide-react';

const IntegrationsPage = () => {
    const [webhooks, setWebhooks] = useState([
        { id: 1, url: 'https://api.example.com/hooks/inspection-complete', event: 'inspection.completed', status: 'active', created_at: '2023-10-15' },
        { id: 2, url: 'https://slack.com/api/webhooks/T123/B456', event: 'task.created', status: 'failed', created_at: '2023-10-20' }
    ]);

    const [apiKeys, setApiKeys] = useState([
        { id: 1, name: 'Production API Key', prefix: 'pk_live_...', created_at: '2023-09-01', last_used: '2023-10-25' },
        { id: 2, name: 'Development Key', prefix: 'pk_test_...', created_at: '2023-10-01', last_used: 'Never' }
    ]);

    const [showWebhookDialog, setShowWebhookDialog] = useState(false);
    const [newWebhook, setNewWebhook] = useState({ url: '', event: '' });
    const [copiedKeyId, setCopiedKeyId] = useState<number | null>(null);

    const handleAddWebhook = (e: any) => {
        e.preventDefault();
        setWebhooks([
            ...webhooks,
            {
                id: Date.now(),
                url: newWebhook.url,
                event: newWebhook.event,
                status: 'active',
                created_at: new Date().toISOString().slice(0, 10)
            }
        ]);
        setShowWebhookDialog(false);
        setNewWebhook({ url: '', event: '' });
    };

    const handleDeleteWebhook = (id: number) => {
        setWebhooks(webhooks.filter(w => w.id !== id));
    };

    const handleRegenerateKey = (id: number) => {
        if (window.confirm('Are you sure? This will invalidate the current key immediately.')) {
            alert('Key regenerated! New key: pk_live_' + Math.random().toString(36).substring(7));
        }
    };

    const handleCopyKey = (id: number) => {
        navigator.clipboard.writeText('pk_live_example_key_12345');
        setCopiedKeyId(id);
        setTimeout(() => setCopiedKeyId(null), 2000);
    };

    return (
        <ModernPageWrapper
            title="Integrations"
            subtitle="Manage connections and API access"
        >
            <Tabs defaultValue="webhooks" className="space-y-6">
                <TabsList>
                    <TabsTrigger value="webhooks">Webhooks</TabsTrigger>
                    <TabsTrigger value="api-keys">API Keys</TabsTrigger>
                </TabsList>

                <TabsContent value="webhooks">
                    <div className="flex justify-between items-center mb-4">
                        <div>
                            <h3 className="text-lg font-medium">Active Webhooks</h3>
                            <p className="text-sm text-muted-foreground">Receive real-time updates for system events</p>
                        </div>
                        <Button onClick={() => setShowWebhookDialog(true)}>
                            <Plus className="h-4 w-4 mr-2" />
                            Add Webhook
                        </Button>
                    </div>

                    <div className="grid gap-4">
                        {webhooks.map(webhook => (
                            <Card key={webhook.id}>
                                <CardContent className="p-6 flex items-center justify-between">
                                    <div className="flex items-start gap-4">
                                        <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg">
                                            <Webhook className="h-6 w-6 text-slate-600" />
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <h4 className="font-semibold">{webhook.url}</h4>
                                                <Badge variant={webhook.status === 'active' ? 'default' : 'destructive'}>
                                                    {webhook.status}
                                                </Badge>
                                            </div>
                                            <p className="text-sm text-muted-foreground mt-1">
                                                Event: <Badge variant="outline">{webhook.event}</Badge> • Created: {webhook.created_at}
                                            </p>
                                        </div>
                                    </div>
                                    <Button variant="ghost" size="icon" onClick={() => handleDeleteWebhook(webhook.id)}>
                                        <Trash2 className="h-4 w-4 text-red-500" />
                                    </Button>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </TabsContent>

                <TabsContent value="api-keys">
                    <div className="flex justify-between items-center mb-4">
                        <div>
                            <h3 className="text-lg font-medium">API Keys</h3>
                            <p className="text-sm text-muted-foreground">Manage access tokens for external applications</p>
                        </div>
                        <Button>
                            <Plus className="h-4 w-4 mr-2" />
                            Generate New Key
                        </Button>
                    </div>

                    <div className="grid gap-4">
                        {apiKeys.map(key => (
                            <Card key={key.id}>
                                <CardContent className="p-6 flex items-center justify-between">
                                    <div className="flex items-start gap-4">
                                        <div className="p-2 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                                            <Key className="h-6 w-6 text-amber-600" />
                                        </div>
                                        <div>
                                            <h4 className="font-semibold">{key.name}</h4>
                                            <div className="flex items-center gap-2 mt-1">
                                                <code className="bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded text-xs font-mono">
                                                    {key.prefix}****************
                                                </code>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-6 w-6"
                                                    onClick={() => handleCopyKey(key.id)}
                                                >
                                                    {copiedKeyId === key.id ? <CheckCircle className="h-3 w-3 text-green-500" /> : <Copy className="h-3 w-3" />}
                                                </Button>
                                            </div>
                                            <p className="text-xs text-muted-foreground mt-2">
                                                Created: {key.created_at} • Last used: {key.last_used}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex gap-2">
                                        <Button variant="outline" size="sm" onClick={() => handleRegenerateKey(key.id)}>
                                            <RefreshCw className="h-4 w-4 mr-2" />
                                            Regenerate
                                        </Button>
                                        <Button variant="ghost" size="icon">
                                            <Trash2 className="h-4 w-4 text-red-500" />
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}

                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
                            <ShieldAlert className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />
                            <div>
                                <h4 className="font-medium text-blue-900">Security Note</h4>
                                <p className="text-sm text-blue-800 mt-1">
                                    API keys grant full access to your organization's data. Keep them secure and never share them in public repositories or client-side code.
                                </p>
                            </div>
                        </div>
                    </div>
                </TabsContent>
            </Tabs>

            <Dialog open={showWebhookDialog} onOpenChange={setShowWebhookDialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Add Webhook Endpoint</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleAddWebhook}>
                        <div className="space-y-4">
                            <div>
                                <Label>Endpoint URL</Label>
                                <Input
                                    value={newWebhook.url}
                                    onChange={(e) => setNewWebhook({ ...newWebhook, url: e.target.value })}
                                    placeholder="https://api.yoursystem.com/webhook"
                                    required
                                />
                            </div>
                            <div>
                                <Label>Event Subscription</Label>
                                <Select
                                    value={newWebhook.event}
                                    onValueChange={(val) => setNewWebhook({ ...newWebhook, event: val })}
                                >
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select event" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="inspection.completed">Inspection Completed</SelectItem>
                                        <SelectItem value="inspection.failed">Inspection Failed</SelectItem>
                                        <SelectItem value="task.created">Task Created</SelectItem>
                                        <SelectItem value="task.overdue">Task Overdue</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                        <DialogFooter className="mt-4">
                            <Button type="button" variant="outline" onClick={() => setShowWebhookDialog(false)}>Cancel</Button>
                            <Button type="submit">Add Webhook</Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>
        </ModernPageWrapper>
    );
};

export default IntegrationsPage;
