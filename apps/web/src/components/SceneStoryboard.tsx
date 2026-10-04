import React from 'react';
import { Scene } from '../types';
import { Camera, Volume2, Sparkles, Film, Clock } from 'lucide-react';

interface SceneStoryboardProps {
  scenes: Scene[];
}

export const SceneStoryboard: React.FC<SceneStoryboardProps> = ({ scenes }) => {
  if (!scenes || scenes.length === 0) {
    return (
      <div className="p-8 text-center glass-panel rounded-2xl">
        <p className="text-slate-400">No scenes generated yet.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {scenes.map((scene) => (
        <div
          key={scene.id || scene.scene_number}
          className="glass-panel rounded-2xl overflow-hidden border border-slate-800 hover:border-purple-500/40 transition-all duration-300 group flex flex-col justify-between"
        >
          {/* Scene Thumbnail / Visual Layer */}
          <div className="relative aspect-[9/16] max-h-[280px] bg-dark-950 overflow-hidden flex items-center justify-center">
            {scene.scene_image_url ? (
              <img
                src={scene.scene_image_url}
                alt={`Scene ${scene.scene_number}`}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
            ) : (
              <Film className="w-12 h-12 text-slate-700" />
            )}

            {/* Top Badges */}
            <div className="absolute top-3 left-3 flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-full bg-black/70 backdrop-blur-md text-xs font-bold text-white border border-white/10">
                Scene {scene.scene_number}
              </span>
              <span className="px-2 py-1 rounded-full bg-purple-900/80 backdrop-blur-md text-[11px] font-medium text-purple-300 border border-purple-500/30 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {scene.duration.toFixed(1)}s
              </span>
            </div>

            {/* Camera Movement Tag */}
            <div className="absolute bottom-3 right-3 px-2.5 py-1 rounded-full bg-black/80 backdrop-blur-md text-[11px] font-medium text-amber-300 border border-amber-500/30 flex items-center gap-1.5">
              <Camera className="w-3 h-3 text-amber-400" />
              <span>{scene.camera_motion}</span>
            </div>
          </div>

          {/* Scene Info */}
          <div className="p-4 space-y-3 flex-1 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold text-pink-400 uppercase tracking-wide">
                  {scene.speaker_name}
                </span>
                <span className="text-[11px] text-slate-500 font-medium">
                  {scene.location}
                </span>
              </div>

              {/* Dialogue text */}
              <p className="text-sm font-medium text-slate-200 bg-dark-900/70 p-2.5 rounded-xl border border-slate-800/80 italic">
                "{scene.dialogue_text}"
              </p>
            </div>

            {/* SFX Tags */}
            {scene.sfx && scene.sfx.length > 0 && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {scene.sfx.map((sfxItem, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[10px] font-medium flex items-center gap-1"
                  >
                    <Volume2 className="w-2.5 h-2.5" />
                    {sfxItem}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
