import { useState, useEffect } from 'react';
import axios from 'axios';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Users, Megaphone, Plus } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HRPage = () => {
  const [employees, setEmployees] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [employeesRes, announcementsRes, statsRes] = await Promise.all([
        axios.get(`${API}/hr/employees`),
        axios.get(`${API}/hr/announcements`),
        axios.get(`${API}/hr/stats`),
      ]);
      setEmployees(employeesRes.data);
      setAnnouncements(announcementsRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to load HR data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModernPageWrapper title="Human Resources" subtitle="Manage employees and communications">
      <div className="space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Total Employees
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.total_employees || 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Megaphone className="h-5 w-5" />
                Announcements
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.total_announcements || 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Megaphone className="h-5 w-5" />
                Published
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.published_announcements || 0}</div>
            </CardContent>
          </Card>
        </div>

        {/* Employees Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Employees ({employees.length})</CardTitle>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Add Employee
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {employees.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No employees found
              </div>
            ) : (
              <div className="space-y-2">
                {employees.slice(0, 10).map((emp: any) => (
                  <div key={emp.id} className="flex justify-between items-center p-3 border rounded-lg">
                    <div>
                      <div className="font-medium">{emp.first_name} {emp.last_name}</div>
                      <div className="text-sm text-muted-foreground">{emp.position || 'No position'}</div>
                    </div>
                    <div className="text-sm text-muted-foreground">{emp.employee_number}</div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Announcements Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recent Announcements ({announcements.length})</CardTitle>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-2" />
                New Announcement
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {announcements.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No announcements found
              </div>
            ) : (
              <div className="space-y-2">
                {announcements.slice(0, 5).map((ann: any) => (
                  <div key={ann.id} className="p-3 border rounded-lg">
                    <div className="font-medium">{ann.title}</div>
                    <div className="text-sm text-muted-foreground mt-1">{ann.content}</div>
                    <div className="text-xs text-muted-foreground mt-2">
                      {new Date(ann.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </ModernPageWrapper>
  );
};

export default HRPage;
