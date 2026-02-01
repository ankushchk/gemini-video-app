/**
 * TypeScript interfaces for Podcast Content Analyzer
 */

export interface TranscriptChunk {
  chunk_id: string;
  start_time: number;
  end_time: number;
  duration: number;
  speakers: string[];
  summary: string;
}

export interface ViralAnalysis {
  chunk_id: string;
  viral_score: number;
  editorial_reasoning: string;
  context_dependency: boolean;
  emotional_peak?: string;
  quotability?: string;
  platform_fit?: string;
}

export interface Caption {
  text: string;
  start_offset: number;
  end_offset: number;
  emphasis: string[];
}

export interface ToneAdaptation {
  pacing: 'slow-burn' | 'rapid-fire' | 'conversational';
  music_vibe: 'energetic' | 'reflective' | 'tense' | 'inspiring';
}

export interface VisualBeat {
  image_concept: string;
  text_overlay: string;
  motion: 'zoom-in' | 'zoom-out' | 'pan-left' | 'pan-right' | 'fade' | 'static';
  motion_intensity: number;
  duration: number;
}

export interface StyleSpec {
  color_palette: string[];
  typography: string;
  composition: 'rule-of-thirds' | 'centered' | 'lower-third';
}

export interface AssemblySpec {
  aspect_ratio: string;
  resolution: string;
  fps: number;
  audio_format: string;
  video_codec: string;
  background_layer: 'image' | 'gradient' | 'solid-color';
  audio_waveform: boolean;
  captions_layer: boolean;
  hook_overlay: boolean;
  image_transition: 'cross-dissolve' | 'cut';
  transition_duration: number;
  text_animation: 'fade-in' | 'slide-up' | 'typewriter';
}

export interface PodcastClip {
  clip_id: string;
  chunk_id: string;
  start: number;
  end: number;
  refined_start: number;
  refined_end: number;
  refined_duration: number;
  viral_score: number;
  reasoning: string;
  hook: string;
  captions: Caption[];
  reel_caption: string;
  hashtags: string[];
  tone: ToneAdaptation;
  visual_beats: VisualBeat[];
  style: StyleSpec;
  assembly_spec: AssemblySpec;
}

export interface PodcastAnalysisResult {
  chunks: TranscriptChunk[];
  analysis: ViralAnalysis[];
  selected_clips: PodcastClip[];
  error?: string;
}

export interface PodcastMetadata {
  guest?: string;
  topic?: string;
  tone?: string;
}
