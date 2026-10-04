import React from 'react';
import { CheckCircle2, Circle, Loader2, Sparkles, Terminal, Cpu, Image, Mic, Film, Volume2, Music, Video } from 'lucide-react';

interface ProgressTimelineProps {
  progress: number;
  currentStage: string;
  stageMessage: string;
  logs?: string[];
  providers?: Record<string, string>;
}

const STAGES = [
  { id: 'story', name: 'Story & Hook Planning', threshold: 10 },
  { id: 'characters', name: 'Character Bible & Rigging', threshold: 25 },
  { id: 'scenes', name: 'Scene & Background Composition', threshold: 45 },
  { id: 'voice', name: 'Speech Synthesis & Word Timing', threshold: 60 },
  { id: 'subtitles', name: 'Subtitles & Dynamic Sound FX', threshold: 72 },
  { id: 'motion', name: 'Scene Animation & Camera Moves', threshold: 85 },
  { id: 'assembly', name: 'FFmpeg 1080x1920 Concat & Burn', threshold: 95 },
  { id: 'thumbnail', name: 'YouTube Thumbnail & Metadata', threshold: 100 },
];

export const ProgressTimeline: React.FC<ProgressTimelineProps> = ({
  progress,
  currentStage,
  stageMessage,
  logs = [],
  providers,
}) => {
  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Percentage Gauge & Pulse Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold uppercase tracking-wider animate-pulse">
          <Sparkles className="w-3.5 h-3.5 text-pink-400" />
          <span>Generating Your YouTube Short</span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold font-display text-white">
          {progress >= 100 ? 'Finishing Up...' : currentStage || 'Creating Magic...'}
        </h2>
        <p className="text-sm text-slate-400 font-medium max-w-md mx-auto">
          {stageMessage || 'Please wait while ToonForge constructs your cartoon video.'}
        </p>

        {/* Big Progress Bar */}
        <div className="w-full max-w-lg mx-auto mt-4 space-y-2">
          <div className="h-3 w-full bg-dark-900 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-purple-600 via-pink-500 to-amber-400 rounded-full transition-all duration-500 shadow-lg shadow-pink-500/30"
              style={{ width: `${Math.max(5, progress)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs font-mono font-semibold text-slate-400">
            <span>START</span>
            <span className="text-pink-400 font-bold">{progress}%</span>
            <span>1080x1920 MP4</span>
          </div>
        </div>
      </div>

      {/* AI Provider Breakdown Panel */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-purple-400" />
            <span>Active Pipeline Engines</span>
          </span>
          <span className="text-[10px] font-mono text-slate-500">Autonomous Orchestration</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
          <div className="p-2.5 rounded-xl bg-dark-900/70 border border-slate-800 flex flex-col justify-between">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Story / Script</span>
            <span className="font-bold text-slate-200 mt-1 truncate">
              {providers?.story?.includes('Ollama') ? 'Ollama' : 'Smart Cartoon'}
            </span>
            <span className={`text-[10px] font-mono font-semibold mt-0.5 ${providers?.story?.includes('REAL AI') ? 'text-emerald-400' : 'text-amber-400'}`}>
              {providers?.story?.includes('REAL AI') ? 'REAL AI' : 'FALLBACK'}
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-dark-900/70 border border-slate-800 flex flex-col justify-between">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Visuals & Rigs</span>
            <span className="font-bold text-slate-200 mt-1 truncate">
              {providers?.visuals?.includes('ComfyUI') ? 'ComfyUI' : 'ToonVector'}
            </span>
            <span className={`text-[10px] font-mono font-semibold mt-0.5 ${providers?.visuals?.includes('REAL AI') ? 'text-emerald-400' : 'text-amber-400'}`}>
              {providers?.visuals?.includes('REAL AI') ? 'REAL AI' : 'FALLBACK'}
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-dark-900/70 border border-slate-800 flex flex-col justify-between">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Voice Synthesis</span>
            <span className="font-bold text-slate-200 mt-1 truncate">
              {providers?.voice?.includes('Kokoro') ? 'Kokoro' : (providers?.voice?.includes('Piper') ? 'Piper' : 'EdgeTTS')}
            </span>
            <span className={`text-[10px] font-mono font-semibold mt-0.5 ${providers?.voice?.includes('REAL') ? 'text-emerald-400' : 'text-blue-400'}`}>
              {providers?.voice?.includes('REAL AI') ? 'REAL AI' : (providers?.voice?.includes('REAL TTS') ? 'REAL TTS' : 'FALLBACK')}
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-dark-900/70 border border-slate-800 flex flex-col justify-between">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Animation</span>
            <span className="font-bold text-slate-200 mt-1 truncate">
              {providers?.animation?.includes('Local AI') ? 'AI Diffusion' : 'Motion Comic'}
            </span>
            <span className={`text-[10px] font-mono font-semibold mt-0.5 ${providers?.animation?.includes('REAL AI') ? 'text-emerald-400' : 'text-amber-400'}`}>
              {providers?.animation?.includes('REAL AI') ? 'REAL AI' : 'FALLBACK'}
            </span>
          </div>
        </div>
      </div>

      {/* Stage Checklist */}
      <div className="glass-panel rounded-3xl p-6 sm:p-7 border border-slate-800 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Production Stages</h3>
        <div className="space-y-2.5">
          {STAGES.map((stage) => {
            const isCompleted = progress >= stage.threshold;
            const isCurrent = progress < stage.threshold && progress >= stage.threshold - 15;

            return (
              <div
                key={stage.id}
                className={`flex items-center justify-between p-3 rounded-xl transition-all ${
                  isCurrent
                    ? 'bg-purple-950/40 border border-purple-500/40 shadow-md shadow-purple-500/10'
                    : isCompleted
                    ? 'bg-dark-900/40 border border-slate-800/60 text-slate-300'
                    : 'bg-dark-950/20 text-slate-600 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  {isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-pink-400 animate-spin shrink-0" />
                  ) : (
                    <Circle className="w-4 h-4 text-slate-700 shrink-0" />
                  )}
                  <span className={`text-xs font-semibold ${isCurrent ? 'text-white' : ''}`}>
                    {stage.name}
                  </span>
                </div>

                <span className="text-[11px] font-mono">
                  {isCompleted ? (
                    <span className="text-emerald-400 font-bold">READY</span>
                  ) : isCurrent ? (
                    <span className="text-pink-400 animate-pulse font-bold">IN PROGRESS</span>
                  ) : (
                    <span className="text-slate-600">QUEUED</span>
                  )}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Live Pipeline Logs Terminal */}
      {logs.length > 0 && (
        <div className="rounded-2xl bg-black/90 border border-slate-800 overflow-hidden font-mono text-xs">
          <div className="px-4 py-2 bg-dark-900/90 border-b border-slate-800 flex items-center gap-2 text-slate-400">
            <Terminal className="w-3.5 h-3.5 text-purple-400" />
            <span className="font-semibold text-[11px] tracking-wider uppercase">Live Pipeline Output</span>
          </div>
          <div className="p-4 max-h-40 overflow-y-auto space-y-1.5 text-slate-300">
            {logs.slice(-6).map((log, idx) => (
              <div key={idx} className="leading-relaxed flex items-start gap-2">
                <span className="text-purple-400 font-bold">❯</span>
                <span>{log}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
