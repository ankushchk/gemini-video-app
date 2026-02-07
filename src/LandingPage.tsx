
import { ArrowRight, Sparkles, Zap, Type, Layers } from 'lucide-react';

interface LandingPageProps {
  onStart: () => void;
}

export default function LandingPage({ onStart }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-neutral-800 selection:text-white font-sans">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 border-b border-neutral-900 bg-black/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-neutral-200" />
            <span className="font-medium tracking-tight">Gemini Video</span>
          </div>
          <button 
            onClick={onStart}
            className="text-sm text-neutral-400 hover:text-white transition-colors"
          >
            Launch App
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="pt-32 pb-20 px-6 max-w-7xl mx-auto flex flex-col items-center text-center">
        
        {/* Badge */}
        <div className="mb-8 inline-flex items-center gap-2 px-3 py-1 rounded-full border border-neutral-800 bg-neutral-900/50 text-xs text-neutral-400">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
          </span>
          Powered by Gemini 2.0 Flash
        </div>

        {/* Main Headline with Highlight Animation */}
        <h1 className="text-5xl md:text-7xl font-light tracking-tight text-neutral-200 mb-8 max-w-4xl mx-auto leading-[1.1]">
          Turn long videos into
          <br />
          <span className="relative inline-block mt-2">
             <span className="relative z-10 text-transparent bg-clip-text bg-gradient-to-r from-white via-neutral-200 to-neutral-400 animate-text-shimmer bg-[length:200%_auto]">
               Viral Content
             </span>
             {/* Graphical Underline/Highlight */}
             <span className="absolute -bottom-2 left-0 w-full h-3 bg-neutral-800/80 -z-10 -rotate-1 rounded-sm"></span>
          </span>
          <span className="text-neutral-500">.</span>
        </h1>

        <p className="text-lg text-neutral-500 max-w-2xl mx-auto mb-12 font-light">
          Automatically extract, caption, and viral-score the best moments from your podcasts and videos. No more manual searching.
        </p>

        {/* Primary CTA */}
        <button 
          onClick={onStart}
          className="group relative inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-black rounded-full font-medium text-lg hover:bg-neutral-200 transition-all active:scale-95"
        >
          Start Creating
          <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-32 w-full text-left">
          <FeatureCard 
            icon={<Zap className="w-6 h-6" />}
            title="Viral Scoring"
            description="AI analyzes hook potential, retention, and shareability for every clip."
          />
          <FeatureCard 
            icon={<Type className="w-6 h-6" />}
            title="Auto-Captions"
            description="Burned-in subtitles with perfect timing using advanced transcription."
          />
          <FeatureCard 
            icon={<Layers className="w-6 h-6" />}
            title="Smart Cutting"
            description="Precise start and end times based on sentence boundaries and context."
          />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-neutral-900 py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center text-sm text-neutral-600">
          <div>© 2026 Gemini Video. All rights reserved.</div>
          <div className="flex gap-6 mt-4 md:mt-0">
            <a href="#" className="hover:text-white transition-colors">Privacy</a>
            <a href="#" className="hover:text-white transition-colors">Terms</a>
            <a href="https://github.com/ankushchk/gemini-video-app" className="hover:text-white transition-colors">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  );
}


function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="p-6 rounded-2xl border border-neutral-900 bg-neutral-900/20 hover:border-neutral-800 transition-colors group">
      <div className="mb-4 text-neutral-400 group-hover:text-white transition-colors bg-neutral-900 w-12 h-12 flex items-center justify-center rounded-lg border border-neutral-800">
        {icon}
      </div>
      <h3 className="text-lg font-medium text-neutral-200 mb-2">{title}</h3>
      <p className="text-sm text-neutral-500 leading-relaxed">
        {description}
      </p>
    </div>
  );
}

