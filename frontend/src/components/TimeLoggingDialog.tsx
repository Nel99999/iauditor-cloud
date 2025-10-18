// @ts-nocheck
import { useState } from 'react';
import axios from 'axios';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Clock, Save } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

interface TimeLoggingDialogProps {
  taskId: string;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const TimeLoggingDialog = ({ taskId, open, onClose, onSuccess }: TimeLoggingDialogProps) => {
  const [hours, setHours] = useState('');
  const [description, setDescription] = useState('');
  const [hourlyRate, setHourlyRate] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async () => {
    if (!hours || parseFloat(hours) <= 0) {
      alert('Please enter valid hours');
      return;
    }

    try {
      setSaving(true);
      await axios.post(`${API}/tasks/${taskId}/log-time`, {
        hours: parseFloat(hours),
        hourly_rate: hourlyRate ? parseFloat(hourlyRate) : null,
        description: description,
      });
      
      onSuccess();
      onClose();
      setHours('');
      setDescription('');
      setHourlyRate('');
    } catch (err) {
      console.error('Failed to log time:', err);
      alert('Failed to log time');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Log Work Hours
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Hours Worked *</Label>
            <Input
              type="number"
              step="0.5"
              min="0.5"
              value={hours}
              onChange={(e) => setHours(e.target.value)}
              placeholder="e.g., 2.5"
            />
          </div>

          <div className="space-y-2">
            <Label>Hourly Rate (optional)</Label>
            <Input
              type="number"
              step="0.01"
              value={hourlyRate}
              onChange={(e) => setHourlyRate(e.target.value)}
              placeholder="e.g., 50.00"
            />
          </div>

          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What did you work on?"
              rows={3}
            />
          </div>

          <div className="flex gap-2">
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={saving} className="flex-1">
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Saving...' : 'Log Time'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default TimeLoggingDialog;
