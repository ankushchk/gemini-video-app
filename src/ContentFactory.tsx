import { useState, type ChangeEvent } from 'react';
import { Upload, TrendingUp, Clock, FileText, User, MessageSquare, Sparkles } from 'lucide-react';
import type { PodcastAnalysisResult, PodcastClip, PodcastMetadata } from './types';
import ClipDetailView from './ClipDetailView';

export default function ContentFactory() {
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [currentStage, setCurrentStage] = useState<number>(0);
  const [clips, setClips] = useState<PodcastClip[]>([]);
  const [selectedClip, setSelectedClip] = useState<PodcastClip | null>(null);
  const [metadata, setMetadata] = useState<PodcastMetadata>({
    guest: '',
    topic: '',
    tone: ''
  });

  const stages = [
    'Semantic Chunking',
    'Viral Analysis',
    'Clip Refinement',
    'Platform Optimization',
    'Visual Treatment',
    'Assembly Specs'
  ];

  const handleUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check file type
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !['txt', 'srt', 'vtt', 'mp4', 'mov', 'avi', 'mkv'].includes(ext)) {
      alert('Please upload a transcript (.txt, .srt, .vtt) or video file (.mp4, .mov, .avi)');
      return;
    }

    setIsAnalyzing(true);
    setCurrentStage(0);
    setClips([]);

    const formData = new FormData();
    formData.append('file', file);
    
    // Add metadata if provided
    if (metadata.guest) formData.append('guest', metadata.guest);
    if (metadata.topic) formData.append('topic', metadata.topic);
    if (metadata.tone) formData.append('tone', metadata.tone);

    try {
      // Simulate stage progression
      const stageInterval = setInterval(() => {
        setCurrentStage(prev => Math.min(prev + 1, 5));
      }, 3000); // Slower progress for potentially larger video files

      // Determine endpoint based on file type
      const isVideo = ['mp4', 'mov', 'avi', 'mkv'].includes(ext);
      const endpoint = isVideo 
        ? 'http://localhost:8000/upload-video' 
        : 'http://localhost:8000/analyze-podcast';

      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      clearInterval(stageInterval);
      setCurrentStage(6);

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data: PodcastAnalysisResult = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      console.log('Analysis result:', data);
      
      // Sort clips by viral score and add source file
      const sortedClips = (data.selected_clips || [])
        .sort((a, b) => b.viral_score - a.viral_score)
        .map(clip => ({
          ...clip,
          source_file: data.source_file // Pass the video path to the clip
        }));
      setClips(sortedClips);

    } catch (error) {
      console.error('Error analyzing content:', error);
      alert(`Failed to analyze content: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsAnalyzing(false);
      setCurrentStage(0);
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

  return (
    <div className="min-h-screen bg-neutral-950 text-white">
      {/* Header */}
      <div className="border-b border-neutral-800 px-6 py-4">
        <div className="flex items-center gap-3">
          <Sparkles className="w-6 h-6 text-purple-500" />
          <h1 className="text-xl font-light tracking-wide">Podcast Content Analyzer</h1>
        </div>
        <p className="text-sm text-neutral-500 mt-1">Transform podcasts and videos into viral short-form content</p>
      </div>

      {/* Metadata Form */}
      <div className="px-6 py-6 border-b border-neutral-800">
        <h2 className="text-sm text-neutral-400 mb-4">Optional Metadata (improves analysis)</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="flex items-center gap-2 text-xs text-neutral-500 mb-2">
              <User className="w-3 h-3" />
              Guest Name
            </label>
            <input
              type="text"
              value={metadata.guest}
              onChange={(e) => setMetadata({ ...metadata, guest: e.target.value })}
              placeholder="e.g., Elon Musk"
              className="w-full bg-neutral-900 border border-neutral-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-neutral-700"
              disabled={isAnalyzing}
            />
          </div>
          <div>
            <label className="flex items-center gap-2 text-xs text-neutral-500 mb-2">
              <MessageSquare className="w-3 h-3" />
              Topic
            </label>
            <input
              type="text"
              value={metadata.topic}
              onChange={(e) => setMetadata({ ...metadata, topic: e.target.value })}
              placeholder="e.g., Artificial Intelligence"
              className="w-full bg-neutral-900 border border-neutral-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-neutral-700"
              disabled={isAnalyzing}
            />
          </div>
          <div>
            <label className="flex items-center gap-2 text-xs text-neutral-500 mb-2">
              <FileText className="w-3 h-3" />
              Tone
            </label>
            <input
              type="text"
              value={metadata.tone}
              onChange={(e) => setMetadata({ ...metadata, tone: e.target.value })}
              placeholder="e.g., Serious, thought-provoking"
              className="w-full bg-neutral-900 border border-neutral-800 rounded px-3 py-2 text-sm focus:outline-none focus:border-neutral-700"
              disabled={isAnalyzing}
            />
          </div>
        </div>
      </div>

      {/* Upload Section */}
      <div className="px-6 py-8">
        <label className="block">
          <input
            type="file"
            accept=".txt,.srt,.vtt,.mp4,.mov,.avi,.mkv"
            onChange={handleUpload}
            className="hidden"
            disabled={isAnalyzing}
          />
          <div className="border-2 border-dashed border-neutral-800 rounded-lg p-12 cursor-pointer hover:border-neutral-700 transition-colors flex flex-col items-center gap-3">
            <Upload className="w-8 h-8 text-neutral-600" />
            <span className="text-sm text-neutral-500">
              {isAnalyzing ? 'Analyzing content...' : 'Upload transcript (.txt, .srt) or video (.mp4)'}
            </span>
            {!isAnalyzing && (
              <span className="text-xs text-neutral-700">
                Supports transcripts (TXT, SRT, VTT) and videos (MP4, MOV, AVI)
              </span>
            )}
          </div>
        </label>

        {/* Stage Progress */}
        {isAnalyzing && (
          <div className="mt-6">
            <div className="flex justify-between text-xs text-neutral-500 mb-3">
              <span>Processing Stages</span>
              <span>{currentStage}/6</span>
            </div>
            <div className="space-y-2">
              {stages.map((stage, idx) => (
                <div key={idx} className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${
                    idx < currentStage ? 'bg-green-500' : 
                    idx === currentStage ? 'bg-yellow-500 animate-pulse' : 
                    'bg-neutral-800'
                  }`} />
                  <span className={`text-xs ${
                    idx <= currentStage ? 'text-neutral-300' : 'text-neutral-700'
                  }`}>
                    {idx + 1}. {stage}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

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
                {/* Clip Header */}
                <div className="p-4 border-b border-neutral-800">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-neutral-600">{clip.clip_id}</span>
                    <div className="flex items-center gap-1">
                      <TrendingUp className="w-3 h-3 text-neutral-600" />
                      <span className={`text-sm font-medium ${getScoreColor(clip.viral_score)}`}>
                        {(clip.viral_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-neutral-500">
                    <Clock className="w-3 h-3" />
                    <span>{formatTime(clip.refined_start)} - {formatTime(clip.refined_end)}</span>
                    <span>•</span>
                    <span>{clip.refined_duration}s</span>
                  </div>
                </div>

                {/* Hook Preview */}
                <div className="p-4">
                  <div className="text-xs text-neutral-600 mb-2">Hook:</div>
                  <p className="text-sm text-white line-clamp-2 group-hover:text-purple-400 transition-colors">
                    {clip.hook}
                  </p>
                </div>

                {/* Metadata Preview */}
                <div className="p-4 pt-0 space-y-2">
                  <div className="flex flex-wrap gap-1">
                    {clip.hashtags.slice(0, 3).map((tag, idx) => (
                      <span key={idx} className="text-xs bg-neutral-800 px-2 py-0.5 rounded text-blue-400">
                        {tag}
                      </span>
                    ))}
                    {clip.hashtags.length > 3 && (
                      <span className="text-xs text-neutral-600">
                        +{clip.hashtags.length - 3}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-neutral-600">
                    {clip.visual_beats.length} visual beats • {clip.captions.length} captions
                  </div>
                </div>

                {/* View Details Button */}
                <div className="p-4 pt-0">
                  <div className="text-xs text-purple-500 group-hover:text-purple-400 transition-colors">
                    Click to view full details →
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
          <p className="text-neutral-700 text-sm">Upload a podcast transcript to generate viral clips</p>
        </div>
      )}

      {/* Clip Detail Modal */}
      {selectedClip && (
        <ClipDetailView 
          clip={selectedClip} 
          onClose={() => setSelectedClip(null)} 
        />
      )}
    </div>
  );
}