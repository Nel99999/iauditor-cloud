import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, CheckCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChecklistExecutionPage = () => {
  const navigate = useNavigate();
  // const { user } = useAuth();
  const { executionId } = useParams();
  
  const [execution, setExecution] = useState<any | null>(null);
  const [template, setTemplate] = useState<any | null>(null);
  const [items, setItems] = useState<any[]>([]);
  const [notes, setNotes] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);

  useEffect(() => {
    loadExecution();
  }, [executionId]);

  const loadExecution = async () => {
    try {
      setLoading(true);
      const execRes = await axios.get(`${API}/checklists/executions/${executionId}`);
      setExecution(execRes.data);
      setItems(execRes.data.items || []);
      setNotes(execRes.data.notes || '');
      
      const templateRes = await axios.get(`${API}/checklists/templates/${execRes.data.template_id}`);
      setTemplate(templateRes.data);
    } catch (err: unknown) {
      console.error('Failed to load checklist:', err);
      alert('Failed to load checklist');
      navigate('/checklists');
    } finally {
      setLoading(false);
    }
  };

  const handleItemToggle = (itemId: string, checked: boolean) => {
    const newItems = items.map((item: any) => 
      item.item_id === itemId 
        ? { ...item, completed: checked, completed_at: checked ? new Date().toISOString() : null }
        : item
    );
    setItems(newItems);
  };

  const getProgress = () => {
    if (!items.length) return 0;
    const completed = items.filter((i: any) => i.completed).length;
    return (completed / items.length) * 100;
  };

  const handleComplete = async () => {
    try {
      setSaving(true);
      await axios.post(`${API}/checklists/executions/${executionId}/complete`, {
        items,
        notes,
      });
      alert('Checklist completed!');
      navigate('/checklists');
    } catch (err: unknown) {
      alert('Failed to complete checklist');
    } finally {
      setSaving(false);
    }
  };

  if (loading || !execution || !template) {
    return <div className="flex items-center justify-center h-96"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div></div>;
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => navigate('/checklists')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{execution.template_name}</h1>
          <p className="text-slate-600 dark:text-slate-400">Date: {execution.date}</p>
        </div>
        <Badge variant={execution.status === 'completed' ? 'default' : 'secondary'}>
          {execution.status}
        </Badge>
      </div>

      <Card>
        <CardContent className="pt-6 space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress</span>
            <span>{Math.round(getProgress())}%</span>
          </div>
          <Progress value={getProgress()} />
        </CardContent>
      </Card>

      <div className="space-y-4">
        {template.items.map((templateItem: any, index: number) => {
          const itemState = items.find((i: any) => i.item_id === templateItem.id) || { completed: false };
          
          return (
            <Card key={templateItem.id}>
              <CardContent className="pt-6">
                <div className="flex items-start gap-4">
                  <Checkbox
                    checked={itemState.completed}
                    onCheckedChange={(checked) => handleItemToggle(templateItem.id, checked)}
                    disabled={execution.status === 'completed'}
                    data-testid={`checklist-item-checkbox-${index}`}
                  />
                  <div className="flex-1">
                    <p className={`font-medium ${itemState.completed ? 'line-through text-slate-500' : ''}`}>
                      {templateItem.text}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardContent className="pt-6 space-y-2">
          <label className="text-sm font-medium">Notes</label>
          <Textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add any notes..."
            rows={4}
            disabled={execution.status === 'completed'}
          />
        </CardContent>
      </Card>

      {execution.status !== 'completed' && (
        <Button
          onClick={handleComplete}
          disabled={saving}
          className="w-full"
          data-testid="complete-checklist-btn"
        >
          <CheckCircle className="h-4 w-4 mr-2" />
          Complete Checklist
        </Button>
      )}
    </div>
  );
};

export default ChecklistExecutionPage;
