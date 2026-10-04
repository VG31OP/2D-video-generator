export interface Character {
  id: string;
  name: string;
  role: string;
  age: string;
  gender: string;
  body_type: string;
  hair_style: string;
  hair_color: string;
  skin_tone: string;
  outfit_desc: string;
  outfit_color: string;
  personality: string;
  voice_name: string;
  avatar_url?: string;
  mouth_open_url?: string;
  mouth_closed_url?: string;
  expression_shock_url?: string;
  expression_happy_url?: string;
}

export interface Scene {
  id: string;
  scene_number: number;
  duration: number;
  location: string;
  action_desc: string;
  dialogue_text: string;
  speaker_name: string;
  camera_motion: string;
  transition: string;
  emotion: string;
  sfx: string[];
  background_url?: string;
  scene_image_url?: string;
  audio_url?: string;
}

export interface ProjectMetadata {
  youtube_title?: string;
  description?: string;
  hashtags?: string[];
  tags?: string[];
  providers?: Record<string, string>;
  qc?: any;
}

export interface Project {
  id: string;
  title: string;
  topic: string;
  status: 'Queued' | 'Planning' | 'Generating' | 'Rendering' | 'Completed' | 'Failed';
  duration_seconds: number;
  art_style: string;
  language: string;
  width?: number;
  height?: number;
  thumbnail_url?: string;
  video_url?: string;
  audio_mix_url?: string;
  subtitles_url?: string;
  error_message?: string;
  story?: any;
  metadata?: ProjectMetadata;
  characters?: Character[];
  scenes?: Scene[];
  job?: {
    id: string;
    status: string;
    progress_percent: number;
    current_stage: string;
    stage_message: string;
    logs: string[];
  };
  created_at: string;
}

export interface Settings {
  ollama_base_url: string;
  ollama_model: string;
  image_provider: string;
  voice_provider: string;
  animation_provider: string;
  default_style: string;
  default_language: string;
  default_duration: number;
  width: number;
  height: number;
  fps: number;
}

export interface SystemCapabilities {
  system?: {
    python_version: string;
    python_ok: boolean;
    os: string;
  };
  hardware: {
    gpu_available: boolean;
    gpu_name: string;
    cuda_available: boolean;
    device_count: number;
    vram_total_gb: number;
  };
  llm: {
    ollama_available: boolean;
    ollama_url: string;
    configured_model?: string;
    ollama_model?: string;
    model_ready?: boolean;
    available_models: string[];
    smart_engine_available: boolean;
    active_provider_type?: string;
  };
  visual: {
    comfyui_available: boolean;
    comfyui_url: string;
    available_checkpoints?: string[];
    active_checkpoint?: string | null;
    toon_vector_available: boolean;
    active_provider_type?: string;
  };
  voice: {
    edge_tts_available: boolean;
    kokoro_available: boolean;
    piper_available: boolean;
    fallback_synth_available: boolean;
    active_provider_type?: string;
  };
  speech?: {
    whisper_available: boolean;
    whisper_flavor?: string | null;
  };
  lip_sync?: {
    real_lipsync_available: boolean;
    mouth_flap_available: boolean;
    active_provider_type?: string;
  };
  animation?: {
    ai_animation_available: boolean;
    motion_comic_available: boolean;
    active_provider_type?: string;
  };
  rendering: {
    ffmpeg_available: boolean;
    ffmpeg_version: string;
    ffprobe_available: boolean;
    libass_supported: boolean;
  };
}
