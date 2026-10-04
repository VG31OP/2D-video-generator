import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { fetchProject, triggerGenerate } from '../services/api';
import { Project } from '../types';
import { VideoPlayer } from '../components/VideoPlayer';
import { CharacterBibleViewer } from '../components/CharacterBibleViewer';
import { SceneStoryboard } from '../components/SceneStoryboard';
import { MetadataCard } from '../components/MetadataCard';
import { Sparkles, Download, RefreshCw, Film, Users, BookOpen, Share2, ArrowLeft, CheckCircle2 } from 'lucide-react';

export const ResultPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'storyboard' | 'characters' | 'script'>('storyboard');
  const [isRegenerating, setIsRegenerating] = useState(false);

  useEffect(() => {
    if (!id) return;
    fetchProject(id)
      .then((data) => {
        setProject(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [id]);

  const handleRegenerate = async () => {
    if (!id) return;
    if (!window.confirm('Regenerate this cartoon short from scratch?')) return;
    try {
      setIsRegenerating(true);
      await triggerGenerate(id);
      navigate(`/project/${id}/generate`);
    } catch (err: any) {
      alert(err.message || 'Failed to regenerate');
      setIsRegenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="py-32 text-center space-y-4">
        <RefreshCw className="w-10 h-10 text-pink-400 animate-spin mx-auto" />
        <p className="text-sm text-slate-400">Loading your finalized cartoon short...</p>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="py-20 text-center space-y-4">
        <p className="text-red-400">Project not found</p>
        <Link to="/" className="text-purple-400 underline text-sm">Return to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-10">
      {/* Top Navigation & Status */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            to="/"
            className="p-2.5 rounded-xl bg-dark-900 border border-slate-800 text-slate-400 hover:text-white transition"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[11px] font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                <span>Ready For YouTube Shorts</span>
              </span>
              <span className="text-xs font-mono text-slate-500">1080x1920 MP4</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black font-display text-white mt-1">
              {project.title}
            </h1>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="px-4 py-2.5 rounded-xl bg-dark-900 border border-slate-700 text-xs font-semibold text-slate-300 hover:text-white hover:border-purple-500 transition flex items-center gap-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRegenerating ? 'animate-spin' : ''}`} />
            <span>Regenerate</span>
          </button>

          {project.video_url && (
            <a
              href={project.video_url}
              download={`${project.title.replace(/\s+/g, '_')}.mp4`}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white text-xs font-bold shadow-lg shadow-purple-600/30 transition-all flex items-center gap-2 hover:scale-105"
            >
              <Download className="w-4 h-4" />
              <span>Download MP4</span>
            </a>
          )}
        </div>
      </div>

      {/* Main Split: 9:16 Video Player on Left, Metadata & Details on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Player Column */}
        <div className="lg:col-span-5 flex flex-col items-center">
          {project.video_url ? (
            <VideoPlayer
              src={project.video_url}
              poster={project.thumbnail_url}
              title={project.title}
            />
          ) : (
            <div className="w-full aspect-[9/16] rounded-3xl bg-dark-950 border border-slate-800 flex items-center justify-center p-8 text-center text-slate-500">
              No video available
            </div>
          )}

          {/* Quick Actions Under Player */}
          <div className="w-full max-w-[360px] mt-4 flex gap-2">
            {project.thumbnail_url && (
              <a
                href={project.thumbnail_url}
                download={`${project.title.replace(/\s+/g, '_')}_thumb.jpg`}
                className="flex-1 py-2.5 rounded-xl bg-dark-900 border border-slate-800 hover:border-slate-700 text-center text-xs font-semibold text-slate-300 hover:text-white transition flex items-center justify-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5 text-pink-400" />
                <span>Thumbnail</span>
              </a>
            )}
            <Link
              to="/create"
              className="flex-1 py-2.5 rounded-xl bg-purple-600/20 border border-purple-500/40 text-center text-xs font-semibold text-purple-300 hover:text-white hover:bg-purple-600/30 transition flex items-center justify-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5 text-pink-400" />
              <span>New Short</span>
            </Link>
          </div>
        </div>

        {/* Right Metadata & Inspector Column */}
        <div className="lg:col-span-7 space-y-6">
          {/* YouTube Metadata Box */}
          <MetadataCard
            metadata={project.metadata}
            title={project.title}
          />

          {/* Tab Navigation */}
          <div className="flex border-b border-slate-800/80 gap-6 text-sm font-semibold">
            <button
              onClick={() => setActiveTab('storyboard')}
              className={`pb-3 flex items-center gap-2 transition border-b-2 ${
                activeTab === 'storyboard'
                  ? 'border-pink-500 text-white'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Film className="w-4 h-4 text-pink-400" />
              <span>Storyboard ({project.scenes?.length || 0} Scenes)</span>
            </button>

            <button
              onClick={() => setActiveTab('characters')}
              className={`pb-3 flex items-center gap-2 transition border-b-2 ${
                activeTab === 'characters'
                  ? 'border-pink-500 text-white'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Users className="w-4 h-4 text-purple-400" />
              <span>Character Bible ({project.characters?.length || 0})</span>
            </button>

            <button
              onClick={() => setActiveTab('script')}
              className={`pb-3 flex items-center gap-2 transition border-b-2 ${
                activeTab === 'script'
                  ? 'border-pink-500 text-white'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <BookOpen className="w-4 h-4 text-amber-400" />
              <span>Story & Script</span>
            </button>
          </div>

          {/* Tab Contents */}
          <div className="pt-2">
            {activeTab === 'storyboard' && (
              <SceneStoryboard scenes={project.scenes || []} />
            )}

            {activeTab === 'characters' && (
              <CharacterBibleViewer characters={project.characters || []} />
            )}

            {activeTab === 'script' && (
              <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-6">
                <div className="space-y-2">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-pink-400">Viral Hook (0-3s)</h3>
                  <p className="text-base text-white font-semibold italic bg-dark-900/80 p-3.5 rounded-xl border border-slate-800">
                    "{project.story?.hook || 'No hook generated'}"
                  </p>
                </div>

                <div className="space-y-2">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-purple-400">Synopsis</h3>
                  <p className="text-sm text-slate-300 leading-relaxed">
                    {project.story?.synopsis || project.topic}
                  </p>
                </div>

                <div className="space-y-3">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400">Scene Dialogue Breakdown</h3>
                  <div className="space-y-2">
                    {project.scenes?.map((s) => (
                      <div key={s.id} className="p-3 rounded-xl bg-dark-900 border border-slate-800/80 text-xs">
                        <span className="font-bold text-pink-400 mr-2">Scene {s.scene_number} ({s.speaker_name}):</span>
                        <span className="text-slate-200">"{s.dialogue_text}"</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
