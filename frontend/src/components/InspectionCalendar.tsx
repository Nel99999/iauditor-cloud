// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Calendar as CalendarIcon, ChevronLeft, ChevronRight, Clock,
  User, Building2, Wrench, AlertCircle, CheckCircle2
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InspectionCalendar = () => {
  const [calendarData, setCalendarData] = useState([]);
  const [units, setUnits] = useState([]);
  const [selectedUnit, setSelectedUnit] = useState('all');
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUnits();
    loadCalendar();
  }, [currentMonth, selectedUnit]);

  const loadUnits = async () => {
    try {
      const response = await axios.get(`${API}/organizations/units`);
      setUnits(response.data);
    } catch (err) {
      console.error('Failed to load units:', err);
    }
  };

  const loadCalendar = async () => {
    try {
      setLoading(true);
      const startDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1);
      const endDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0);
      
      const params = {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
      };
      
      if (selectedUnit !== 'all') {
        params.unit_id = selectedUnit;
      }

      const response = await axios.get(`${API}/inspections/calendar`, { params });
      setCalendarData(response.data.calendar_items || []);
    } catch (err) {
      console.error('Failed to load calendar:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-500"><CheckCircle2 className="h-3 w-3 mr-1" />Completed</Badge>;
      case 'in_progress':
        return <Badge className="bg-blue-500"><Clock className="h-3 w-3 mr-1" />In Progress</Badge>;
      case 'scheduled':
        return <Badge className="bg-gray-500"><CalendarIcon className="h-3 w-3 mr-1" />Scheduled</Badge>;
      case 'overdue':
        return <Badge variant="destructive"><AlertCircle className="h-3 w-3 mr-1" />Overdue</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const previousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const getMonthName = () => {
    return currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  // Group inspections by date
  const inspectionsByDate = {};
  calendarData.forEach(item => {
    const date = new Date(item.due_date).toLocaleDateString();
    if (!inspectionsByDate[date]) {
      inspectionsByDate[date] = [];
    }
    inspectionsByDate[date].push(item);
  });

  // Generate calendar days
  const firstDay = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1);
  const lastDay = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0);
  const daysInMonth = lastDay.getDate();
  const startingDayOfWeek = firstDay.getDay();

  const calendarDays = [];
  for (let i = 0; i < startingDayOfWeek; i++) {
    calendarDays.push(null);
  }
  for (let day = 1; day <= daysInMonth; day++) {
    calendarDays.push(day);
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <CalendarIcon className="h-6 w-6 text-primary" />
            Inspection Calendar
          </h2>
          <p className="text-muted-foreground mt-1">
            View and manage scheduled inspections
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Select value={selectedUnit} onValueChange={setSelectedUnit}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="All Units" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Units</SelectItem>
              {units.map(unit => (
                <SelectItem key={unit.id} value={unit.id}>
                  {unit.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Calendar Navigation */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <Button variant="outline" size="sm" onClick={previousMonth}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <CardTitle className="text-xl">{getMonthName()}</CardTitle>
            <Button variant="outline" size="sm" onClick={nextMonth}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
          ) : (
            <>
              {/* Calendar Grid */}
              <div className="grid grid-cols-7 gap-2">
                {/* Day headers */}
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div key={day} className="text-center font-semibold text-sm text-muted-foreground p-2">
                    {day}
                  </div>
                ))}

                {/* Calendar days */}
                {calendarDays.map((day, index) => {
                  if (day === null) {
                    return <div key={`empty-${index}`} className="p-2 min-h-24"></div>;
                  }

                  const dateStr = new Date(
                    currentMonth.getFullYear(),
                    currentMonth.getMonth(),
                    day
                  ).toLocaleDateString();
                  
                  const dayInspections = inspectionsByDate[dateStr] || [];
                  const isToday = new Date().toLocaleDateString() === dateStr;

                  return (
                    <div
                      key={day}
                      className={`
                        p-2 border rounded-lg min-h-24 transition-colors
                        ${isToday ? 'bg-blue-50 dark:bg-blue-950/20 border-blue-500' : 'hover:bg-slate-50 dark:hover:bg-slate-900'}
                        ${dayInspections.length > 0 ? 'cursor-pointer' : ''}
                      `}
                    >
                      <div className={`text-sm font-semibold mb-1 ${isToday ? 'text-blue-600' : ''}`}>
                        {day}
                      </div>
                      <div className="space-y-1">
                        {dayInspections.slice(0, 2).map((inspection, idx) => (
                          <div
                            key={idx}
                            className="text-xs p-1 bg-slate-100 dark:bg-slate-800 rounded truncate"
                            title={inspection.template_name}
                          >
                            {inspection.template_name.substring(0, 15)}...
                          </div>
                        ))}
                        {dayInspections.length > 2 && (
                          <div className="text-xs text-muted-foreground">
                            +{dayInspections.length - 2} more
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Upcoming Inspections List */}
      <Card>
        <CardHeader>
          <CardTitle>Upcoming Inspections</CardTitle>
          <CardDescription>
            Scheduled inspections for {getMonthName()}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {calendarData.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <CalendarIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No inspections scheduled for this period</p>
            </div>
          ) : (
            <div className="space-y-3">
              {calendarData.slice(0, 10).map((inspection, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{inspection.template_name}</span>
                      {getStatusBadge(inspection.status)}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <CalendarIcon className="h-3 w-3" />
                        <span>{new Date(inspection.due_date).toLocaleDateString()}</span>
                      </div>
                      {inspection.assigned_to_name && (
                        <div className="flex items-center gap-1">
                          <User className="h-3 w-3" />
                          <span>{inspection.assigned_to_name}</span>
                        </div>
                      )}
                      {inspection.unit_name && (
                        <div className="flex items-center gap-1">
                          <Building2 className="h-3 w-3" />
                          <span>{inspection.unit_name}</span>
                        </div>
                      )}
                      {inspection.asset_name && (
                        <div className="flex items-center gap-1">
                          <Wrench className="h-3 w-3" />
                          <span>{inspection.asset_name}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Scheduled</CardTitle>
            <CalendarIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{calendarData.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {calendarData.filter(i => i.status === 'completed').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {calendarData.filter(i => i.status === 'in_progress').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {calendarData.filter(i => i.status === 'overdue').length}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default InspectionCalendar;
