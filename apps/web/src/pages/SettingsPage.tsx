import React, { useEffect, useState } from 'react';
import { fetchSettings, updateSettings, testOllamaConnection, testGeminiConnection, fetchSystemHealth, testAllProviders } from '../services/api';
import { useInstagramLoginPolling } from '../hooks/useInstagramLoginPolling';
import { Settings, SystemCapabilities } from '../types';
import { Settings as SettingsIcon, Cpu, Mic, Image as ImageIcon, CheckCircle, AlertCircle, Save, RefreshCw, Sparkles, Server, HardDrive, Play, Check, X, ShieldAlert, Key, Eye, EyeOff, ExternalLink } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<Settings>({
    llm_provider: 'auto',
    gemini_api_key: '',
    gemini_model: 'gemini-2.0-flash',
    ollama_base_url: 'http://localhost:11434',
    ollama_model: 'llama3.2',
    image_provider: 'toon_vector',
    voice_provider: 'edge_tts',
    animation_provider: 'motion_comic',
    default_style: 'Modern 2D Cartoon',
    default_language: 'English',
    default_duration: 30,
    width: 1080,
    height: 1920,
    fps: 30,
  });

  const [caps, setCaps] = useState<SystemCapabilities | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [testingOllama, setTestingOllama] = useState(false);
  const [ollamaStatus, setOllamaStatus] = useState<{ connected: boolean; models?: string[]; error?: string } | null>(null);
  const [testingGemini, setTestingGemini] = useState(false);
  const [geminiStatus, setGeminiStatus] = useState<{ connected: boolean; model?: string; displayName?: string; error?: string } | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);
  const [runningAllTests, setRunningAllTests] = useState(false);
  const [diagnosticsResults, setDiagnosticsResults] = useState<any | null>(null);

  const { instaStatus, startLoginCapture, launchingLogin } = useInstagramLoginPolling();

  const loadData = () => {
    Promise.all([fetchSettings(), fetchSystemHealth()])
      .then(([sData, cData]) => {
        setSettings(sData);
        setCaps(cData);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      await updateSettings(settings);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      alert(err.message || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleTestOllama = async () => {
    try {
      setTestingOllama(true);
      setOllamaStatus(null);
      const res = await testOllamaConnection(settings.ollama_base_url);
      setOllamaStatus(res);
      loadData();
    } catch (err: any) {
      setOllamaStatus({ connected: false, error: err.message });
    } finally {
      setTestingOllama(false);
    }
  };

  const handleTestGemini = async () => {
    try {
      setTestingGemini(true);
      setGeminiStatus(null);
      const res = await testGeminiConnection(settings.gemini_api_key, settings.gemini_model);
      setGeminiStatus(res);
      loadData();
    } catch (err: any) {
      setGeminiStatus({ connected: false, error: err.message });
    } finally {
      setTestingGemini(false);
    }
  };


  const handleRunAllTests = async () => {
    try {
      setRunningAllTests(true);
      const res = await testAllProviders();
      setDiagnosticsResults(res);
      loadData();
    } catch (err: any) {
      alert('Error testing providers: ' + err.message);
    } finally {
      setRunningAllTests(false);
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center space-y-4">
        <RefreshCw className="w-8 h-8 text-pink-400 animate-spin mx-auto" />
        <p className="text-sm text-slate-400">Loading system settings & AI health status...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold font-display text-white">System & AI Configuration</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Real-time status of local AI models, hardware acceleration, voice synthesis, and rendering.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRunAllTests}
            disabled={runningAllTests}
            className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-xs font-semibold text-white flex items-center gap-1.5 shadow-md shadow-purple-600/20 transition"
          >
            <Play className={`w-3.5 h-3.5 ${runningAllTests ? 'animate-spin' : ''}`} />
            <span>{runningAllTests ? 'Testing...' : 'Test All Providers'}</span>
          </button>
          <button
            onClick={loadData}
            className="px-3.5 py-2 rounded-xl bg-dark-900 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white flex items-center gap-1.5 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Provider Diagnostics Grid */}
      <div className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-6">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Server className="w-4 h-4 text-purple-400" />
            <span>Provider Diagnostics (Real Local Health)</span>
          </h3>
          <span className="text-[10px] font-mono text-slate-500">Auto-Detect on Startup</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          {/* System */}
          <div className="p-4 rounded-2xl bg-dark-900/90 border border-slate-800 space-y-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">System</span>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Python</span>
                <span className="font-mono text-emerald-400 font-bold flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> {caps?.system?.python_version || 'OK'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">FFmpeg</span>
                <span className={`font-mono font-bold flex items-center gap-1 ${caps?.rendering?.ffmpeg_available ? 'text-emerald-400' : 'text-red-400'}`}>
                  {caps?.rendering?.ffmpeg_available ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
                  {caps?.rendering?.ffmpeg_available ? 'Ready' : 'Missing'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">CUDA</span>
                <span className={`font-mono font-bold flex items-center gap-1 ${caps?.hardware?.cuda_available ? 'text-emerald-400' : 'text-blue-400'}`}>
                  {caps?.hardware?.cuda_available ? <Check className="w-3.5 h-3.5" /> : 'CPU'}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 truncate pt-1 border-t border-slate-800">
                {caps?.hardware?.gpu_name || 'CPU Mode'}
              </div>
            </div>
          </div>

          {/* AI Engines */}
          <div className="p-4 rounded-2xl bg-dark-900/90 border border-slate-800 space-y-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">AI Generation</span>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Gemini</span>
                <span className={`font-mono font-bold flex items-center gap-1 ${caps?.llm?.gemini_available ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {caps?.llm?.gemini_available ? <Check className="w-3.5 h-3.5" /> : (caps?.llm?.gemini_configured ? 'API Err' : 'No Key')}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Ollama</span>
                <span className={`font-mono font-bold flex items-center gap-1 ${caps?.llm?.ollama_available ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {caps?.llm?.ollama_available ? <Check className="w-3.5 h-3.5" /> : 'Offline'}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 truncate pt-1 border-t border-slate-800">
                Active: <span className="text-purple-400 font-semibold">{caps?.llm?.gemini_available ? `Gemini (${caps?.llm?.configured_model || 'Flash'})` : (caps?.llm?.ollama_available ? 'Ollama' : 'Smart Engine')}</span>
              </div>
            </div>
          </div>

          {/* Voice */}
          <div className="p-4 rounded-2xl bg-dark-900/90 border border-slate-800 space-y-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Voice (TTS)</span>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Kokoro</span>
                <span className={`font-mono font-bold flex items-center gap-1 ${caps?.voice?.kokoro_available ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {caps?.voice?.kokoro_available ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Piper</span>
                <span className={`font-mono font-bold flex items-center gap-1 ${caps?.voice?.piper_available ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {caps?.voice?.piper_available ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">EdgeTTS</span>
                <span className={`font-mono font-bold flex items-center gap-1 ${caps?.voice?.edge_tts_available ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {caps?.voice?.edge_tts_available ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 truncate pt-1 border-t border-slate-800">
                Active: {caps?.voice?.edge_tts_available ? 'Neural EdgeTTS' : 'Offline Synth'}
              </div>
            </div>
          </div>

          {/* Speech / LipSync */}
          <div className="p-4 rounded-2xl bg-dark-900/90 border border-slate-800 space-y-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Speech & LipSync</span>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Whisper</span>
                <span className={`font-mono font-bold flex items-center gap-1 ${caps?.speech?.whisper_available ? 'text-emerald-400' : 'text-blue-400'}`}>
                  {caps?.speech?.whisper_available ? <Check className="w-3.5 h-3.5" /> : 'Edge Sync'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Lip Sync</span>
                <span className="font-mono text-blue-400 font-bold">MouthFlap</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Animation</span>
                <span className="font-mono text-purple-400 font-bold">MotionComic</span>
              </div>
              <div className="text-[10px] text-slate-500 truncate pt-1 border-t border-slate-800">
                Auto Timing Sync Active
              </div>
            </div>
          </div>
        </div>

        {/* Diagnostics Results Live Output */}
        {diagnosticsResults && (
          <div className="p-4 rounded-2xl bg-black/80 border border-purple-500/30 font-mono text-xs space-y-2">
            <div className="flex items-center gap-2 text-purple-400 font-bold">
              <CheckCircle className="w-4 h-4" />
              <span>Provider Self-Test Report</span>
            </div>
            <pre className="text-slate-300 text-[11px] overflow-x-auto whitespace-pre-wrap">
              {JSON.stringify(diagnosticsResults, null, 2)}
            </pre>
          </div>
        )}
      </div>

      <form onSubmit={handleSave} className="space-y-8">
        {/* 1. LLM & Script Generation */}
        <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-6">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <Cpu className="w-5 h-5 text-purple-400" />
              <h2 className="text-lg font-bold text-white">AI Language Model (Story & Script Generation)</h2>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Provider:</span>
              <select
                value={settings.llm_provider || 'auto'}
                onChange={(e) => setSettings({ ...settings, llm_provider: e.target.value })}
                className="bg-dark-900 border border-purple-500/40 rounded-xl px-3 py-1.5 text-xs text-white font-semibold focus:outline-none focus:border-purple-400"
              >
                <option value="auto">Auto (Best Available)</option>
                <option value="gemini">Google Gemini (Cloud AI)</option>
                <option value="ollama">Ollama (Local AI)</option>
                <option value="smart_cartoon">Shorts Comedy Engine (Fallback)</option>
              </select>
            </div>
          </div>

          {/* Google Gemini Card */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-blue-950/30 via-dark-900 to-purple-950/20 border border-blue-500/30 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-bold text-white">Google Gemini Provider</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  Recommended
                </span>
              </div>
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noreferrer"
                className="text-xs text-blue-400 hover:text-blue-300 hover:underline flex items-center gap-1"
              >
                <span>Get Free Gemini Key</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <Key className="w-3.5 h-3.5 text-slate-400" />
                  <span>Gemini API Key</span>
                </label>
                <div className="relative flex gap-2">
                  <div className="relative flex-1">
                    <input
                      type={showApiKey ? 'text' : 'password'}
                      value={settings.gemini_api_key || ''}
                      onChange={(e) => setSettings({ ...settings, gemini_api_key: e.target.value })}
                      className="w-full bg-dark-900 border border-slate-700 rounded-xl p-2.5 pr-10 text-xs text-white focus:outline-none focus:border-blue-500"
                      placeholder="AIzaSy..."
                    />
                    <button
                      type="button"
                      onClick={() => setShowApiKey(!showApiKey)}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                    >
                      {showApiKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                  <button
                    type="button"
                    onClick={handleTestGemini}
                    disabled={testingGemini}
                    className="px-3 py-2 rounded-xl bg-blue-600/20 border border-blue-500/40 text-xs font-semibold text-blue-300 hover:bg-blue-600/30 hover:text-white transition shrink-0 flex items-center gap-1.5"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${testingGemini ? 'animate-spin' : ''}`} />
                    <span>Test Key</span>
                  </button>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Gemini Model</label>
                <select
                  value={settings.gemini_model || 'gemini-2.0-flash'}
                  onChange={(e) => setSettings({ ...settings, gemini_model: e.target.value })}
                  className="w-full bg-dark-900 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="gemini-3.5-flash">gemini-3.5-flash (Ultra Fast & Smart - Recommended)</option>
                  <option value="gemini-3.1-flash-lite">gemini-3.1-flash-lite (Ultra Low Latency)</option>
                  <option value="gemini-3-flash-preview">gemini-3-flash-preview (Next-Gen Preview)</option>
                  <option value="gemini-2.0-flash">gemini-2.0-flash (Fast & Smart)</option>
                  <option value="gemini-1.5-flash">gemini-1.5-flash (Legacy Reliable)</option>
                </select>
              </div>
            </div>

            {/* Gemini Test Status */}
            {geminiStatus && (
              <div
                className={`p-3 rounded-xl border text-xs flex items-center gap-2 ${
                  geminiStatus.connected
                    ? 'bg-emerald-950/40 border-emerald-600/40 text-emerald-300'
                    : 'bg-rose-950/40 border-rose-600/40 text-rose-300'
                }`}
              >
                {geminiStatus.connected ? <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" /> : <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />}
                <span>
                  {geminiStatus.connected
                    ? `Connected successfully to Google Gemini! Model: ${geminiStatus.displayName || geminiStatus.model}`
                    : `Connection error: ${geminiStatus.error}`}
                </span>
              </div>
            )}
          </div>

          {/* Ollama Local AI Card */}
          <div className="p-5 rounded-2xl bg-dark-900/60 border border-slate-800 space-y-4">
            <div className="flex items-center gap-2">
              <Server className="w-4 h-4 text-purple-400" />
              <span className="text-sm font-bold text-white">Local Ollama Provider (Optional)</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Ollama Endpoint URL</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={settings.ollama_base_url}
                    onChange={(e) => setSettings({ ...settings, ollama_base_url: e.target.value })}
                    className="flex-1 bg-dark-950 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-purple-500"
                    placeholder="http://localhost:11434"
                  />
                  <button
                    type="button"
                    onClick={handleTestOllama}
                    disabled={testingOllama}
                    className="px-3 py-2 rounded-xl bg-dark-950 border border-slate-700 text-xs font-semibold text-purple-400 hover:text-white hover:border-purple-500 transition shrink-0 flex items-center gap-1.5"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${testingOllama ? 'animate-spin' : ''}`} />
                    <span>Test</span>
                  </button>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300">Ollama Model</label>
                <input
                  type="text"
                  value={settings.ollama_model}
                  onChange={(e) => setSettings({ ...settings, ollama_model: e.target.value })}
                  className="w-full bg-dark-950 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-purple-500"
                  placeholder="llama3.2 / mistral / qwen2.5"
                />
              </div>
            </div>

            {/* Ollama Test Status Banner */}
            {ollamaStatus && (
              <div
                className={`p-3 rounded-xl border text-xs flex items-center gap-2 ${
                  ollamaStatus.connected
                    ? 'bg-emerald-950/40 border-emerald-600/40 text-emerald-300'
                    : 'bg-amber-950/40 border-amber-600/40 text-amber-300'
                }`}
              >
                {ollamaStatus.connected ? <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" /> : <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />}
                <span>
                  {ollamaStatus.connected
                    ? `Connected to Ollama! Available models: ${(ollamaStatus.models || []).join(', ')}`
                    : `Ollama unavailable at ${settings.ollama_base_url}. (Auto-fallback to Gemini or Smart Cartoon Story Engine)`}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* 2. Visual & Voice Providers */}
        <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-6">
          <div className="flex items-center gap-2.5 pb-2 border-b border-slate-800">
            <ImageIcon className="w-5 h-5 text-pink-400" />
            <h2 className="text-lg font-bold text-white">Visual & Voice Engines</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Visual Artwork Engine</label>
              <select
                value={settings.image_provider}
                onChange={(e) => setSettings({ ...settings, image_provider: e.target.value })}
                className="w-full bg-dark-900 border border-slate-700 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-purple-500"
              >
                <option value="toon_vector">Modern 2D Cartoon Vector (Built-in Free Engine)</option>
                <option value="comfyui">ComfyUI Local AI Diffusion</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Voice Synthesis Engine</label>
              <select
                value={settings.voice_provider}
                onChange={(e) => setSettings({ ...settings, voice_provider: e.target.value })}
                className="w-full bg-dark-900 border border-slate-700 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-purple-500"
              >
                <option value="edge_tts">Neural Multi-Speaker (Free, High Quality)</option>
                <option value="piper">Local Piper TTS</option>
                <option value="kokoro">Kokoro TTS</option>
                <option value="fallback_synth">Offline Harmonic Vocal Synth</option>
              </select>
            </div>
          </div>
        </div>

        {/* 3. Output Resolution & FFmpeg */}
        <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-6">
          <div className="flex items-center gap-2.5 pb-2 border-b border-slate-800">
            <SettingsIcon className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-bold text-white">Video Rendering (FFmpeg)</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Resolution</label>
              <input
                type="text"
                disabled
                value={`${settings.width} x ${settings.height} (9:16 Shorts)`}
                className="w-full bg-dark-950/60 border border-slate-800 rounded-xl p-3 text-xs text-slate-400 cursor-not-allowed"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Frame Rate (FPS)</label>
              <select
                value={settings.fps}
                onChange={(e) => setSettings({ ...settings, fps: parseInt(e.target.value) })}
                className="w-full bg-dark-900 border border-slate-700 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-purple-500"
              >
                <option value={30}>30 FPS (Standard YouTube Shorts)</option>
                <option value={60}>60 FPS (Ultra Smooth)</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Default Target Duration</label>
              <select
                value={settings.default_duration}
                onChange={(e) => setSettings({ ...settings, default_duration: parseInt(e.target.value) })}
                className="w-full bg-dark-900 border border-slate-700 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-purple-500"
              >
                <option value={30}>30 Seconds</option>
                <option value={45}>45 Seconds</option>
                <option value={60}>60 Seconds</option>
              </select>
            </div>
          </div>
        </div>

        {/* 6. Instagram Automation Integration */}
        <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-800 space-y-6">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded-lg bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
                IG
              </div>
              <h2 className="text-lg font-bold text-white">Instagram Automation & Reels Publishing</h2>
            </div>
            <span className={`px-2.5 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 ${
              instaStatus?.authenticated
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
            }`}>
              {instaStatus?.authenticated ? (
                <>
                  <Check className="w-3.5 h-3.5" />
                  <span>Connected (@{instaStatus.profile?.username})</span>
                </>
              ) : (
                <>
                  <X className="w-3.5 h-3.5" />
                  <span>Not Logged In</span>
                </>
              )}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            <div className="space-y-3">
              <p className="text-xs text-slate-300 leading-relaxed">
                Connect your Instagram account once to enable 100% autonomous Reels publishing, analytics tracking, and automated captioning without touching any manual UI buttons.
              </p>
              {instaStatus?.authenticated ? (
                <div className="p-3.5 rounded-2xl bg-dark-900 border border-slate-800 flex items-center gap-3">
                  {instaStatus.profile?.profile_pic_url ? (
                    <img
                      src={instaStatus.profile.profile_pic_url}
                      alt="Avatar"
                      className="w-10 h-10 rounded-full object-cover border border-pink-500/40"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-pink-500/20 flex items-center justify-center text-pink-400 font-bold text-sm">
                      @{instaStatus.profile?.username?.[0]?.toUpperCase()}
                    </div>
                  )}
                  <div>
                    <h4 className="text-xs font-bold text-white">@{instaStatus.profile?.username}</h4>
                    <p className="text-[11px] text-slate-400">
                      {instaStatus.profile?.follower_count?.toLocaleString() || 0} followers • {instaStatus.profile?.media_count || 0} posts
                    </p>
                  </div>
                </div>
              ) : (
                <div className="p-3.5 rounded-2xl bg-dark-900 border border-slate-800 text-xs text-slate-400 space-y-1">
                  <div className="font-semibold text-slate-300">Terminal Command:</div>
                  <code className="text-pink-400 font-mono text-[11px] block bg-black/40 p-2 rounded-lg">
                    python scripts/instagram_manager.py login
                  </code>
                </div>
              )}
            </div>

            <div className="space-y-3 text-right flex flex-col items-end">
              <button
                type="button"
                onClick={startLoginCapture}
                disabled={launchingLogin}
                className="px-5 py-3 rounded-2xl bg-gradient-to-r from-pink-600 via-rose-500 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white text-xs font-bold shadow-lg shadow-pink-600/25 transition-all flex items-center gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                <span>{instaStatus?.authenticated ? 'Reconnect / Switch Account' : 'Connect Instagram (Browser Session Capture)'}</span>
              </button>
              <span className="text-[10px] text-slate-500">
                Safe & zero-risk login with full 2FA and OTP support
              </span>
            </div>
          </div>
        </div>

        {/* Save Bar */}
        <div className="flex items-center justify-between pt-4">
          <div>
            {saveSuccess && (
              <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                <CheckCircle className="w-4 h-4" />
                <span>Settings saved successfully!</span>
              </span>
            )}
          </div>
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-3 rounded-2xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white text-sm font-bold shadow-lg shadow-purple-600/30 transition-all flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save Settings'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
