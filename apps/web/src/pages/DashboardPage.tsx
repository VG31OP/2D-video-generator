import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { fetchProjects, deleteProject } from '../services/api';
import { Project } from '../types';
import { Sparkles, Play, Trash2, Clock, Film, Plus, AlertCircle, RefreshCw, Eye } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const navigate = useNavigate();

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await fetchProjects();
      setProjects(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this short?')) return;
    try {
      await deleteProject(id);
      setProjects((prev) => prev.filter((p) => p.id !== id));
    } catch (err: any) {
      alert(err.message || 'Failed to delete');
    }
  };

  const filteredProjects = projects.filter((p) => {
    if (filter === 'completed') return p.status === 'Completed';
    if (filter === 'generating') return p.status === 'Generating' || p.status === 'Planning' || p.status === 'Rendering';
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* Top Hero Banner */}
      <div className="relative rounded-3xl overflow-hidden glass-panel-glow p-8 sm:p-12 border border-purple-500/30">
        <div className="relative z-10 max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-purple-500/20 border border-purple-500/40 text-purple-300 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-pink-400" />
            <span>Autonomous Cartoon Generation</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-black font-display text-white tracking-tight leading-tight">
            Turn Any Topic Into A <span className="gradient-text">Viral YouTube Short</span>
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Zero editing required. Enter a title and ToonForge automatically crafts the story, character bible, 2D cartoon scenes, voice acting, dynamic subtitles, and final 9:16 MP4 video.
          </p>
          <div className="pt-2 flex flex-wrap gap-4">
            <Link
              to="/create"
              className="px-6 py-3.5 rounded-2xl text-base font-bold text-white bg-gradient-to-r from-purple-600 via-pink-600 to-amber-500 hover:from-purple-500 hover:to-amber-400 shadow-xl shadow-purple-600/30 transition-all duration-300 flex items-center gap-2.5 hover:scale-105 active:scale-95"
            >
              <Sparkles className="w-5 h-5" />
              <span>Create New Short</span>
            </Link>
          </div>
        </div>

        {/* Decorative Background Blob */}
        <div className="absolute right-[-10%] top-[-20%] w-[500px] h-[500px] bg-gradient-to-br from-purple-600/20 via-pink-600/20 to-transparent rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Projects List Header & Filter Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold font-display text-white">Your Cartoon Shorts</h2>
          <p className="text-xs text-slate-400">Manage and preview your generated 9:16 animations</p>
        </div>

        <div className="flex items-center gap-2">
          {['all', 'completed', 'generating'].map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold capitalize transition ${
                filter === tab
                  ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                  : 'bg-dark-900 border border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab}
            </button>
          ))}
          <button
            onClick={loadProjects}
            className="p-2 rounded-xl bg-dark-900 border border-slate-800 text-slate-400 hover:text-white transition"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Loading & Error States */}
      {loading && projects.length === 0 && (
        <div className="py-20 text-center space-y-4">
          <RefreshCw className="w-8 h-8 text-pink-400 animate-spin mx-auto" />
          <p className="text-sm text-slate-400 font-medium">Loading your projects...</p>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-2xl bg-red-950/40 border border-red-800/50 text-red-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Empty State */}
      {!loading && filteredProjects.length === 0 && (
        <div className="glass-panel rounded-3xl p-12 text-center space-y-6 max-w-lg mx-auto border border-slate-800">
          <div className="w-16 h-16 rounded-3xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mx-auto text-purple-400">
            <Film className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-lg font-bold text-white">No cartoon shorts found</h3>
            <p className="text-xs text-slate-400">Generate your first autonomous AI short in seconds.</p>
          </div>
          <div className="pt-2 space-y-2">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Try these viral prompts:</span>
            <div className="space-y-1.5">
              {[
                'A lazy student accidentally creates an AI that becomes smarter than him',
                'My orange cat found my unlocked phone and ordered 500 pizzas',
                'When you accidentally press the big red button in a secret lab',
              ].map((idea, idx) => (
                <button
                  key={idx}
                  onClick={() => navigate('/create', { state: { topic: idea } })}
                  className="w-full p-2.5 rounded-xl bg-dark-900 border border-slate-800 text-left text-xs font-medium text-slate-300 hover:text-purple-300 hover:border-purple-500/40 transition truncate"
                >
                  ✨ {idea}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Projects Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredProjects.map((project) => (
          <div
            key={project.id}
            onClick={() => {
              if (project.status === 'Completed') {
                navigate(`/project/${project.id}/result`);
              } else {
                navigate(`/project/${project.id}/generate`);
              }
            }}
            className="group glass-panel rounded-3xl overflow-hidden border border-slate-800 hover:border-purple-500/50 transition-all duration-300 cursor-pointer flex flex-col justify-between hover:shadow-2xl hover:shadow-purple-900/20"
          >
            {/* Thumbnail Poster Aspect 9:16 Card */}
            <div className="relative aspect-[9/16] max-h-[380px] bg-dark-950 overflow-hidden flex items-center justify-center">
              {project.thumbnail_url ? (
                <img
                  src={project.thumbnail_url}
                  alt={project.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
              ) : (
                <div className="p-8 text-center space-y-2">
                  <Film className="w-12 h-12 text-slate-700 mx-auto" />
                  <p className="text-xs text-slate-500">Generating preview...</p>
                </div>
              )}

              {/* Status Badge */}
              <div className="absolute top-3 left-3">
                <span
                  className={`px-3 py-1 rounded-full text-xs font-bold backdrop-blur-md border ${
                    project.status === 'Completed'
                      ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40'
                      : project.status === 'Failed'
                      ? 'bg-red-950/80 text-red-300 border-red-500/40'
                      : 'bg-purple-950/80 text-purple-300 border-purple-500/40 animate-pulse'
                  }`}
                >
                  {project.status === 'Completed' ? '✓ Ready' : project.status}
                </span>
              </div>

              {/* Duration Badge */}
              {project.duration_seconds > 0 && (
                <div className="absolute top-3 right-3 px-2.5 py-1 rounded-full bg-black/70 backdrop-blur-md text-[11px] font-mono text-white border border-white/10 flex items-center gap-1">
                  <Clock className="w-3 h-3 text-pink-400" />
                  <span>{project.duration_seconds.toFixed(0)}s</span>
                </div>
              )}

              {/* Hover Action Overlay */}
              <div className="absolute inset-0 bg-black/50 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-3">
                <div className="w-14 h-14 rounded-full bg-pink-500 text-white flex items-center justify-center shadow-xl shadow-pink-500/40 transform scale-90 group-hover:scale-100 transition-transform">
                  <Play className="w-6 h-6 fill-white ml-1" />
                </div>
              </div>
            </div>

            {/* Project Details */}
            <div className="p-5 space-y-3 flex-1 flex flex-col justify-between">
              <div>
                <h3 className="font-bold text-base text-white group-hover:text-pink-400 transition-colors line-clamp-1">
                  {project.title}
                </h3>
                <p className="text-xs text-slate-400 line-clamp-2 mt-1">
                  {project.topic}
                </p>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-xs text-slate-500">
                <span>{project.art_style}</span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={(e) => handleDelete(project.id, e)}
                    className="p-1.5 rounded-lg hover:bg-red-500/20 text-slate-500 hover:text-red-400 transition"
                    title="Delete Short"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
