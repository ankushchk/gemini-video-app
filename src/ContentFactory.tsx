import { useState, type ChangeEvent } from 'react';

import { TrendingUp, Clock, Sparkles, Video, Film, Loader2, Edit } from 'lucide-react';
import type { PodcastAnalysisResult, PodcastClip } from './types';
import ClipDetailView from './ClipDetailView';
import ReelsView from './ReelsView';
import { SubtitleEditor } from './SubtitleEditor';
import Dashboard, { type AnalysisConfig } from './Dashboard';

export default function ContentFactory() {
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [currentStage, setCurrentStage] = useState<number>(0);
  const [clips, setClips] = useState<PodcastClip[]>([]);
  const [selectedClip, setSelectedClip] = useState<PodcastClip | null>(null);
  const [activeReel, setActiveReel] = useState<PodcastClip | null>(null);
  const [editingClip, setEditingClip] = useState<PodcastClip | null>(null);
  const [error, setError] = useState<string | null>(null);

  const stages = [
    'Semantic Chunking',
    'Viral Analysis',
    'Clip Refinement',
    'Platform Optimization',
    'Visual Treatment',
    'Assembly Specs'
  ];

  const handleAnalysis = async (config: AnalysisConfig) => {
    setIsAnalyzing(true);
    setCurrentStage(0);
    setError(null);
    setClips([]);
    
    // Simulate stage progression
    const interval = setInterval(() => {
      setCurrentStage(prev => (prev < stages.length - 1 ? prev + 1 : prev));
    }, 2000);

    try {
      let response;
      
      if (config.file) {
        // Handle File Upload
        const formData = new FormData();
        formData.append('file', config.file);
        if (config.transcript) {
          formData.append('transcript', config.transcript);
        }
        // Pass constraints
        formData.append('start_time', config.startTime.toString());
        formData.append('end_time', config.endTime.toString());
        if (config.topic) formData.append('topic', config.topic);
        if (config.style) formData.append('caption_style', config.style);
        
        response = await fetch('http://localhost:8000/upload-video', {
          method: 'POST',
          body: formData, // No Content-Type header needed, browser sets it for FormData
        });
      } else {
        // Handle YouTube URL
        response = await fetch('http://localhost:8000/analyze-youtube', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            video_url: config.url,
            start_time: config.startTime,
            end_time: config.endTime,
            topic: config.topic,
            caption_style: config.style
          }),
        });
      }

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data: PodcastAnalysisResult = await response.json();
      
      if (data.error) throw new Error(data.error);
      
      // Inject source information
      const processedClips = (data.selected_clips || []).map(clip => ({
        ...clip,
        source_file: data.source_file || config.url // Use returned source_file (local path) or URL
      }));

      setClips(processedClips);
      setCurrentStage(stages.length - 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during analysis');
    } finally {
      clearInterval(interval);
      setIsAnalyzing(false);
    }
  };



  const getScoreColor = (score: number): string => {
    if (score >= 0.9) return 'text-green-500';
    if (score >= 0.75) return 'text-yellow-500';
    return 'text-orange-500';
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleClipUpdate = (updatedClip: PodcastClip) => {
    setClips(prevClips => prevClips.map(c => 
      c.clip_id === updatedClip.clip_id ? updatedClip : c
    ));
    setEditingClip(null);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-neutral-800 bg-neutral-950/80 backdrop-blur-md px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-neutral-900 p-2 rounded-lg border border-neutral-800">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-medium tracking-tight text-white leading-tight">Podcast Content Analyzer</h1>
                <p className="text-xs text-neutral-500 font-medium">Gemini Video 2.0</p>
              </div>
            </div>
            
            <div className="hidden md:block">
               <p className="text-sm text-neutral-500">Transform podcasts and videos into viral short-form content</p>
            </div>
        </div>
      </header>

      {/* Analysis Output Section */}
      {isAnalyzing && (
        <div className="w-full max-w-2xl mx-auto mb-12">
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-8 text-center">
            <Loader2 className="w-8 h-8 text-white animate-spin mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">{stages[currentStage]}</h3>
            <p className="text-neutral-500 font-light">Analyzing content...</p>
          </div>
        </div>
      )}
          
      {/* Clips Grid */}
      {clips.length > 0 && (
        <div className="px-6 pb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <span className="text-sm text-neutral-500">Viral Clips</span>
              <span className="text-xs text-neutral-700">{clips.length}</span>
            </div>
            <div className="text-xs text-neutral-600">
              Sorted by viral potential
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {clips.map((clip) => (
              <div 
                key={clip.clip_id}
                onClick={() => setSelectedClip(clip)}
                className="group cursor-pointer bg-neutral-900 rounded-lg overflow-hidden border border-neutral-800 hover:border-neutral-700 transition-all"
              >
                {/* Thumbnail / Header Area */}
                <div className="relative h-48 bg-neutral-950 overflow-hidden">
                   {clip.thumbnail_path ? (
                    <img 
                      src={`http://localhost:8000/${clip.thumbnail_path}`} 
                      alt={clip.hook}
                      className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105 opacity-90 group-hover:opacity-100"
                    />
                   ) : (
                    <div className="w-full h-full flex items-center justify-center">
                        <Video className="w-12 h-12 text-neutral-800 group-hover:text-neutral-700 transition-colors" />
                    </div>
                   )}
                   
                   {/* Overlay content */}
                   <div className="absolute top-0 left-0 w-full h-full bg-black/20" />
                   
                   {/* Play Reel Button */}
                   <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity z-10 pointer-events-none flex-col gap-3">
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          setActiveReel(clip);
                        }}
                        className="pointer-events-auto bg-white text-black px-4 py-2 rounded-lg font-medium flex items-center gap-2 transform translate-y-2 group-hover:translate-y-0 transition-all hover:bg-neutral-200 shadow-xl"
                      >
                        <Film className="w-4 h-4" />
                        Watch Reel
                      </button>
                      
                      <button 
                         onClick={(e) => {
                           e.stopPropagation();
                           setEditingClip(clip);
                         }}
                         className="pointer-events-auto bg-black/60 backdrop-blur-md text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transform translate-y-2 group-hover:translate-y-0 transition-all hover:bg-black/80 border border-white/10"
                      >
                        <Edit className="w-3 h-3" />
                        Edit Captions
                      </button>
                   </div>
                   
                   <div className={`absolute top-3 right-3 flex items-center gap-1 bg-black px-2 py-1 rounded text-white border border-neutral-800 ${getScoreColor(clip.viral_score)}`}>
                      <TrendingUp className="w-3 h-3" />
                      <span className="text-xs font-medium">{(clip.viral_score * 100).toFixed(0)}%</span>
                   </div>

                   <div className="absolute bottom-3 left-3 right-3">
                      <h3 className="font-medium text-white text-sm line-clamp-2 drop-shadow-md group-hover:text-red-400 transition-colors">
                        {clip.hook}
                      </h3>
                   </div>
                </div>

                {/* Details Body */}
                <div className="p-4 space-y-3">
                  <div className="flex items-center gap-2 text-xs text-neutral-500">
                    <Clock className="w-3 h-3" />
                    <span>{formatTime(clip.refined_start)} - {formatTime(clip.refined_end)}</span>
                    <span>•</span>
                    <span>{clip.refined_duration}s</span>
                  </div>

                  <p className="text-xs text-neutral-500 line-clamp-2">
                    {clip.reasoning}
                  </p>

                  <div className="flex flex-wrap gap-1">
                     {clip.hashtags.slice(0, 2).map((tag, idx) => (
                        <span key={idx} className="text-[10px] bg-neutral-800 text-neutral-400 px-1.5 py-0.5 rounded">
                           {tag}
                        </span>
                     ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {clips.length === 0 && !isAnalyzing && (
        <Dashboard onAnalyze={handleAnalysis} isLoading={isAnalyzing} />
      )}

      {/* Clip Detail Modal */}
      {selectedClip && (
        <ClipDetailView 
          clip={selectedClip} 
          onClose={() => setSelectedClip(null)} 
        />
      )}

      {/* Reels View Modal */}
      {activeReel && (
        <ReelsView 
          clip={activeReel}
          onClose={() => setActiveReel(null)}
        />
      )}

      {/* Subtitle Editor Modal */}
      {editingClip && (
        <SubtitleEditor 
          clip={editingClip}
          onClose={() => setEditingClip(null)}
          onSave={handleClipUpdate}
        />
      )}
    </div>
  );
}