import React, { useRef, useState, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, RotateCcw, Maximize, Download, Sparkles } from 'lucide-react';

interface VideoPlayerProps {
  src: string;
  poster?: string;
  title?: string;
  autoPlay?: boolean;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ src, poster, title, autoPlay = true }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    const current = videoRef.current.currentTime;
    const total = videoRef.current.duration || 1;
    setCurrentTime(current);
    setProgress((current / total) * 100);
  };

  const handleLoadedMetadata = () => {
    if (!videoRef.current) return;
    setDuration(videoRef.current.duration || 0);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!videoRef.current) return;
    const seekTo = (parseFloat(e.target.value) / 100) * duration;
    videoRef.current.currentTime = seekTo;
    setProgress(parseFloat(e.target.value));
  };

  const toggleFullscreen = () => {
    if (!videoRef.current) return;
    if (videoRef.current.requestFullscreen) {
      videoRef.current.requestFullscreen();
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="relative w-full max-w-[360px] mx-auto aspect-[9/16] rounded-3xl overflow-hidden shadow-2xl shadow-purple-900/30 border-2 border-slate-800 bg-black group select-none">
      {/* 9:16 Video */}
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        className="w-full h-full object-cover cursor-pointer"
        onClick={togglePlay}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        loop
        playsInline
        autoPlay={autoPlay}
      />

      {/* Top Overlay Badge */}
      <div className="absolute top-4 left-4 right-4 flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-xs font-semibold text-white">
          <span className="w-2 h-2 rounded-full bg-pink-500 animate-ping"></span>
          <span>9:16 HD Short</span>
        </div>
        <div className="px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-[11px] font-mono text-purple-300">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
      </div>

      {/* Center Play Overlay Icon when Paused */}
      {!isPlaying && (
        <div
          onClick={togglePlay}
          className="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer transition-opacity duration-300"
        >
          <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-purple-600 to-pink-500 flex items-center justify-center shadow-xl shadow-pink-500/40 transform group-hover:scale-110 transition-transform">
            <Play className="w-7 h-7 text-white fill-white ml-1" />
          </div>
        </div>
      )}

      {/* Bottom Controls Bar */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/90 via-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        {/* Progress Slider */}
        <input
          type="range"
          min="0"
          max="100"
          value={progress}
          onChange={handleSeek}
          className="w-full h-1.5 bg-slate-700/60 rounded-lg appearance-none cursor-pointer accent-pink-500 mb-3"
        />

        {/* Buttons Row */}
        <div className="flex items-center justify-between text-white">
          <div className="flex items-center gap-3">
            <button
              onClick={togglePlay}
              className="p-1.5 rounded-lg hover:bg-white/20 transition"
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 fill-white" />}
            </button>
            <button
              onClick={toggleMute}
              className="p-1.5 rounded-lg hover:bg-white/20 transition"
              title={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? <VolumeX className="w-5 h-5 text-red-400" /> : <Volume2 className="w-5 h-5" />}
            </button>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={src}
              download={`${title || 'toonforge_short'}.mp4`}
              className="p-1.5 rounded-lg hover:bg-white/20 transition text-pink-400 hover:text-pink-300"
              title="Download MP4"
            >
              <Download className="w-5 h-5" />
            </a>
            <button
              onClick={toggleFullscreen}
              className="p-1.5 rounded-lg hover:bg-white/20 transition"
              title="Fullscreen"
            >
              <Maximize className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
