// @ts-nocheck
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { ModernPageWrapper } from '@/design-system/components';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import PhotoCapture from '@/components/PhotoCapture';
import SignaturePad from '@/components/SignaturePad';
import {
  ArrowLeft, ArrowRight, Check, AlertCircle, MapPin, Clock, Save
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EnhancedInspectionExecutionPage = () => {
  const navigate = useNavigate();
  const { templateId } = useParams();

  const [template, setTemplate] = useState(null);
  const [execution, setExecution] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [findings, setFindings] = useState([]);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [location, setLocation] = useState(null);

  useEffect(() => {
    loadTemplate();
    getLocation();
  }, [templateId]);

  const loadTemplate = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/inspections/templates/${templateId}`);
      setTemplate(response.data);
      
      // Start inspection execution
      const executionResponse = await axios.post(`${API}/inspections/executions`, {
        template_id: templateId,
        location: location,
      });
      setExecution(executionResponse.data);

      // Initialize answers object
      const initialAnswers = {};
      response.data.questions.forEach(q => {
        initialAnswers[q.id] = {
          question_id: q.id,
          answer: null,
          photo_ids: [],
          signature_data: null,
          notes: null,
        };
      });
      setAnswers(initialAnswers);
    } catch (err) {
      console.error('Failed to load template:', err);
      alert('Failed to load inspection template');
      navigate('/inspections');
    } finally {
      setLoading(false);
    }
  };

  const getLocation = () => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          console.error('Failed to get location:', error);
        }
      );
    }
  };

  const handleAnswerChange = (questionId, field, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: {
        ...prev[questionId],
        [field]: value,
      },
    }));
  };

  const isQuestionValid = (question) => {
    const answer = answers[question.id];
    
    // Check if required and has answer
    if (question.required && (answer.answer === null || answer.answer === '')) {
      return false;
    }

    // Check photo requirements
    if (question.photo_required) {
      const photoCount = answer.photo_ids?.length || 0;
      if (photoCount < (question.min_photos || 0)) {
        return false;
      }
    }

    // Check signature requirement
    if (question.signature_required && !answer.signature_data) {
      return false;
    }

    return true;
  };

  const canProceed = () => {
    if (!template) return false;
    const question = template.questions[currentQuestionIndex];
    return isQuestionValid(question);
  };

  const handleNext = () => {
    if (currentQuestionIndex < template.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleComplete = async () => {
    try {
      setSaving(true);
      
      // Convert answers object to array
      const answersArray = Object.values(answers).filter(a => a.answer !== null);

      await axios.post(`${API}/inspections/executions/${execution.id}/complete`, {
        answers: answersArray,
        findings: findings,
        notes: notes,
      });

      alert('Inspection completed successfully!');
      navigate('/inspections');
    } catch (err) {
      console.error('Failed to complete inspection:', err);
      alert('Failed to complete inspection');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!template || !execution) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p>Failed to load inspection</p>
      </div>
    );
  }

  const currentQuestion = template.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / template.questions.length) * 100;
  const isLastQuestion = currentQuestionIndex === template.questions.length - 1;

  return (
    <ModernPageWrapper
      title={template.name}
      subtitle="Complete the inspection"
      actions={
        <Button variant="outline" size="sm" onClick={() => navigate('/inspections')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Cancel
        </Button>
      }
    >
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Progress Bar */}
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Progress</span>
                <Badge variant="outline">
                  Question {currentQuestionIndex + 1} of {template.questions.length}
                </Badge>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          </CardContent>
        </Card>

        {/* Inspection Info */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                <span>{new Date().toLocaleTimeString()}</span>
              </div>
              {location && (
                <div className="flex items-center gap-1">
                  <MapPin className="h-4 w-4" />
                  <span>Location captured</span>
                </div>
              )}
              {template.estimated_duration_minutes && (
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>Est. {template.estimated_duration_minutes}min</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Question Card */}
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="default">Q{currentQuestionIndex + 1}</Badge>
                  {currentQuestion.required && (
                    <Badge variant="destructive" className="text-xs">Required</Badge>
                  )}
                </div>
                <CardTitle className="text-xl">{currentQuestion.question_text}</CardTitle>
                {currentQuestion.help_text && (
                  <CardDescription className="mt-2">
                    {currentQuestion.help_text}
                  </CardDescription>
                )}
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Answer Input */}
            <div className="space-y-4">
              {currentQuestion.question_type === 'yes_no' && (
                <RadioGroup
                  value={answers[currentQuestion.id]?.answer?.toString() || ''}
                  onValueChange={(value) => handleAnswerChange(currentQuestion.id, 'answer', value === 'true')}
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="true" id="yes" />
                    <Label htmlFor="yes" className="text-lg cursor-pointer">Yes</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="false" id="no" />
                    <Label htmlFor="no" className="text-lg cursor-pointer">No</Label>
                  </div>
                </RadioGroup>
              )}

              {currentQuestion.question_type === 'text' && (
                <Textarea
                  value={answers[currentQuestion.id]?.answer || ''}
                  onChange={(e) => handleAnswerChange(currentQuestion.id, 'answer', e.target.value)}
                  placeholder="Enter your answer..."
                  rows={4}
                />
              )}

              {currentQuestion.question_type === 'number' && (
                <Input
                  type="number"
                  value={answers[currentQuestion.id]?.answer || ''}
                  onChange={(e) => handleAnswerChange(currentQuestion.id, 'answer', parseFloat(e.target.value))}
                  placeholder="Enter a number..."
                />
              )}

              {currentQuestion.question_type === 'multiple_choice' && (
                <RadioGroup
                  value={answers[currentQuestion.id]?.answer || ''}
                  onValueChange={(value) => handleAnswerChange(currentQuestion.id, 'answer', value)}
                >
                  {currentQuestion.options?.map((option, idx) => (
                    <div key={idx} className="flex items-center space-x-2">
                      <RadioGroupItem value={option} id={`option-${idx}`} />
                      <Label htmlFor={`option-${idx}`} className="cursor-pointer">{option}</Label>
                    </div>
                  ))}
                </RadioGroup>
              )}
            </div>

            <Separator />

            {/* Photo Capture */}
            {currentQuestion.photo_required && (
              <div className="space-y-2">
                <Label className="text-base font-semibold">Photos</Label>
                <PhotoCapture
                  photos={answers[currentQuestion.id]?.photo_ids || []}
                  onChange={(photos) => handleAnswerChange(currentQuestion.id, 'photo_ids', photos)}
                  minPhotos={currentQuestion.min_photos || 0}
                  maxPhotos={currentQuestion.max_photos || 10}
                  required={currentQuestion.photo_required}
                />
              </div>
            )}

            {/* Signature Capture */}
            {currentQuestion.signature_required && (
              <div className="space-y-2">
                <Label className="text-base font-semibold">Signature</Label>
                <SignaturePad
                  signature={answers[currentQuestion.id]?.signature_data}
                  onChange={(signature) => handleAnswerChange(currentQuestion.id, 'signature_data', signature)}
                  required={currentQuestion.signature_required}
                />
              </div>
            )}

            {/* Notes */}
            <div className="space-y-2">
              <Label>Additional Notes (optional)</Label>
              <Textarea
                value={answers[currentQuestion.id]?.notes || ''}
                onChange={(e) => handleAnswerChange(currentQuestion.id, 'notes', e.target.value)}
                placeholder="Add any additional observations..."
                rows={2}
              />
            </div>

            {/* Validation Message */}
            {!isQuestionValid(currentQuestion) && (
              <div className="flex items-start gap-2 text-sm text-amber-600 bg-amber-50 dark:bg-amber-950/20 p-3 rounded-lg">
                <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium">Please complete the following:</p>
                  <ul className="list-disc list-inside mt-1 space-y-1">
                    {currentQuestion.required && (answers[currentQuestion.id]?.answer === null || answers[currentQuestion.id]?.answer === '') && (
                      <li>Answer is required</li>
                    )}
                    {currentQuestion.photo_required && (answers[currentQuestion.id]?.photo_ids?.length || 0) < (currentQuestion.min_photos || 0) && (
                      <li>At least {currentQuestion.min_photos} photo(s) required</li>
                    )}
                    {currentQuestion.signature_required && !answers[currentQuestion.id]?.signature_data && (
                      <li>Signature is required</li>
                    )}
                  </ul>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Navigation Buttons */}
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentQuestionIndex === 0}
            className="flex-1"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Previous
          </Button>

          {!isLastQuestion ? (
            <Button
              onClick={handleNext}
              disabled={!canProceed()}
              className="flex-1"
            >
              Next
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={handleComplete}
              disabled={!canProceed() || saving}
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              {saving ? (
                <>
                  <Save className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Check className="h-4 w-4 mr-2" />
                  Complete Inspection
                </>
              )}
            </Button>
          )}
        </div>

        {/* Overall Progress */}
        <Card className="bg-slate-50 dark:bg-slate-900">
          <CardContent className="pt-6">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-primary">
                  {Object.values(answers).filter(a => a.answer !== null).length}
                </div>
                <div className="text-sm text-muted-foreground">Answered</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {Object.values(answers).filter(a => a.photo_ids && a.photo_ids.length > 0).length}
                </div>
                <div className="text-sm text-muted-foreground">With Photos</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-indigo-600">
                  {Object.values(answers).filter(a => a.signature_data).length}
                </div>
                <div className="text-sm text-muted-foreground">Signed</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </ModernPageWrapper>
  );
};

export default EnhancedInspectionExecutionPage;
