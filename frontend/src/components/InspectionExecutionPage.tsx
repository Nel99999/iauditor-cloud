// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, CheckCircle, Camera, Save, Trash2, AlertTriangle, MapPin, WifiOff } from 'lucide-react';
import OfflineStorageService, { OfflineInspection } from '../services/OfflineStorageService';
import { v4 as uuidv4 } from 'uuid';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InspectionExecutionPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { templateId, executionId } = useParams();

  const [template, setTemplate] = useState<any | null>(null);
  const [execution, setExecution] = useState<any | null>(null);
  const [answers, setAnswers] = useState<{ [key: string]: any }>({});
  const [findings, setFindings] = useState<string>('');
  const [notes, setNotes] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [isOffline, setIsOffline] = useState<boolean>(!navigator.onLine);
  const [location, setLocation] = useState<{ lat: number, lng: number } | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    if (executionId) {
      loadExecution();
    } else if (templateId) {
      startNewInspection();
    }
  }, [templateId, executionId]);

  const captureLocation = () => {
    if (!navigator.geolocation) {
      setLocationError("Geolocation is not supported by your browser");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude
        });
        setLocationError(null);
      },
      (error) => {
        console.error("Error capturing location:", error);
        setLocationError("Unable to retrieve your location");
      }
    );
  };

  const startNewInspection = async () => {
    try {
      setLoading(true);

      // Capture location immediately
      captureLocation();

      // Load template
      let templateData;
      if (navigator.onLine) {
        const templateRes = await axios.get(`${API}/inspections/templates/${templateId}`);
        templateData = templateRes.data;
        // Cache it for future offline use
        OfflineStorageService.saveTemplate(templateData);
      } else {
        // Try loading from offline cache
        templateData = OfflineStorageService.getTemplate(templateId!);
        if (!templateData) {
          throw new Error("Template not found offline. Please go online to download it first.");
        }
      }
      setTemplate(templateData);

      // Create new execution
      let executionData;
      if (navigator.onLine) {
        const execRes = await axios.post(`${API}/inspections/executions`, {
          template_id: templateId,
          location: location ? { lat: location.lat, lng: location.lng } : null,
        });
        executionData = execRes.data;
      } else {
        // Create local offline execution
        executionData = {
          id: uuidv4(), // Generate local ID
          template_id: templateId,
          status: 'in_progress',
          created_at: new Date().toISOString(),
          answers: [],
          location: location ? { lat: location.lat, lng: location.lng } : null,
        };
      }

      setExecution(executionData);

      // Initialize answers
      const initialAnswers = {};
      templateData.questions.forEach((q: any) => {
        initialAnswers[q.id] = {
          question_id: q.id,
          answer: q.question_type === 'yes_no' ? null : '',
          photo_ids: [],
          notes: '',
        };
      });
      setAnswers(initialAnswers);
    } catch (err: unknown) {
      console.error('Failed to start inspection:', err);
      alert(err instanceof Error ? err.message : 'Failed to start inspection');
      navigate('/inspections');
    } finally {
      setLoading(false);
    }
  };

  const loadExecution = async () => {
    try {
      setLoading(true);

      if (navigator.onLine) {
        const [execRes, templateRes] = await Promise.all([
          axios.get(`${API}/inspections/executions/${executionId}`),
          axios.get(`${API}/inspections/templates/${templateId}`),
        ]);

        setExecution(execRes.data);
        setTemplate(templateRes.data);
        if (execRes.data.location) {
          setLocation(execRes.data.location);
        }

        // Load existing answers
        const loadedAnswers = {};
        execRes.data.answers.forEach((ans: any) => {
          loadedAnswers[ans.question_id] = ans;
        });
        setAnswers(loadedAnswers);
        setNotes(execRes.data.notes || '');
      } else {
        // Load from offline storage
        const offlineInspection = OfflineStorageService.getOfflineInspection(executionId!);
        if (offlineInspection) {
          const templateData = OfflineStorageService.getTemplate(offlineInspection.template_id);
          setExecution(offlineInspection);
          setTemplate(templateData);

          // Map array back to object
          const loadedAnswers = {};
          offlineInspection.answers.forEach((ans: any) => {
            loadedAnswers[ans.question_id] = ans;
          });
          setAnswers(loadedAnswers);
          setNotes(offlineInspection.notes || '');
        } else {
          throw new Error("Inspection not found offline.");
        }
      }

    } catch (err: unknown) {
      console.error('Failed to load execution:', err);
      alert('Failed to load inspection');
      navigate('/inspections');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId: string, value: any) => {
    setAnswers({
      ...answers,
      [questionId]: {
        ...(answers as any)[questionId],
        answer: value,
      },
    });
  };

  const handlePhotoUpload = async (questionId: string, file: File) => {
    if (!navigator.onLine) {
      alert("Photo upload is not yet supported offline.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API}/inspections/upload-photo`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const photoId = response.data.file_id;

      setAnswers({
        ...answers,
        [questionId]: {
          ...(answers as any)[questionId],
          photo_ids: [...((answers as any)[questionId].photo_ids || []), photoId],
        },
      });

      // alert('Photo uploaded successfully!'); // Removed alert for smoother flow
    } catch (err: unknown) {
      console.error('Photo upload failed:', err);
      alert('Failed to upload photo');
    }
  };

  const handleDeletePhoto = (questionId: string, photoIdToDelete: string) => {
    const currentIds = (answers as any)[questionId].photo_ids || [];
    const newIds = currentIds.filter((id: string) => id !== photoIdToDelete);

    setAnswers({
      ...answers,
      [questionId]: {
        ...(answers as any)[questionId],
        photo_ids: newIds,
      },
    });
  };

  const handleFlagFinding = (question: any) => {
    const answer = answers[question.id]?.answer;
    const findingText = `Q${question.order + 1}: ${question.question_text} - ${answer || 'No answer'}`;

    setFindings(prev => prev ? `${prev}\n${findingText}` : findingText);

    // Optional: Scroll to findings section
    const findingsElement = document.getElementById('findings-section');
    if (findingsElement) {
      findingsElement.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleSaveProgress = async () => {
    try {
      setSaving(true);

      if (navigator.onLine) {
        await axios.put(`${API}/inspections/executions/${execution.id}`, {
          answers: Object.values(answers),
          notes,
        });
      } else {
        // Save offline
        const offlineData: OfflineInspection = {
          id: execution.id,
          template_id: template.id,
          answers: Object.values(answers),
          status: 'in_progress',
          created_at: execution.created_at,
          updated_at: new Date().toISOString(),
          synced: false,
          notes,
        };
        OfflineStorageService.saveOfflineInspection(offlineData);
      }

      alert(navigator.onLine ? 'Progress saved!' : 'Progress saved to device (Offline)');
    } catch (err: unknown) {
      console.error('Failed to save:', err);
      alert('Failed to save progress');
    } finally {
      setSaving(false);
    }
  };

  const handleComplete = async () => {
    // Validate required questions
    const unansweredRequired = template.questions.filter(
      (q: any) => q.required && !answers[q.id]?.answer
    );

    if (unansweredRequired.length > 0) {
      alert(`Please answer all required questions (${unansweredRequired.length} remaining)`);
      return;
    }

    try {
      setSaving(true);

      if (navigator.onLine) {
        await axios.post(`${API}/inspections/executions/${execution.id}/complete`, {
          answers: Object.values(answers),
          findings: findings.split('\n').filter((f: any) => f.trim()),
          notes,
        });
      } else {
        // Complete offline
        const offlineData: OfflineInspection = {
          id: execution.id,
          template_id: template.id,
          answers: Object.values(answers),
          status: 'completed',
          created_at: execution.created_at,
          updated_at: new Date().toISOString(),
          synced: false,
          notes,
          findings: findings.split('\n').filter((f: any) => f.trim()),
        };
        OfflineStorageService.saveOfflineInspection(offlineData);
      }

      alert(navigator.onLine ? 'Inspection completed!' : 'Inspection completed offline! It will sync when you are back online.');
      navigate('/inspections');
    } catch (err: unknown) {
      console.error('Failed to complete:', err);
      alert('Failed to complete inspection');
    } finally {
      setSaving(false);
    }
  };

  const getProgress = () => {
    const totalQuestions = template?.questions.length || 0;
    const answeredQuestions = Object.values(answers).filter(
      (a) => a.answer !== null && a.answer !== ''
    ).length;
    return totalQuestions > 0 ? (answeredQuestions / totalQuestions) * 100 : 0;
  };

  const renderQuestion = (question: any, index: number) => {
    const answer = answers[question.id];

    return (
      <Card key={question.id} className="border-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge variant="outline">Q{index + 1}</Badge>
              {question.required && <Badge variant="destructive">Required</Badge>}
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="text-red-500 hover:text-red-700 hover:bg-red-50"
                onClick={() => handleFlagFinding(question)}
                title="Flag as Finding"
              >
                <AlertTriangle className="h-4 w-4" />
              </Button>
              <Badge className="capitalize">{question.question_type.replace('_', ' ')}</Badge>
            </div>
          </div>
          <CardTitle className="text-lg mt-2">{question.question_text}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Text Input */}
          {question.question_type === 'text' && (
            <Textarea
              value={answer?.answer || ''}
              onChange={(e) => handleAnswerChange(question.id, e.target.value)}
              placeholder="Enter your answer..."
              rows={3}
            />
          )}

          {/* Number Input */}
          {question.question_type === 'number' && (
            <Input
              type="number"
              value={answer?.answer || ''}
              onChange={(e) => handleAnswerChange(question.id, e.target.value)}
              placeholder="Enter number..."
            />
          )}

          {/* Yes/No */}
          {question.question_type === 'yes_no' && (
            <RadioGroup
              value={answer?.answer?.toString()}
              onValueChange={(value) => handleAnswerChange(question.id, value === 'true')}
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="true" id={`${question.id}-yes`} />
                <Label htmlFor={`${question.id}-yes`}>Yes</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="false" id={`${question.id}-no`} />
                <Label htmlFor={`${question.id}-no`}>No</Label>
              </div>
            </RadioGroup>
          )}

          {/* Multiple Choice */}
          {question.question_type === 'multiple_choice' && (
            <RadioGroup
              value={answer?.answer}
              onValueChange={(value) => handleAnswerChange(question.id, value)}
            >
              {question.options?.map((option: any, idx: number) => (
                <div key={idx} className="flex items-center space-x-2">
                  <RadioGroupItem value={option} id={`${question.id}-${idx}`} />
                  <Label htmlFor={`${question.id}-${idx}`}>{option}</Label>
                </div>
              ))}
            </RadioGroup>
          )}

          {/* Photo Capture */}
          {question.question_type === 'photo' && (
            <div className="space-y-2">
              <Input
                type="file"
                accept="image/*"
                disabled={isOffline}
                onChange={(e: any) => {
                  if (e.target.files![0]) {
                    handlePhotoUpload(question.id, e.target.files![0]);
                  }
                }}
              />
              {isOffline && <p className="text-xs text-yellow-600">Photo upload unavailable offline</p>}

              {/* Photo Previews */}
              {answer?.photo_ids?.length > 0 && (
                <div className="grid grid-cols-3 gap-2 mt-2">
                  {answer.photo_ids.map((photoId: string) => (
                    <div key={photoId} className="relative group">
                      <img
                        src={`${API}/inspections/photos/${photoId}`}
                        alt="Inspection Evidence"
                        className="w-full h-24 object-cover rounded-md border"
                      />
                      <button
                        onClick={() => handleDeletePhoto(question.id, photoId)}
                        className="absolute top-1 right-1 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Delete Photo"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Notes for this question */}
          <div className="space-y-2">
            <Label className="text-sm text-muted-foreground">Notes (optional)</Label>
            <Input
              value={answer?.notes || ''}
              onChange={(e) => setAnswers({
                ...answers,
                [question.id]: { ...answers[question.id], notes: e.target.value }
              })}
              placeholder="Add notes for this question..."
            />
          </div>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!template || !execution) {
    return <div>Failed to load inspection</div>;
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => navigate('/inspections')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            {template.name}
            {isOffline && <Badge variant="outline" className="text-yellow-600 border-yellow-600"><WifiOff className="h-3 w-3 mr-1" /> Offline Mode</Badge>}
          </h1>
          <p className="text-slate-600 dark:text-slate-400 flex items-center gap-2">
            Inspector: {user?.name}
            {location && (
              <span className="flex items-center text-green-600 text-xs bg-green-50 px-2 py-1 rounded-full">
                <MapPin className="h-3 w-3 mr-1" />
                Location Captured
              </span>
            )}
          </p>
        </div>
        <Badge variant={execution.status === 'completed' ? 'default' : 'secondary'}>
          {execution.status}
        </Badge>
      </div>

      {/* Progress */}
      <Card>
        <CardContent className="pt-6 space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress</span>
            <span>{Math.round(getProgress())}%</span>
          </div>
          <Progress value={getProgress()} />
        </CardContent>
      </Card>

      {/* Questions */}
      <div className="space-y-4">
        {template.questions.map((question: any, index: number) => renderQuestion(question, index))}
      </div>

      {/* Findings & Notes */}
      <Card id="findings-section">
        <CardHeader>
          <CardTitle>Findings & Notes</CardTitle>
          <CardDescription>Document any issues or observations</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Findings (one per line)</Label>
            <Textarea
              value={findings}
              onChange={(e) => setFindings(e.target.value)}
              placeholder="List any issues found..."
              rows={4}
            />
          </div>
          <div className="space-y-2">
            <Label>Additional Notes</Label>
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any additional comments..."
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex gap-2">
        <Button
          variant="outline"
          onClick={handleSaveProgress}
          disabled={saving || execution.status === 'completed'}
        >
          <Save className="h-4 w-4 mr-2" />
          Save Progress
        </Button>
        <Button
          onClick={handleComplete}
          disabled={saving || execution.status === 'completed'}
          className="flex-1"
          data-testid="complete-inspection-btn"
        >
          <CheckCircle className="h-4 w-4 mr-2" />
          Complete Inspection
        </Button>
      </div>
    </div>
  );
};

export default InspectionExecutionPage;
