import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { createProject } from '../services/api';
import { Sparkles, Sliders, Play, ChevronDown, ChevronUp, Zap, Wand2 } from 'lucide-react';

export const CreateShortPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const [topic, setTopic] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Advanced Options (Hidden by default)
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [artStyle, setArtStyle] = useState('Modern 2D Cartoon');
  const [language, setLanguage] = useState('English');
  const [duration, setDuration] = useState(30);

  useEffect(() => {
    if (location.state && location.state.topic) {
      setTopic(location.state.topic);
    }
  }, [location.state]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) {
      setError('Please enter a video topic or idea');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      const res = await createProject({
        topic: topic.trim(),
        art_style: artStyle,
        language: language,
        duration_seconds: duration,
      });

      navigate(`/project/${res.id}/generate`);
    } catch (err: any) {
      setError(err.message || 'Failed to start short generation');
      setIsSubmitting(false);
    }
  };

  const STYLE_PRESETS = [
    { id: 'Modern 2D Cartoon', name: 'Modern 2D', icon: '🎨', badge: 'Crisp Vectors' },
    { id: 'Pixel Art 16-Bit Arcade', name: 'Pixel Art', icon: '👾', badge: '16-Bit Retro' },
    { id: 'Dark Noir Detective', name: 'Dark Noir', icon: '🕵️', badge: 'Dramatic B&W' },
    { id: 'Comic Book Pop Art', name: 'Comic Pop', icon: '💥', badge: 'Halftone Dots' },
    { id: 'Cyberpunk Neon Animated', name: 'Cyberpunk', icon: '⚡', badge: 'Synthwave Glow' },
    { id: 'Chibi / Kawaii Cute', name: 'Chibi Kawaii', icon: '🐣', badge: 'Cute Pastel' },
    { id: '90s Saturday Morning Retro', name: '90s Retro', icon: '📺', badge: 'Classic Inks' },
    { id: 'Doodle / Stick Figure Comedy', name: 'Doodle Stick', icon: '✏️', badge: 'Notebook Line' },
    { id: 'Anime Comic Shorts', name: 'Anime Shorts', icon: '⚔️', badge: 'Cel Shading' },
    { id: 'Claymation / Stop-Motion Style', name: 'Claymation', icon: '🏺', badge: 'Stop-Motion' },
  ];

  const sampleIdeas = [
    'A lazy student accidentally creates an AI that becomes smarter than him',
    'My orange cat found my unlocked phone and ordered 500 pizzas',
    'When you accidentally press the big red button in a secret lab',
    'A guy challenges a gym bro to a workout without knowing anything',
    'When you lie on your resume and actually get hired as NASA pilot',
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-16 space-y-10">
      {/* Title Header */}
      <div className="text-center space-y-4 max-w-2xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-pink-500/10 border border-pink-500/30 text-pink-400 text-xs font-semibold uppercase tracking-wider">
          <Wand2 className="w-3.5 h-3.5" />
          <span>Title In → Finished Short Out</span>
        </div>
        <h1 className="text-4xl sm:text-5xl font-black font-display text-white tracking-tight">
          Create An Autonomous <span className="gradient-text">Cartoon Short</span>
        </h1>
        <p className="text-slate-400 text-sm sm:text-base">
          No video editing skills needed. Simply enter what your cartoon should be about.
        </p>
      </div>

      {/* Main Creation Card */}
      <form onSubmit={handleSubmit} className="glass-panel-glow rounded-3xl p-6 sm:p-10 border border-purple-500/30 space-y-8">
        {/* Primary Prompt Input */}
        <div className="space-y-3">
          <label className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-pink-400" />
            <span>What should this cartoon be about?</span>
          </label>
          <div className="relative">
            <textarea
              rows={4}
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. A lazy student accidentally creates an AI that becomes smarter than him..."
              className="w-full bg-dark-900/90 border-2 border-slate-700/80 focus:border-pink-500 rounded-2xl p-4 text-base sm:text-lg text-white placeholder-slate-500 focus:outline-none focus:ring-4 focus:ring-pink-500/20 transition-all resize-none"
              disabled={isSubmitting}
            />
          </div>
        </div>

        {/* Quick Inspiration Pills */}
        <div className="space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Quick Ideas:</span>
          <div className="flex flex-wrap gap-2">
            {sampleIdeas.map((idea, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setTopic(idea)}
                className="px-3 py-1.5 rounded-xl bg-dark-900/80 border border-slate-800 text-xs text-slate-300 hover:text-white hover:border-purple-500/50 hover:bg-purple-950/30 transition-all truncate max-w-full text-left"
              >
                💡 {idea}
              </button>
            ))}
          </div>
        </div>

        {/* Visual Cartoon Style Grid */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <span>Choose Animation / Cartoon Style</span>
              <span className="text-pink-400 font-semibold lowercase">({artStyle})</span>
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
            {STYLE_PRESETS.map((preset) => {
              const isSelected = artStyle === preset.id;
              return (
                <button
                  key={preset.id}
                  type="button"
                  onClick={() => setArtStyle(preset.id)}
                  className={`p-3 rounded-2xl border text-left transition-all relative overflow-hidden group ${
                    isSelected
                      ? 'bg-purple-600/20 border-pink-500 shadow-lg shadow-pink-500/20 ring-1 ring-pink-500/50'
                      : 'bg-dark-900/70 border-slate-800 hover:border-slate-700 hover:bg-dark-900'
                  }`}
                >
                  <div className="text-xl mb-1">{preset.icon}</div>
                  <div className={`text-xs font-bold truncate ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                    {preset.name}
                  </div>
                  <div className="text-[10px] text-slate-400 truncate">
                    {preset.badge}
                  </div>
                  {isSelected && (
                    <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-pink-400 shadow-sm shadow-pink-400" />
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Advanced Settings Drawer */}
        <div className="border-t border-slate-800/80 pt-4">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition"
          >
            <Sliders className="w-3.5 h-3.5 text-purple-400" />
            <span>Advanced Configuration (Optional)</span>
            {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showAdvanced && (
            <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4 p-5 rounded-2xl bg-dark-900/60 border border-slate-800">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400">Cartoon Style</label>
                <select
                  value={artStyle}
                  onChange={(e) => setArtStyle(e.target.value)}
                  className="w-full bg-dark-950 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-purple-500"
                >
                  <option value="Modern 2D Cartoon">Modern 2D Cartoon (Crisp Vectors - Default)</option>
                  <option value="Anime Comic Shorts">Anime Comic Shorts (Action Lines & Cel Shading)</option>
                  <option value="90s Saturday Morning Retro">90s Saturday Morning Retro (Classic Inks & Bold Lines)</option>
                  <option value="Chibi / Kawaii Cute">Chibi / Kawaii Cute (Expressive & Playful)</option>
                  <option value="Comic Book Pop Art">Comic Book Pop Art (Vintage Halftone Dots)</option>
                  <option value="Cyberpunk Neon Animated">Cyberpunk Neon Animated (Synthwave Glow & Dystopian)</option>
                  <option value="Dark Noir Detective">Dark Noir Detective (High-Contrast Dramatic Shadows)</option>
                  <option value="Doodle / Stick Figure Comedy">Doodle / Stick Figure Comedy (Viral Minimalist)</option>
                  <option value="Pixel Art 16-Bit Arcade">Pixel Art 16-Bit Arcade (Retro Video Game)</option>
                  <option value="Claymation / Stop-Motion Style">Claymation / Stop-Motion Style (Tactile Textured)</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400">Dialogue Language</label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full bg-dark-950 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-purple-500"
                >
                  <option value="English">English</option>
                  <option value="Hindi">Hindi</option>
                  <option value="Hinglish">Hinglish</option>
                  <option value="Gujarati">Gujarati</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400">Target Duration</label>
                <select
                  value={duration}
                  onChange={(e) => setDuration(parseInt(e.target.value))}
                  className="w-full bg-dark-950 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-purple-500"
                >
                  <option value={30}>30 Seconds (Fast Paced - Recommended)</option>
                  <option value={45}>45 Seconds (Standard)</option>
                  <option value={60}>60 Seconds (Full Story)</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 rounded-xl bg-red-950/50 border border-red-800/60 text-red-300 text-xs">
            {error}
          </div>
        )}

        {/* Primary CTA Button */}
        <button
          type="submit"
          disabled={isSubmitting || !topic.trim()}
          className="w-full py-4 rounded-2xl text-lg font-extrabold text-white bg-gradient-to-r from-purple-600 via-pink-600 to-amber-500 hover:from-purple-500 hover:to-amber-400 shadow-xl shadow-purple-600/30 hover:shadow-pink-500/40 transition-all duration-300 flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.01] active:scale-[0.99]"
        >
          <Sparkles className="w-5 h-5 animate-pulse" />
          <span>{isSubmitting ? 'Initializing AI Pipeline...' : 'Generate Short 🎬'}</span>
        </button>
      </form>
    </div>
  );
};
