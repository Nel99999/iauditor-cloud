// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { GraduationCap, BookOpen, AlertCircle, TrendingUp } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TrainingPage = () => {
  const [courses, setCourses] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [coursesRes, statsRes] = await Promise.all([
        axios.get(`${API}/training/courses`),
        axios.get(`${API}/training/stats`),
      ]);
      setCourses(coursesRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Failed to load training:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModernPageWrapper title="Training & Competency" subtitle="Learning management system">
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Total Courses</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.total_courses || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Enrollments</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.total_enrollments || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Completed (Month)</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold">{stats?.completed_this_month || 0}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm text-red-600">Expired Certs</CardTitle></CardHeader>
            <CardContent><div className="text-2xl font-bold text-red-600">{stats?.expired_certifications || 0}</div></CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Training Courses ({courses.length})</CardTitle></CardHeader>
          <CardContent>
            {courses.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">No courses yet</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {courses.map((course) => (
                  <Card key={course.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-center gap-2">
                        <GraduationCap className="h-5 w-5 text-primary" />
                        <CardTitle className="text-base">{course.name}</CardTitle>
                      </div>
                      <div className="text-sm text-muted-foreground">{course.course_code}</div>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div><span className="text-muted-foreground">Type:</span> {course.course_type}</div>
                      <div><span className="text-muted-foreground">Duration:</span> {course.duration_hours}h</div>
                      {course.valid_for_years && (
                        <div><span className="text-muted-foreground">Valid:</span> {course.valid_for_years} years</div>
                      )}
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

export default TrainingPage;
