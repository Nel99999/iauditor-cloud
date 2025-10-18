// @ts-nocheck
import { useState, useRef } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Camera, Upload, X, Image as ImageIcon, Loader2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

interface PhotoCaptureProps {
  photos: string[]; // Array of GridFS file IDs
  onChange: (photos: string[]) => void;
  minPhotos?: number;
  maxPhotos?: number;
  required?: boolean;
}

const PhotoCapture = ({ 
  photos = [], 
  onChange, 
  minPhotos = 0, 
  maxPhotos = 10,
  required = false 
}: PhotoCaptureProps) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    // Check max photos limit
    if (photos.length + files.length > maxPhotos) {
      setError(`Maximum ${maxPhotos} photos allowed`);
      return;
    }

    setError(null);
    setUploading(true);

    try {
      const uploadPromises = files.map(async (file) => {
        // Create form data
        const formData = new FormData();
        formData.append('file', file);

        // Upload to GridFS
        const response = await axios.post(`${API}/inspections/upload-photo`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        return response.data.file_id;
      });

      const fileIds = await Promise.all(uploadPromises);
      onChange([...photos, ...fileIds]);
    } catch (err) {
      console.error('Failed to upload photos:', err);
      setError('Failed to upload photos. Please try again.');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleRemovePhoto = (index: number) => {
    const newPhotos = photos.filter((_, i) => i !== index);
    onChange(newPhotos);
    setError(null);
  };

  const handleCameraClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const isValid = photos.length >= minPhotos && photos.length <= maxPhotos;
  const canAddMore = photos.length < maxPhotos;

  return (
    <div className="space-y-4">
      {/* Photo Grid */}
      {photos.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          {photos.map((photoId, index) => (
            <Card key={index} className="relative group">
              <CardContent className="p-2">
                <div className="aspect-square bg-slate-100 dark:bg-slate-800 rounded-lg overflow-hidden relative">
                  <img
                    src={`${API}/inspections/photos/${photoId}`}
                    alt={`Photo ${index + 1}`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.currentTarget.src = '/placeholder-image.png';
                    }}
                  />
                  <Button
                    size="sm"
                    variant="destructive"
                    className="absolute top-2 right-2 h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => handleRemovePhoto(index)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                <div className="text-xs text-center text-muted-foreground mt-1">
                  Photo {index + 1}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Upload Buttons */}
      {canAddMore && (
        <div className="flex gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            multiple={maxPhotos - photos.length > 1}
            onChange={handleFileSelect}
            className="hidden"
          />
          
          <Button
            type="button"
            variant="outline"
            className="flex-1"
            onClick={handleCameraClick}
            disabled={uploading}
          >
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Camera className="h-4 w-4 mr-2" />
                Take Photo
              </>
            )}
          </Button>

          <Button
            type="button"
            variant="outline"
            onClick={handleCameraClick}
            disabled={uploading}
          >
            <Upload className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Status Info */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-2">
          <ImageIcon className="h-4 w-4 text-muted-foreground" />
          <span className="text-muted-foreground">
            {photos.length} / {maxPhotos} photos
          </span>
          {minPhotos > 0 && (
            <Badge variant={isValid ? 'default' : 'destructive'} className="text-xs">
              {minPhotos} min required
            </Badge>
          )}
        </div>
        
        {required && photos.length === 0 && (
          <Badge variant="destructive" className="text-xs">
            Required
          </Badge>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="text-sm text-red-600 bg-red-50 dark:bg-red-950/20 p-2 rounded">
          {error}
        </div>
      )}

      {/* Validation Message */}
      {!isValid && photos.length > 0 && (
        <div className="text-sm text-amber-600 bg-amber-50 dark:bg-amber-950/20 p-2 rounded">
          {photos.length < minPhotos
            ? `Please add at least ${minPhotos - photos.length} more photo(s)`
            : `Please remove ${photos.length - maxPhotos} photo(s)`}
        </div>
      )}
    </div>
  );
};

export default PhotoCapture;
