// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Megaphone, AlertCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AnnouncementsPage = () => {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnnouncements();
  }, []);

  const loadAnnouncements = async () => {
    try {
      const response = await axios.get(`${API}/hr/announcements`);
      setAnnouncements(response.data);
    } catch (err) {
      console.error('Failed to load announcements:', err);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      urgent: 'bg-red-500',
      important: 'bg-amber-500',
      normal: 'bg-blue-500',
    };
    return <Badge className={colors[priority] || 'bg-slate-500'}>{priority}</Badge>;
  };

  return (
    <ModernPageWrapper title="Announcements" subtitle="Organization-wide communications">
      <div className="space-y-6">
        <Card>
          <CardHeader><CardTitle>Recent Announcements ({announcements.length})</CardTitle></CardHeader>
          <CardContent>
            {announcements.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">No announcements yet</div>
            ) : (
              <div className="space-y-4">
                {announcements.map((ann) => (
                  <Card key={ann.id} className="border-l-4 border-l-primary">
                    <CardContent className="pt-6">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Megaphone className="h-5 w-5 text-primary" />
                            <h3 className="font-bold text-lg">{ann.title}</h3>
                            {getPriorityBadge(ann.priority)}
                          </div>
                          <p className="text-sm mb-2">{ann.content}</p>
                          <div className="text-xs text-muted-foreground">
                            {ann.published ? `Published: ${ann.published_at?.substring(0, 10)}` : 'Draft'}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </ModernPageWrapper>
  );
};

export default AnnouncementsPage;
