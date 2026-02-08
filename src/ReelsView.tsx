import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Play, Volume2, VolumeX, Share2, Heart, TrendingUp } from 'lucide-react';
import type { PodcastClip } from './types';

interface ReelsViewProps {
  clip: PodcastClip;
  onClose: () => void;
}

export default function ReelsView({ clip, onClose }: ReelsViewProps) {
  const [isPlaying, setIsPlaying] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Fetch/Render Vertical Video
  useEffect(() => {
    const fetchVerticalVideo = async () => {
      setLoading(true);
      try {
        const formData = new FormData();
        formData.append('source_file', clip.source_file || '');
        formData.append('clip_data', JSON.stringify(clip));

        const response = await fetch('http://localhost:8000/render-vertical', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) throw new Error('Failed to render vertical video');

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setVideoUrl(url);
      } catch (err) {
        console.error("Error rendering vertical video:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchVerticalVideo();
    return () => {
      if (videoUrl) URL.revokeObjectURL(videoUrl);
    };
  }, [clip]);

  // Handle Video Time Update
  const handleTimeUpdate = () => {
    if (videoRef.current) {
      // Relative time in the clip
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) videoRef.current.pause();
      else videoRef.current.play();
      setIsPlaying(!isPlaying);
    }
  };

  const getActiveCaption = (time: number) => {
    // time is relative to clip start (0s)
    // captions in clip.captions have start_offset relative to clip start
    return clip.captions.find(c => time >= c.start_offset && time <= c.end_offset);
  };

  const activeCaption = getActiveCaption(currentTime);

  return (
    <div className="fixed inset-0 z-50 bg-black flex items-center justify-center backdrop-blur-3xl">
      {/* Close Button */}
      <button 
        onClick={onClose}
        className="absolute top-4 right-4 z-50 p-2 bg-black/40 rounded-full hover:bg-black/60 transition-colors"
      >
        <X className="w-6 h-6 text-white" />
      </button>

      {/* Main Reel Container */}
      <div className="relative w-full h-full max-w-[450px] max-h-[90vh] bg-neutral-900 rounded-xl overflow-hidden shadow-2xl border border-neutral-800">
        
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center z-20 bg-neutral-900">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-2 border-red-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-neutral-400">Rendering Vertical Studio...</p>
            </div>
          </div>
        )}

        {videoUrl && (
          <>
            <video
              ref={videoRef}
              src={videoUrl}
              className="w-full h-full object-cover"
              loop
              autoPlay
              muted={isMuted}
              playsInline
              onTimeUpdate={handleTimeUpdate}
              onClick={togglePlay}
            />

            {/* Controls Overlay */}
            <div className="absolute inset-0 pointer-events-none flex flex-col justify-between p-6">
              
              {/* Top Gradient */}
              <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-black/60 to-transparent pointer-events-none" />

              {/* Viral Score Badge */}
              <div className="relative z-10 flex justify-between items-start">
                 <div className="bg-black/30 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/10 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-green-400" />
                    <span className="text-xs font-bold text-white">{(clip.viral_score * 100).toFixed(0)}% Viral Score</span>
                 </div>
                 
                 <button 
                   onClick={() => setIsMuted(!isMuted)} 
                   className="pointer-events-auto p-2 bg-black/20 rounded-full backdrop-blur-sm"
                  >
                   {isMuted ? <VolumeX className="w-5 h-5 text-white" /> : <Volume2 className="w-5 h-5 text-white" />}
                 </button>
              </div>

              {/* Center Play/Pause Indicator (only when paused) */}
              {!isPlaying && (
                <div className="absolute inset-0 flex items-center justify-center z-10">
                  <div className="bg-black/40 p-4 rounded-full backdrop-blur-sm">
                    <Play className="w-10 h-10 text-white fill-white" />
                  </div>
                </div>
              )}

              {/* Bottom Info & Captions */}
              <div className="relative z-10 space-y-4">
                 
                 {/* Karaoke Captions Area */}
                 <div className="min-h-[100px] flex items-center justify-center text-center px-4 mb-12">
                   <AnimatePresence mode="wait">
                     {activeCaption ? (
                       <motion.div
                         key={activeCaption.start_offset}
                         initial={{ opacity: 0, y: 10, scale: 0.95 }}
                         animate={{ opacity: 1, y: 0, scale: 1 }}
                         exit={{ opacity: 0, y: -10, scale: 1.05 }}
                         transition={{ duration: 0.15 }}
                         className="relative flex flex-col items-center gap-2"
                       >
                         {/* Animated Emoji */}
                         {activeCaption.emoji && (
                           <motion.div
                             initial={{ scale: 0, rotate: -20 }}
                             animate={{ scale: 1.5, rotate: 0 }}
                             transition={{ type: "spring", bounce: 0.5 }}
                             className="text-6xl filter drop-shadow-lg mb-2"
                           >
                             {activeCaption.emoji}
                           </motion.div>
                         )}

                         <p 
                           className="text-2xl font-black text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)] leading-tight stroke-black"
                           style={{ textShadow: '0 0 10px rgba(0,0,0,0.5)' }}
                         >
                           {/* Highlight emphasis words */}
                           {activeCaption.text.split(' ').map((word, idx) => {
                             const isEmphatic = activeCaption.emphasis?.some(e => word.toLowerCase().includes(e.toLowerCase()));
                             return (
                               <span 
                                 key={idx} 
                                 className={`${isEmphatic ? 'text-yellow-400 scale-110 inline-block mx-1' : 'mx-1'}`}
                               >
                                 {word}
                               </span>
                             );
                           })}
                         </p>
                       </motion.div>
                     ) : (
                        <div className="h-8" /> // Spacer to prevent jump
                     )}
                   </AnimatePresence>
                 </div>

                 {/* Clip Metadata */}
                 <div className="space-y-2">
                    <h3 className="text-white font-bold text-lg drop-shadow-md pr-12 leading-snug">
                      {clip.hook}
                    </h3>
                    <div className="flex items-center gap-3">
                       <div className="flex items-center gap-1 text-white/90 bg-white/10 px-2 py-1 rounded backdrop-blur-sm">
                          <span className="text-xs font-medium">#{clip.hashtags[0] || 'viral'}</span>
                       </div>
                    </div>
                 </div>

              </div>

              {/* Side Actions (TikTok Style) */}
              <div className="absolute right-4 bottom-28 flex flex-col gap-6 items-center pointer-events-auto">
                 <button className="flex flex-col items-center gap-1 group">
                    <div className="p-3 bg-zinc-800/80 rounded-full hover:bg-zinc-700 transition-colors">
                        <Heart className="w-6 h-6 text-white group-hover:text-red-500 transition-colors" />
                    </div>
                    <span className="text-xs font-medium text-white shadow-black drop-shadow-md">Like</span>
                 </button>
                 <button className="flex flex-col items-center gap-1 group">
                    <div className="p-3 bg-zinc-800/80 rounded-full hover:bg-zinc-700 transition-colors">
                        <Share2 className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-xs font-medium text-white shadow-black drop-shadow-md">Share</span>
                 </button>
              </div>

            </div>
          </>
        )}
      </div>
    </div>
  );
}
