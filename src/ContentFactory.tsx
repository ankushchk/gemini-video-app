import React, { useState, type ChangeEvent } from 'react';
import { Upload, TrendingUp, Clock } from 'lucide-react';

interface Clip {
  id: number;
  thumbnail: string;
  viralScore: number;
  duration: number;
  hook: string;
}

export default function ContentFactory() {
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [clips, setClips] = useState<Clip[]>([]);

  const handleUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsAnalyzing(true);
    setProgress(0);
    setClips([]);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Simulate progress while waiting for backend
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 1, 90));
      }, 500);

      const response = await fetch('http://localhost:8000/upload-video', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      console.log('Analysis result:', data);
      
      // Assumption: data is a list of objects or has a key with the list
      // Based on scout_agent prompt, it returns a JSON object. We expect it to key "hooks" or be an array.
      // Let's assume the prompt returns an array of objects directly or wrapped.
      // We'll inspect the data structure. If it's pure JSON array from the prompt:
      
      const hooks = Array.isArray(data) ? data : (data.hooks || []);
      
      const newClips: Clip[] = hooks.map((hook: any, index: number) => ({
        id: index + 1,
        thumbnail: `https://picsum.photos/seed/${index + 1}/400/600`, // Placeholder
        viralScore: hook['Viral Score'] || hook.viralScore || 0,
        duration: 15, // Default or calculate from timestamps if available
        hook: hook['reason'] || hook.reason || 'No description'
      }));

      setClips(newClips.sort((a, b) => b.viralScore - a.viralScore));

    } catch (error) {
      console.error('Error uploading video:', error);
      alert('Failed to analyze video');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Removed generateClips as it is now handled in handleUpload



  const getScoreColor = (score: number): string => {
    if (score >= 90) return 'text-green-500';
    if (score >= 75) return 'text-yellow-500';
    return 'text-orange-500';
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      {/* Header */}
      <div className="border-b border-neutral-800 px-6 py-4">
        <h1 className="text-xl font-light tracking-wide">Content Factory</h1>
      </div>

      {/* Upload Section */}
      <div className="px-6 py-8">
        <label className="block">
          <input
            type="file"
            accept="video/*"
            onChange={handleUpload}
            className="hidden"
            disabled={isAnalyzing}
          />
          <div className="border-2 border-dashed border-neutral-800 rounded-lg p-12 cursor-pointer hover:border-neutral-700 transition-colors flex flex-col items-center gap-3">
            <Upload className="w-8 h-8 text-neutral-600" />
            <span className="text-sm text-neutral-500">
              {isAnalyzing ? 'Analyzing...' : 'Upload long-form video'}
            </span>
          </div>
        </label>

        {/* Progress Bar */}
        {isAnalyzing && (
          <div className="mt-6">
            <div className="flex justify-between text-xs text-neutral-500 mb-2">
              <span>Processing</span>
              <span>{progress}%</span>
            </div>
            <div className="h-1 bg-neutral-900 rounded-full overflow-hidden">
              <div 
                className="h-full bg-white transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Clips Grid */}
      {clips.length > 0 && (
        <div className="px-6 pb-8">
          <div className="flex items-center gap-2 mb-6">
            <span className="text-sm text-neutral-500">Generated Clips</span>
            <span className="text-xs text-neutral-700">{clips.length}</span>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
            {clips.map((clip) => (
              <div 
                key={clip.id}
                className="group cursor-pointer"
              >
                <div className="relative aspect-[9/16] bg-neutral-900 rounded-lg overflow-hidden mb-2">
                  <img 
                    src={clip.thumbnail} 
                    alt={`Clip ${clip.id}`}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="absolute bottom-2 left-2 right-2">
                      <p className="text-xs text-white/90">{clip.hook}</p>
                    </div>
                  </div>
                  <div className="absolute top-2 right-2 bg-black/70 px-1.5 py-0.5 rounded text-xs flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {clip.duration}s
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-neutral-600">#{clip.id}</span>
                  <div className="flex items-center gap-1">
                    <TrendingUp className="w-3 h-3 text-neutral-600" />
                    <span className={`text-xs font-medium ${getScoreColor(clip.viralScore)}`}>
                      {clip.viralScore}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {clips.length === 0 && !isAnalyzing && (
        <div className="px-6 py-16 text-center">
          <p className="text-neutral-700 text-sm">Upload a video to generate clips</p>
        </div>
      )}
    </div>
  );
}