import React, { useState } from 'react';
import { Character } from '../types';
import { User, Volume2, Palette, Sparkles, Smile, Frown, Zap } from 'lucide-react';

interface CharacterBibleViewerProps {
  characters: Character[];
}

export const CharacterBibleViewer: React.FC<CharacterBibleViewerProps> = ({ characters }) => {
  const [selectedChar, setSelectedChar] = useState<Character | null>(characters[0] || null);

  if (!characters || characters.length === 0) {
    return (
      <div className="p-8 text-center glass-panel rounded-2xl">
        <p className="text-slate-400">No characters generated yet.</p>
      </div>
    );
  }

  const activeChar = selectedChar || characters[0];

  return (
    <div className="space-y-6">
      {/* Character Selector Tabs */}
      <div className="flex flex-wrap gap-3">
        {characters.map((char) => (
          <button
            key={char.id}
            onClick={() => setSelectedChar(char)}
            className={`flex items-center gap-3 px-4 py-2.5 rounded-xl border transition-all ${
              activeChar.id === char.id
                ? 'bg-purple-600/20 border-purple-500/50 shadow-lg shadow-purple-500/20 text-white'
                : 'bg-dark-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
            }`}
          >
            {char.avatar_url ? (
              <img src={char.avatar_url} alt={char.name} className="w-7 h-7 rounded-full object-cover border border-purple-400/40" />
            ) : (
              <User className="w-5 h-5 text-purple-400" />
            )}
            <div className="text-left">
              <div className="text-sm font-bold leading-tight">{char.name}</div>
              <div className="text-[11px] text-slate-500 font-medium">{char.role}</div>
            </div>
          </button>
        ))}
      </div>

      {/* Selected Character Deep Profile Card */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left: Avatar & Multi-Expression Sprites */}
        <div className="lg:col-span-5 space-y-4">
          <div className="relative aspect-[4/5] rounded-2xl overflow-hidden bg-gradient-to-b from-dark-850 to-dark-950 border border-slate-700/60 flex items-center justify-center p-4">
            {activeChar.avatar_url ? (
              <img
                src={activeChar.avatar_url}
                alt={activeChar.name}
                className="w-full h-full object-contain filter drop-shadow-[0_10px_20px_rgba(0,0,0,0.8)] hover:scale-105 transition-transform duration-300"
              />
            ) : (
              <User className="w-24 h-24 text-slate-600" />
            )}
            <div className="absolute top-3 left-3 px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-xs font-semibold text-purple-300 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-pink-400" />
              <span>{activeChar.role}</span>
            </div>
          </div>

          {/* Expression Sprite Previews */}
          <div className="space-y-1.5">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Expression Rigs</span>
            <div className="grid grid-cols-4 gap-2">
              {[
                { label: 'Talking', url: activeChar.mouth_open_url },
                { label: 'Closed', url: activeChar.mouth_closed_url },
                { label: 'Shock', url: activeChar.expression_shock_url },
                { label: 'Happy', url: activeChar.expression_happy_url },
              ].map((exp, idx) => (
                <div key={idx} className="p-1 rounded-xl bg-dark-900 border border-slate-800 text-center">
                  {exp.url ? (
                    <img src={exp.url} alt={exp.label} className="w-full h-12 object-contain rounded-lg mb-1" />
                  ) : (
                    <div className="w-full h-12 flex items-center justify-center bg-slate-800/40 rounded-lg mb-1 text-slate-600 text-xs">N/A</div>
                  )}
                  <span className="text-[10px] text-slate-400 font-medium block">{exp.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Character Bible Metadata */}
        <div className="lg:col-span-7 space-y-6">
          <div>
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-bold font-display text-white">{activeChar.name}</h3>
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-pink-500/15 text-pink-400 border border-pink-500/30">
                Age: {activeChar.age}
              </span>
            </div>
            <p className="text-sm text-slate-300 mt-2 italic">"{activeChar.personality}"</p>
          </div>

          {/* Consistency Attributes Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3.5 rounded-xl bg-dark-900/60 border border-slate-800/80">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Outfit</span>
              <p className="text-sm text-slate-200 mt-1">{activeChar.outfit_desc}</p>
            </div>

            <div className="p-3.5 rounded-xl bg-dark-900/60 border border-slate-800/80">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Hair Style</span>
              <p className="text-sm text-slate-200 mt-1">{activeChar.hair_style}</p>
            </div>

            <div className="p-3.5 rounded-xl bg-dark-900/60 border border-slate-800/80">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Assigned Voice</span>
              <div className="flex items-center gap-2 mt-1">
                <Volume2 className="w-4 h-4 text-purple-400" />
                <span className="text-sm font-medium text-slate-200">{activeChar.voice_name || 'Guy (Energetic)'}</span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-dark-900/60 border border-slate-800/80">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Color Palette</span>
              <div className="flex items-center gap-2 mt-2">
                <div
                  className="w-5 h-5 rounded-full border border-white/20 shadow-sm"
                  style={{ backgroundColor: activeChar.hair_color || '#2d3748' }}
                  title={`Hair: ${activeChar.hair_color}`}
                />
                <div
                  className="w-5 h-5 rounded-full border border-white/20 shadow-sm"
                  style={{ backgroundColor: activeChar.skin_tone || '#f6d5b8' }}
                  title={`Skin: ${activeChar.skin_tone}`}
                />
                <div
                  className="w-5 h-5 rounded-full border border-white/20 shadow-sm"
                  style={{ backgroundColor: activeChar.outfit_color || '#3b82f6' }}
                  title={`Outfit: ${activeChar.outfit_color}`}
                />
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-800/30 text-xs text-purple-300">
            <span className="font-bold block mb-1">🔒 Consistency Lock Active</span>
            ToonForge re-uses this character specification across all {activeChar.name} scenes to guarantee uniform appearance throughout the short.
          </div>
        </div>
      </div>
    </div>
  );
};
