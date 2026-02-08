import { useState } from 'react';
import { Clock, Sparkles, Type, Search, Upload, FileVideo, FileText, Youtube } from 'lucide-react';

interface DashboardProps {
  onAnalyze: (config: AnalysisConfig) => void;
  isLoading: boolean;
}

export interface AnalysisConfig {
  url: string;
  startTime: number;
  endTime: number;
  topic: string;
  style: string;
  file?: File;
  transcript?: File;
}

interface VideoMeta {
  title: string;
  duration: number;
  thumbnail: string;
}

export default function Dashboard({ onAnalyze, isLoading }: DashboardProps) {
  const [url, setUrl] = useState('');
  const [meta, setMeta] = useState<VideoMeta | null>(null);
  const [loadingMeta, setLoadingMeta] = useState(false);
  
  // Config State
  const [range, setRange] = useState<[number, number]>([0, 600]); // Default 10 mins
  const [topic, setTopic] = useState('');
  const [activeStyle, setActiveStyle] = useState('karaoke');
  
  // Upload State
  const [uploadMode, setUploadMode] = useState<'youtube' | 'file'>('youtube');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedTranscript, setSelectedTranscript] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      // Create fake meta for local file to show preview
      setMeta({
        title: file.name,
        duration: 600, // Default 10 mins for local files as we can't easily get duration without reading it
        thumbnail: URL.createObjectURL(file) // Create object URL for preview if it's an image/video
      });
    }
  };

  const fetchMeta = async () => {
    if (!url.includes('youtube.com') && !url.includes('youtu.be')) return;
    
    setLoadingMeta(true);
    try {
      const res = await fetch('http://localhost:8000/get-video-meta', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_url: url })
      });
      const data = await res.json();
      if (data.title) {
        setMeta(data);
        setRange([0, Math.min(data.duration, 600)]); // Cap at 10m initial view
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingMeta(false);
    }
  };



  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, '0')}`;
  };

  const handleTimeInput = (type: 'start' | 'end', value: string) => {
    // Parse MM:SS or S
    const parts = value.split(':');
    let seconds = 0;
    if (parts.length === 2) {
      seconds = parseInt(parts[0]) * 60 + parseInt(parts[1]);
    } else {
      seconds = parseInt(parts[0]);
    }
    
    if (isNaN(seconds)) return;
    
    // Clamp
    if (meta) {
      seconds = Math.max(0, Math.min(seconds, meta.duration));
    }
    
    const newRange = [...range] as [number, number];
    if (type === 'start') {
       // Don't let start go past end
       if (seconds < newRange[1]) newRange[0] = seconds;
    } else {
       // Don't let end go before start
       if (seconds > newRange[0]) newRange[1] = seconds;
    }
    setRange(newRange);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      
      {/* 1. Content Input Section */}
      <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-8 mb-8">
        <h1 className="text-3xl font-light text-white mb-2 tracking-tight">
          Create Viral Clips
        </h1>
        <p className="text-neutral-500 mb-8 font-light">
          {uploadMode === 'youtube' 
            ? "Paste a YouTube link to identify hooks, add captions, and go viral." 
            : "Upload your video manually to process it locally."}
        </p>

        {/* Custom Tab Switcher */}
        <div className="flex gap-4 mb-6 border-b border-neutral-800 pb-1">
          <button 
            onClick={() => { setUploadMode('youtube'); setMeta(null); }}
            className={`pb-3 px-2 text-sm font-medium transition-all relative ${
              uploadMode === 'youtube' ? 'text-white' : 'text-neutral-500 hover:text-neutral-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <Youtube className="w-4 h-4" />
              YouTube Link
            </div>
            {uploadMode === 'youtube' && (
              <div className="absolute bottom-0 left-0 w-full h-[1px] bg-white" />
            )}
          </button>
          <button 
            onClick={() => { setUploadMode('file'); setMeta(null); }}
            className={`pb-3 px-2 text-sm font-medium transition-all relative ${
              uploadMode === 'file' ? 'text-white' : 'text-neutral-500 hover:text-neutral-300'
            }`}
          >
             <div className="flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Upload File
            </div>
            {uploadMode === 'file' && (
              <div className="absolute bottom-0 left-0 w-full h-[1px] bg-white" />
            )}
          </button>
        </div>

        {uploadMode === 'youtube' ? (
          <div className="flex gap-4">
            <input 
              type="text" 
              placeholder="Required: Paste YouTube Link"
              className="flex-1 bg-neutral-950 border border-neutral-800 rounded-lg px-4 py-4 text-white placeholder-neutral-600 focus:outline-none focus:border-neutral-500 transition-all font-light"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onBlur={fetchMeta}
              onKeyDown={(e) => e.key === 'Enter' && fetchMeta()}
            />
            {meta ? (
              <button 
                  onClick={() => setMeta(null)}
                  className="px-6 py-4 border border-neutral-800 hover:bg-neutral-900 text-white rounded-lg transition-all"
              >
                  Clear
              </button>
            ) : (
              <button 
                  onClick={fetchMeta}
                  disabled={loadingMeta || !url}
                  className="px-8 py-4 bg-white hover:bg-neutral-200 disabled:opacity-50 text-black font-medium rounded-lg transition-all flex items-center gap-2"
              >
                  {loadingMeta ? 'Loading...' : 'Start'}
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
             {/* Video Upload Area */}
             <div className="border border-dashed border-neutral-700 bg-neutral-950/50 rounded-lg p-8 text-center hover:border-neutral-500 transition-colors cursor-pointer relative">
                <input 
                  type="file" 
                  accept="video/*,audio/*"
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="flex flex-col items-center gap-2 pointer-events-none">
                   {selectedFile ? (
                     <>
                        <FileVideo className="w-8 h-8 text-green-500" />
                        <span className="text-white font-medium">{selectedFile.name}</span>
                        <span className="text-xs text-neutral-500">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
                     </>
                   ) : (
                     <>
                        <Upload className="w-8 h-8 text-neutral-500" />
                        <span className="text-neutral-400">Click to upload video or audio</span>
                        <span className="text-xs text-neutral-600">MP4, MOV, MP3, WAV supported</span>
                     </>
                   )}
                </div>
             </div>

             {/* Optional Transcript */}
             {selectedFile && (
                <div className="flex items-center gap-4 bg-neutral-950 border border-neutral-800 p-4 rounded-lg">
                   <div className="p-2 bg-neutral-900 rounded">
                      <FileText className="w-5 h-5 text-neutral-400" />
                   </div>
                   <div className="flex-1">
                      <p className="text-sm text-neutral-300">Manual Transcript (Optional)</p>
                      <p className="text-xs text-neutral-600">Improve accuracy by providing a script</p>
                   </div>
                   <label className="cursor-pointer px-4 py-2 bg-neutral-900 border border-neutral-800 rounded text-xs text-white hover:bg-neutral-800 transition-colors">
                      {selectedTranscript ? 'Change' : 'Upload .txt'}
                      <input 
                        type="file" 
                        accept=".txt,.vtt,.srt" 
                        className="hidden" 
                        onChange={(e) => e.target.files && setSelectedTranscript(e.target.files[0])}
                      />
                   </label>
                   {selectedTranscript && (
                      <span className="text-xs text-green-500">{selectedTranscript.name}</span>
                   )}
                </div>
             )}
          </div>
        )}
      </div>

      {/* 2. Configuration Dashboard (Shown after Meta fetch) */}
      {meta && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-in slide-in-from-bottom-4 duration-500 fade-in">
            
            {/* Left Col: Video Preview & Timeframe */}
            <div className="space-y-6">
                <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden">
                    <img src={meta.thumbnail} alt={meta.title} className="w-full h-48 object-cover opacity-80" />
                    <div className="p-4">
                        <h3 className="font-bold text-white text-lg line-clamp-1">{meta.title}</h3>
                        <p className="text-neutral-400 text-sm mt-1">{formatTime(meta.duration)} • {meta.title} Channel</p>
                    </div>
                </div>

                <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6">
                    <div className="flex items-center gap-2 mb-4 text-purple-400">
                        <Clock className="w-5 h-5" />
                        <h2 className="font-bold">Processing Timeframe</h2>
                    </div>
                    <p className="text-xs text-neutral-400 mb-6 font-light">Select a segment to analyze (Credit Saver)</p>
                    
                    <div className="px-2">
                        {/* Custom Dual Range Slider */}
                        <div className="relative h-12 mb-4 group">
                           {/* Track Background */}
                           <div className="absolute top-1/2 left-0 w-full h-1 bg-neutral-800 rounded-full -translate-y-1/2 overflow-hidden">
                              {/* Active Range Bar */}
                              <div 
                                  className="absolute h-full bg-white opacity-80"
                                  style={{ 
                                      left: `${(range[0] / meta.duration) * 100}%`, 
                                      right: `${100 - (range[1] / meta.duration) * 100}%` 
                                  }}
                              />
                           </div>
                           
                           {/* Invisible Inputs */}
                           <input 
                              type="range" 
                              min={0} 
                              max={meta.duration} 
                              value={range[0]} 
                              onChange={(e) => {
                                 const val = Math.min(Number(e.target.value), range[1] - 1);
                                 setRange([val, range[1]]);
                              }}
                              className="absolute top-1/2 -translate-y-1/2 w-full h-1 pointer-events-none appearance-none bg-transparent z-20 range-sm"
                           />
                           <input 
                              type="range" 
                              min={0} 
                              max={meta.duration} 
                              value={range[1]} 
                              onChange={(e) => {
                                 const val = Math.max(Number(e.target.value), range[0] + 1);
                                 setRange([range[0], val]);
                              }}
                              className="absolute top-1/2 -translate-y-1/2 w-full h-1 pointer-events-none appearance-none bg-transparent z-20 range-sm"
                           />
                           
                           {/* Custom Style for Thumbs */}
                           <style>{`
                              /* Webkit (Chrome, Safari, Edge) */
                              .range-sm::-webkit-slider-thumb {
                                -webkit-appearance: none;
                                appearance: none;
                                width: 16px;
                                height: 16px;
                                border-radius: 50%;
                                background: white;
                                cursor: pointer;
                                pointer-events: auto;
                                border: 2px solid #171717; /* neutral-900 for contrast */
                                box-shadow: 0 0 0 2px rgba(255,255,255,0.2);
                              }
                              .range-sm::-webkit-slider-thumb:hover {
                                transform: scale(1.1);
                              }
                              
                              /* Moz (Firefox) */
                              .range-sm::-moz-range-thumb {
                                width: 16px;
                                height: 16px;
                                border-radius: 50%;
                                background: white;
                                cursor: pointer;
                                pointer-events: auto;
                                border: 2px solid #171717;
                                border: none;
                              }
                           `}</style>
                        </div>

                        {/* Precise Numeric Control */}
                        <div className="flex justify-between items-center bg-neutral-950 rounded-lg p-3 border border-neutral-800">
                             <div className="flex flex-col gap-1">
                                <label className="text-[10px] uppercase text-neutral-500 font-bold tracking-wider">Start</label>
                                <input 
                                  type="text" 
                                  className="bg-transparent text-white font-mono text-sm w-16 focus:outline-none border-b border-transparent focus:border-neutral-700 text-center"
                                  value={formatTime(range[0])}
                                  onChange={(e) => handleTimeInput('start', e.target.value)}
                                />
                             </div>
                             
                             <div className="h-8 w-[1px] bg-neutral-800 mx-4"></div>
                             
                             <div className="flex flex-col gap-1 text-right">
                                <label className="text-[10px] uppercase text-neutral-500 font-bold tracking-wider">End</label>
                                <input 
                                  type="text" 
                                  className="bg-transparent text-white font-mono text-sm w-16 focus:outline-none border-b border-transparent focus:border-neutral-700 text-center"
                                  value={formatTime(range[1])}
                                  onChange={(e) => handleTimeInput('end', e.target.value)}
                                />
                             </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Col: Topic & Style */}
            <div className="space-y-6">
                
                {/* Topic Input */}
                <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6">
                    <div className="flex items-center gap-2 mb-4 text-blue-400">
                        <Search className="w-5 h-5" />
                        <h2 className="font-bold">What moments do you want?</h2>
                    </div>
                    <textarea 
                        className="w-full bg-black/30 border border-neutral-700 rounded-lg p-3 text-white text-sm focus:border-blue-500 focus:outline-none min-h-[80px]"
                        placeholder="e.g. Funny moments, Startup advice, High energy debates..."
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                    />
                </div>

                {/* Style Selector */}
                <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6">
                    <div className="flex items-center gap-2 mb-4 text-green-400">
                        <Type className="w-5 h-5" />
                        <h2 className="font-bold">Caption Style</h2>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3">
                        {['karaoke', 'minimal', 'bold', 'neon'].map((style) => (
                            <button
                                key={style}
                                onClick={() => setActiveStyle(style)}
                                className={`p-3 rounded-lg border text-sm font-medium transition-all ${
                                    activeStyle === style 
                                    ? 'bg-green-500/20 border-green-500 text-green-400' 
                                    : 'bg-black/20 border-neutral-700 text-neutral-400 hover:border-neutral-500'
                                }`}
                            >
                                {style.charAt(0).toUpperCase() + style.slice(1)}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Main Action */}
                <button
                    onClick={() => onAnalyze({
                        url,
                        startTime: range[0],
                        endTime: range[1],
                        topic,
                        style: activeStyle,
                        file: selectedFile || undefined,
                        transcript: selectedTranscript || undefined
                    })}
                    disabled={isLoading}
                    className="w-full py-4 bg-white hover:bg-neutral-200 text-black font-medium text-lg rounded-xl transition-all flex justify-center items-center gap-3"
                >
                    {isLoading ? (
                        <>
                            <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                            Analyzing...
                        </>
                    ) : (
                        <>
                            <Sparkles className="w-5 h-5" />
                            Get Clips
                        </>
                    )}
                </button>

            </div>
        </div>
      )}
    </div>
  );
}
