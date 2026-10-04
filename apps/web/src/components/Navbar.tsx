import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sparkles, Video, Film, Settings, Cpu, CheckCircle2 } from 'lucide-react';
import { fetchSystemHealth } from '../services/api';
import { SystemCapabilities } from '../types';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [caps, setCaps] = useState<SystemCapabilities | null>(null);

  useEffect(() => {
    fetchSystemHealth()
      .then((data) => setCaps(data))
      .catch(() => {});
  }, []);

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-dark-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-pink-500 to-amber-400 p-[2px] shadow-lg shadow-purple-500/20 group-hover:shadow-pink-500/30 transition-all duration-300">
            <div className="w-full h-full bg-dark-950 rounded-[10px] flex items-center justify-center">
              <Film className="w-5 h-5 text-pink-400 group-hover:scale-110 transition-transform duration-300" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-display font-extrabold text-xl tracking-tight text-white">Toon<span className="text-pink-500">Forge</span></span>
              <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-purple-500/20 text-purple-400 border border-purple-500/30 rounded-full">AI SHORTS</span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Autonomous 2D Cartoon Engine</p>
          </div>
        </Link>

        {/* Center Live Capability Pill */}
        {caps && (
          <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-dark-900 border border-slate-800 text-[11px] font-mono text-slate-400">
            <div className="flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${caps.llm.ollama_available ? 'bg-emerald-400' : 'bg-purple-400'}`}></span>
              <span>LLM: {caps.llm.ollama_available ? 'Ollama' : 'Smart Engine'}</span>
            </div>
            <span className="text-slate-700">|</span>
            <div className="flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${caps.voice.edge_tts_available ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
              <span>Voice: {caps.voice.edge_tts_available ? 'Neural TTS' : 'Synth'}</span>
            </div>
            <span className="text-slate-700">|</span>
            <div className="flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${caps.hardware.cuda_available ? 'bg-emerald-400' : 'bg-blue-400'}`}></span>
              <span>GPU: {caps.hardware.cuda_available ? caps.hardware.gpu_name.slice(0, 12) : 'CPU Mode'}</span>
            </div>
          </div>
        )}

        {/* Navigation Links */}
        <nav className="flex items-center gap-1 sm:gap-2">
          <Link
            to="/"
            className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
              isActive('/') && location.pathname === '/'
                ? 'bg-purple-600/15 text-purple-400 border border-purple-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Video className="w-4 h-4" />
            <span>Dashboard</span>
          </Link>

          <Link
            to="/settings"
            className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
              isActive('/settings')
                ? 'bg-purple-600/15 text-purple-400 border border-purple-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </Link>

          <Link
            to="/create"
            className="ml-2 sm:ml-4 px-4 py-2 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-purple-600 via-pink-600 to-amber-500 hover:from-purple-500 hover:to-amber-400 shadow-lg shadow-purple-600/25 hover:shadow-pink-500/35 transition-all duration-300 flex items-center gap-2 hover:scale-[1.02] active:scale-[0.98]"
          >
            <Sparkles className="w-4 h-4 animate-pulse" />
            <span>Create Short</span>
          </Link>
        </nav>
      </div>
    </header>
  );
};
