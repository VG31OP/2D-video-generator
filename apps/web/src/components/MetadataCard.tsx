import React, { useState } from 'react';
import { ProjectMetadata } from '../types';
import { Copy, Check, Hash, Video, Sparkles, Cpu, Layers } from 'lucide-react';

interface MetadataCardProps {
  metadata?: ProjectMetadata;
  title: string;
}

export const MetadataCard: React.FC<MetadataCardProps> = ({ metadata, title }) => {
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const handleCopy = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const ytTitle = metadata?.youtube_title || `${title} #shorts`;
  const desc = metadata?.description || `Watch what happens next! Subscribe for daily funny cartoon shorts.`;
  const hashtags = metadata?.hashtags || ['#shorts', '#cartoon', '#animation', '#funny', '#ai'];
  const providers = (metadata as any)?.providers;

  return (
    <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400">
            <Video className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold font-display text-white">YouTube Shorts Package</h3>
            <p className="text-xs text-slate-400">Optimized for high algorithm click-through rate</p>
          </div>
        </div>
      </div>

      {/* Generation Provider Report Badge */}
      {providers && (
        <div className="p-4 rounded-2xl bg-dark-900/90 border border-slate-800 space-y-2.5">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-purple-400" />
            <span>Generation Attribution Report</span>
          </span>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            <div className="p-2 rounded-lg bg-dark-950/70 border border-slate-800/80">
              <span className="text-[10px] text-slate-500 block">Story Engine</span>
              <span className="font-semibold text-slate-300 truncate block text-[11px]">{providers.story}</span>
            </div>
            <div className="p-2 rounded-lg bg-dark-950/70 border border-slate-800/80">
              <span className="text-[10px] text-slate-500 block">Visual Artwork</span>
              <span className="font-semibold text-slate-300 truncate block text-[11px]">{providers.visuals}</span>
            </div>
            <div className="p-2 rounded-lg bg-dark-950/70 border border-slate-800/80">
              <span className="text-[10px] text-slate-500 block">Voice Speech</span>
              <span className="font-semibold text-slate-300 truncate block text-[11px]">{providers.voice}</span>
            </div>
            <div className="p-2 rounded-lg bg-dark-950/70 border border-slate-800/80">
              <span className="text-[10px] text-slate-500 block">Animation / LipSync</span>
              <span className="font-semibold text-slate-300 truncate block text-[11px]">{providers.animation}</span>
            </div>
          </div>
        </div>
      )}

      {/* Title */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Video Title</label>
          <button
            onClick={() => handleCopy(ytTitle, 'title')}
            className="flex items-center gap-1.5 text-xs font-semibold text-purple-400 hover:text-purple-300 transition"
          >
            {copiedField === 'title' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedField === 'title' ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
        <div className="p-3.5 rounded-xl bg-dark-900 border border-slate-800 text-sm font-semibold text-white">
          {ytTitle}
        </div>
      </div>

      {/* Description */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Description</label>
          <button
            onClick={() => handleCopy(desc, 'desc')}
            className="flex items-center gap-1.5 text-xs font-semibold text-purple-400 hover:text-purple-300 transition"
          >
            {copiedField === 'desc' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedField === 'desc' ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
        <div className="p-3.5 rounded-xl bg-dark-900 border border-slate-800 text-xs text-slate-300 leading-relaxed">
          {desc}
        </div>
      </div>

      {/* Hashtags */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Viral Hashtags</label>
          <button
            onClick={() => handleCopy(hashtags.join(' '), 'tags')}
            className="flex items-center gap-1.5 text-xs font-semibold text-purple-400 hover:text-purple-300 transition"
          >
            {copiedField === 'tags' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedField === 'tags' ? 'Copied All' : 'Copy All'}</span>
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {hashtags.map((tag, idx) => (
            <span
              key={idx}
              className="px-3 py-1 rounded-lg bg-pink-500/10 text-pink-400 border border-pink-500/20 text-xs font-semibold flex items-center gap-1 cursor-pointer hover:bg-pink-500/20 transition"
              onClick={() => handleCopy(tag, `tag_${idx}`)}
            >
              <Hash className="w-3 h-3" />
              {tag.replace('#', '')}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
