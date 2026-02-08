
import { useState } from 'react';
import { X, Type, Clock } from 'lucide-react';
import type { PodcastClip, Caption } from './types';

interface SubtitleEditorProps {
  clip: PodcastClip;
  onClose: () => void;
  onSave: (updatedClip: PodcastClip) => void;
}

export function SubtitleEditor({ clip, onClose, onSave }: SubtitleEditorProps) {
  const [captions, setCaptions] = useState<Caption[]>(clip.captions || []);
  const [activeCaptionIndex, setActiveCaptionIndex] = useState<number | null>(null);
  
  // Style settings (future expansion)
  const [fontSize] = useState(24);
  
  const handleTextChange = (index: number, newText: string) => {
    const newCaptions = [...captions];
    newCaptions[index] = { ...newCaptions[index], text: newText };
    setCaptions(newCaptions);
  };

  const handleTimeChange = (index: number, field: 'start_offset' | 'end_offset', value: string) => {
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return;
    
    const newCaptions = [...captions];
    newCaptions[index] = { ...newCaptions[index], [field]: numValue };
    setCaptions(newCaptions);
  };

  const handleSave = () => {
    onSave({
      ...clip,
      captions: captions
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-neutral-900 w-full max-w-4xl h-[80vh] rounded-xl border border-neutral-800 flex flex-col shadow-2xl">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-neutral-800">
          <div className="flex items-center gap-2">
            <Type className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-semibold text-white">Subtitle Editor</h2>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-neutral-800 rounded-full transition-colors">
            <X className="w-5 h-5 text-neutral-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 flex overflow-hidden">
          
          {/* Left: Preview (Placeholder for now, simplified) */}
          <div className="w-1/3 bg-black p-4 flex items-center justify-center border-r border-neutral-800 relative">
             <div className="aspect-[9/16] h-full bg-neutral-800 rounded-lg flex items-center justify-center relative overflow-hidden">
                <p className="text-neutral-500 text-sm">Video Preview</p>
                {/* Simulated Caption Overlay */}
                <div className="absolute bottom-20 w-full text-center px-4">
                     <p 
                       style={{ fontSize: `${fontSize}px` }}
                       className="text-white font-bold drop-shadow-md bg-black/50 p-2 rounded inline-block"
                     >
                       {activeCaptionIndex !== null ? captions[activeCaptionIndex].text : "Select a caption"}
                     </p>
                </div>
             </div>
          </div>

          {/* Right: Caption List */}
          <div className="w-2/3 overflow-y-auto p-4 space-y-2">
            {captions.map((cap, idx) => (
              <div 
                key={idx}
                className={`group flex items-start gap-3 p-3 rounded-lg border transition-all ${
                  activeCaptionIndex === idx 
                    ? 'bg-neutral-800 border-purple-500/50' 
                    : 'bg-neutral-950/50 border-neutral-800 hover:border-neutral-700'
                }`}
                onClick={() => setActiveCaptionIndex(idx)}
              >
                <div className="flex flex-col gap-1 min-w-[32px] pt-1">
                   <span className="text-xs text-neutral-500 font-mono">#{idx+1}</span>
                </div>
                
                <div className="flex-1 space-y-2">
                   {/* Text Input */}
                   <textarea 
                     value={cap.text}
                     onChange={(e) => handleTextChange(idx, e.target.value)}
                     className="w-full bg-transparent text-white text-sm focus:outline-none resize-none"
                     rows={2}
                   />
                   
                   {/* Timing & Metadata */}
                   <div className="flex items-center gap-4 text-xs text-neutral-500">
                      <div className="flex items-center gap-1 bg-neutral-900 px-2 py-1 rounded">
                        <Clock className="w-3 h-3" />
                        <input 
                          type="number" 
                          step="0.1"
                          value={cap.start_offset}
                          onChange={(e) => handleTimeChange(idx, 'start_offset', e.target.value)}
                          className="w-12 bg-transparent focus:outline-none text-neutral-300"
                        />
                        <span>→</span>
                        <input 
                           type="number" 
                           step="0.1"
                           value={cap.end_offset}
                           onChange={(e) => handleTimeChange(idx, 'end_offset', e.target.value)}
                           className="w-12 bg-transparent focus:outline-none text-neutral-300"
                        />
                      </div>
                      
                      {cap.emphasis && cap.emphasis.length > 0 && (
                        <span className="text-yellow-500/80">
                          Emphasis: {cap.emphasis.join(", ")}
                        </span>
                      )}
                   </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-neutral-800 flex justify-end gap-3">
          <button 
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-neutral-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button 
            onClick={handleSave}
            className="px-4 py-2 text-sm font-medium bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors shadow-lg shadow-purple-900/20"
          >
            Save & Burn Captions
          </button>
        </div>

      </div>
    </div>
  );
}
