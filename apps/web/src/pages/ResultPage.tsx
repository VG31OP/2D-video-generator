import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { fetchProject, triggerGenerate, uploadToInstagramReels } from '../services/api';
import { useInstagramLoginPolling } from '../hooks/useInstagramLoginPolling';
import { Project } from '../types';
import { VideoPlayer } from '../components/VideoPlayer';
import { CharacterBibleViewer } from '../components/CharacterBibleViewer';
import { SceneStoryboard } from '../components/SceneStoryboard';
import { MetadataCard } from '../components/MetadataCard';
import { Sparkles, Download, RefreshCw, Film, Users, BookOpen, Share2, ArrowLeft, CheckCircle2, Send, ExternalLink, X } from 'lucide-react';

const InstagramIcon: React.FC<{ className?: string }> = ({ className = "w-4 h-4" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="20" x="2" y="2" rx="5" ry="5" />
    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
    <line x1="17.5" x2="17.51" y1="6.5" y2="6.5" />
  </svg>
);

export const ResultPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'storyboard' | 'characters' | 'script'>('storyboard');
  const [isRegenerating, setIsRegenerating] = useState(false);

  // Instagram integration state via shared polling hook
  const { instaStatus, startLoginCapture } = useInstagramLoginPolling();
  const [showInstaModal, setShowInstaModal] = useState(false);
  const [instaCaption, setInstaCaption] = useState('');
  const [uploadingInsta, setUploadingInsta] = useState(false);
  const [instaResult, setInstaResult] = useState<{ success: boolean; url?: string; code?: string; error?: string } | null>(null);

  useEffect(() => {
    if (!id) return;
    fetchProject(id)
      .then((data) => {
        setProject(data);
        setLoading(false);
        const tags = "#reels #animation #cartoon #comedy #viral #explorepage #trending #instaanimation #shorts";
        setInstaCaption(`${data.title} 🎬✨\n\nDrop a ❤️ and follow for more animated cartoon comedy!\n.\n.\n${tags}`);
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

  const handleUploadToInsta = async () => {
    if (!id) return;
    try {
      setUploadingInsta(true);
      setInstaResult(null);
      const res = await uploadToInstagramReels(id, instaCaption);
      setInstaResult({ success: true, url: res.url, code: res.code });
    } catch (err: any) {
      setInstaResult({ success: false, error: err.message || 'Failed to publish Reel' });
    } finally {
      setUploadingInsta(false);
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
              <span className="px-2.5 py-0.5 rounded-full bg-gradient-to-r from-pink-500/20 to-purple-500/20 text-pink-400 border border-pink-500/30 text-[11px] font-bold flex items-center gap-1">
                <InstagramIcon className="w-3 h-3 text-pink-400" />
                <span>Ready For Instagram Reels & Shorts</span>
              </span>
              <span className="text-xs font-mono text-slate-500">1080x1920 9:16</span>
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
            <button
              onClick={() => setShowInstaModal(true)}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-pink-600 via-rose-500 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white text-xs font-bold shadow-lg shadow-pink-600/25 transition-all flex items-center gap-2 hover:scale-105"
            >
              <InstagramIcon className="w-4 h-4" />
              <span>Post to Instagram Reels</span>
            </button>
          )}

          {project.video_url && (
            <a
              href={project.video_url}
              download={`${project.title.replace(/\s+/g, '_')}.mp4`}
              className="px-4 py-2.5 rounded-xl bg-dark-900 border border-slate-700 hover:border-slate-600 text-white text-xs font-semibold transition-all flex items-center gap-2 hover:scale-105"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
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

      {/* Instagram Reels Publish Modal */}
      {showInstaModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-dark-950 border border-pink-500/30 rounded-3xl w-full max-w-lg p-6 sm:p-8 space-y-6 shadow-2xl shadow-pink-950/40 relative">
            <button
              onClick={() => {
                setShowInstaModal(false);
                setInstaResult(null);
              }}
              className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-white bg-dark-900 border border-slate-800 transition"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Header */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600 flex items-center justify-center shadow-lg shadow-pink-500/25">
                <InstagramIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Publish to Instagram Reels</h3>
                <p className="text-xs text-slate-400">Autonomous vertical 9:16 reel posting</p>
              </div>
            </div>

            {/* Account Status / Login Prompt */}
            {!instaStatus?.authenticated ? (
              <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 space-y-3">
                <div className="flex items-start gap-3">
                  <div className="p-1 rounded-lg bg-amber-500/20 text-amber-400 mt-0.5">
                    <InstagramIcon className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-amber-300">Instagram Account Not Connected</h4>
                    <p className="text-[11px] text-slate-300 mt-1 leading-relaxed">
                      Capture your Instagram login once. Your session will be securely stored locally, allowing 100% autonomous posting without manual steps.
                    </p>
                  </div>
                </div>
                <div className="flex flex-col sm:flex-row gap-2 pt-1">
                  <button
                    onClick={startLoginCapture}
                    className="flex-1 py-2 px-3 rounded-xl bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white text-xs font-bold transition flex items-center justify-center gap-1.5"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>Open Browser Login Capture</span>
                  </button>
                </div>
                <p className="text-[10px] text-slate-500 text-center font-mono">
                  Or run: python scripts/instagram_manager.py login
                </p>
              </div>
            ) : (
              <div className="flex items-center justify-between p-3.5 rounded-2xl bg-dark-900 border border-slate-800">
                <div className="flex items-center gap-3">
                  {instaStatus.profile?.profile_pic_url ? (
                    <img
                      src={instaStatus.profile.profile_pic_url}
                      alt="Avatar"
                      className="w-10 h-10 rounded-full object-cover border border-pink-500/40"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-pink-500/20 flex items-center justify-center text-pink-400 font-bold text-sm">
                      @{instaStatus.profile?.username?.[0]?.toUpperCase() || 'IG'}
                    </div>
                  )}
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-bold text-white">@{instaStatus.profile?.username}</span>
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" title="Active Session" />
                    </div>
                    <span className="text-[11px] text-slate-400">
                      {instaStatus.profile?.follower_count?.toLocaleString() || 0} followers • {instaStatus.profile?.media_count || 0} posts
                    </span>
                  </div>
                </div>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  Ready
                </span>
              </div>
            )}

            {/* Caption Editor */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                <span>Reel Caption & Viral Hashtags</span>
                <span className="text-[10px] text-slate-500 font-mono">{instaCaption.length} chars</span>
              </label>
              <textarea
                value={instaCaption}
                onChange={(e) => setInstaCaption(e.target.value)}
                rows={5}
                className="w-full bg-dark-900 border border-slate-800 rounded-2xl p-3.5 text-xs text-slate-200 focus:outline-none focus:border-pink-500 focus:ring-1 focus:ring-pink-500/30 font-sans leading-relaxed resize-none"
                placeholder="Write your reel caption..."
              />
            </div>

            {/* Result Message */}
            {instaResult && (
              <div
                className={`p-4 rounded-2xl border ${
                  instaResult.success
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                }`}
              >
                {instaResult.success ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs font-bold">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span>Reel Uploaded Successfully to Instagram!</span>
                    </div>
                    {instaResult.url && (
                      <a
                        href={instaResult.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1.5 text-xs font-bold text-pink-400 hover:text-pink-300 underline"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span>View Reel: {instaResult.url}</span>
                      </a>
                    )}
                  </div>
                ) : (
                  <p className="text-xs">{instaResult.error || 'Failed to upload reel.'}</p>
                )}
              </div>
            )}

            {/* Action Footer */}
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setShowInstaModal(false)}
                className="px-4 py-2.5 rounded-xl bg-dark-900 border border-slate-800 text-xs font-semibold text-slate-400 hover:text-white transition"
              >
                Close
              </button>
              <button
                onClick={handleUploadToInsta}
                disabled={uploadingInsta || !instaStatus?.authenticated || !!instaResult?.success}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-pink-600 via-rose-500 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white text-xs font-bold shadow-lg shadow-pink-600/30 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105"
              >
                {uploadingInsta ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Uploading Reel...</span>
                  </>
                ) : instaResult?.success ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Reel Published</span>
                  </>
                ) : (
                  <>
                    <Send className="w-3.5 h-3.5" />
                    <span>Publish Reel Now</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
