import type { PodcastClip } from './types';
import { X, Clock, TrendingUp, Hash, Palette, Film } from 'lucide-react';

interface ClipDetailViewProps {
  clip: PodcastClip;
  onClose: () => void;
}

export default function ClipDetailView({ clip, onClose }: ClipDetailViewProps) {
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getScoreColor = (score: number): string => {
    if (score >= 0.9) return 'text-green-500';
    if (score >= 0.75) return 'text-yellow-500';
    return 'text-orange-500';
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6">
      <div className="bg-neutral-900 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-neutral-900 border-b border-neutral-800 p-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-light">{clip?.clip_id || 'Unknown Clip'}</h2>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-neutral-600" />
              <span className={`text-sm font-medium ${getScoreColor(clip?.viral_score || 0)}`}>
                {((clip?.viral_score || 0) * 100).toFixed(0)}%
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-neutral-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Timing */}
          <div className="flex items-center gap-4 text-sm text-neutral-400">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span>{formatTime(clip?.refined_start || 0)} - {formatTime(clip?.refined_end || 0)}</span>
            </div>
            <span>•</span>
            <span>{clip?.refined_duration || 0}s</span>
          </div>

          {/* Hook */}
          <div>
            <h3 className="text-sm text-neutral-500 mb-2">Hook (First 3 seconds)</h3>
            <p className="text-lg font-medium text-white">{clip?.hook || 'No hook detected'}</p>
          </div>

          {/* Reasoning */}
          <div>
            <h3 className="text-sm text-neutral-500 mb-2">Why This Will Go Viral</h3>
            <p className="text-neutral-300">{clip?.reasoning || 'No analysis available'}</p>
          </div>

          {/* Captions */}
          <div>
            <h3 className="text-sm text-neutral-500 mb-3">On-Screen Captions</h3>
            <div className="space-y-2">
              {(clip?.captions || []).map((caption, idx) => (
                <div key={idx} className="bg-neutral-800/50 rounded p-3">
                  <div className="text-sm text-neutral-400 mb-1">
                    {formatTime(caption.start_offset)} - {formatTime(caption.end_offset)}
                  </div>
                  <div className="text-white">
                    {caption.text.split(' ').map((word, wordIdx) => (
                      <span
                        key={wordIdx}
                        className={(caption.emphasis || []).some(e => word.includes(e)) ? 'font-bold text-yellow-400' : ''}
                      >
                        {word}{' '}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
              {(!clip?.captions || clip.captions.length === 0) && (
                <p className="text-sm text-neutral-500 italic">No captions generated.</p>
              )}
            </div>
          </div>

          {/* Reel Caption & Hashtags */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm text-neutral-500 mb-2">Reel Caption</h3>
              <p className="text-neutral-300 text-sm">{clip?.reel_caption || 'No caption generated'}</p>
            </div>
            <div>
              <h3 className="text-sm text-neutral-500 mb-2 flex items-center gap-2">
                <Hash className="w-4 h-4" />
                Hashtags
              </h3>
              <div className="flex flex-wrap gap-2">
                {(clip?.hashtags || []).map((tag, idx) => (
                  <span key={idx} className="text-xs bg-neutral-800 px-2 py-1 rounded text-blue-400">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Tone */}
          <div className="grid grid-cols-2 gap-4 p-4 bg-neutral-800/30 rounded-lg">
            <div>
              <div className="text-xs text-neutral-500 mb-1">Pacing</div>
              <div className="text-sm text-white capitalize">{clip?.tone?.pacing || 'N/A'}</div>
            </div>
            <div>
              <div className="text-xs text-neutral-500 mb-1">Music Vibe</div>
              <div className="text-sm text-white capitalize">{clip?.tone?.music_vibe || 'N/A'}</div>
            </div>
          </div>

          {/* Visual Beats */}
          <div>
            <h3 className="text-sm text-neutral-500 mb-3 flex items-center gap-2">
              <Palette className="w-4 h-4" />
              Visual Treatment Plan
            </h3>
            <div className="space-y-3">
              {(clip?.visual_beats || []).map((beat, idx) => (
                <div key={idx} className="bg-neutral-800/50 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="text-sm font-medium text-white">Beat {idx + 1}</div>
                    <div className="text-xs text-neutral-400">{beat.duration}s</div>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-neutral-500">Image: </span>
                      <span className="text-neutral-300">{beat.image_concept}</span>
                    </div>
                    <div>
                      <span className="text-neutral-500">Text: </span>
                      <span className="text-neutral-300 italic">"{beat.text_overlay}"</span>
                    </div>
                    <div className="flex gap-4">
                      <div>
                        <span className="text-neutral-500">Motion: </span>
                        <span className="text-neutral-300 capitalize">{beat.motion}</span>
                      </div>
                      <div>
                        <span className="text-neutral-500">Intensity: </span>
                        <span className="text-neutral-300">{beat.motion_intensity}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
               {(!clip?.visual_beats || clip.visual_beats.length === 0) && (
                <p className="text-sm text-neutral-500 italic">No visual beats planned.</p>
              )}
            </div>
          </div>

          {/* Style Specs */}
          <div>
            <h3 className="text-sm text-neutral-500 mb-3">Style Specifications</h3>
            <div className="bg-neutral-800/30 rounded-lg p-4 space-y-3">
              <div>
                <div className="text-xs text-neutral-500 mb-2">Color Palette</div>
                <div className="flex gap-2">
                  {(clip?.style?.color_palette || []).map((color, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <div
                        className="w-8 h-8 rounded border border-neutral-700"
                        style={{ backgroundColor: color }}
                      />
                      <span className="text-xs text-neutral-400">{color}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-xs text-neutral-500 mb-1">Typography</div>
                <div className="text-sm text-neutral-300">{clip?.style?.typography || 'N/A'}</div>
              </div>
              <div>
                <div className="text-xs text-neutral-500 mb-1">Composition</div>
                <div className="text-sm text-neutral-300 capitalize">{clip?.style?.composition || 'N/A'}</div>
              </div>
            </div>
          </div>

          {/* Assembly Specs */}
          <div>
            <h3 className="text-sm text-neutral-500 mb-3 flex items-center gap-2">
              <Film className="w-4 h-4" />
              Assembly Specifications
            </h3>
            <div className="bg-neutral-800/30 rounded-lg p-4">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <div className="text-xs text-neutral-500 mb-1">Resolution</div>
                  <div className="text-neutral-300">{clip?.assembly_spec?.resolution || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-xs text-neutral-500 mb-1">Aspect Ratio</div>
                  <div className="text-neutral-300">{clip?.assembly_spec?.aspect_ratio || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-xs text-neutral-500 mb-1">FPS</div>
                  <div className="text-neutral-300">{clip?.assembly_spec?.fps || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-xs text-neutral-500 mb-1">Video Codec</div>
                  <div className="text-neutral-300">{clip?.assembly_spec?.video_codec || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-xs text-neutral-500 mb-1">Audio Format</div>
                  <div className="text-neutral-300">{clip?.assembly_spec?.audio_format || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-xs text-neutral-500 mb-1">Transition</div>
                  <div className="text-neutral-300 capitalize">{clip?.assembly_spec?.image_transition || 'N/A'}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Export Button */}
          <button
            onClick={() => {
              const dataStr = JSON.stringify(clip, null, 2);
              const dataBlob = new Blob([dataStr], { type: 'application/json' });
              const url = URL.createObjectURL(dataBlob);
              const link = document.createElement('a');
              link.href = url;
              link.download = `${clip?.clip_id || 'clip'}_spec.json`;
              link.click();
              URL.revokeObjectURL(url);
            }}
            className="w-full bg-white text-black py-3 rounded-lg font-medium hover:bg-neutral-200 transition-colors"
          >
            Export JSON Specification
          </button>
        </div>
      </div>
    </div>
  );
}
