import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from apps.api.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    topic = Column(Text, nullable=False)
    status = Column(String(50), default="Queued") # Queued, Planning, Generating, Rendering, Completed, Failed
    duration_seconds = Column(Float, default=0.0)
    width = Column(Integer, default=1080)
    height = Column(Integer, default=1920)
    fps = Column(Integer, default=30)
    language = Column(String(50), default="English")
    art_style = Column(String(100), default="Modern 2D Cartoon")
    
    # AI Generation Data
    story_json = Column(Text, nullable=True) # Full structured story
    script_text = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True) # YouTube Title, Description, Tags, Hashtags
    
    # Asset URLs / relative paths
    thumbnail_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    audio_mix_url = Column(String(500), nullable=True)
    subtitles_url = Column(String(500), nullable=True)
    
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan", order_by="Scene.scene_number")
    jobs = relationship("GenerationJob", back_populates="project", cascade="all, delete-orphan", order_by="desc(GenerationJob.started_at)")


class Character(Base):
    __tablename__ = "characters"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(50), default="Protagonist") # Protagonist, Sidekick, Antagonist, Narrator
    age = Column(String(50), default="Young Adult")
    gender = Column(String(50), default="Neutral")
    body_type = Column(String(100), default="Slim cartoon build")
    hair_style = Column(String(100), default="Messy modern")
    hair_color = Column(String(50), default="#2d3748")
    skin_tone = Column(String(50), default="#f6d5b8")
    outfit_desc = Column(String(255), default="Casual hoodie and pants")
    outfit_color = Column(String(50), default="#3b82f6")
    personality = Column(Text, default="Witty, expressive, dynamic")
    visual_traits = Column(Text, default="Large expressive eyes, animated mouth")
    
    # Voice Config
    voice_id = Column(String(100), default="en-US-GuyNeural")
    voice_name = Column(String(100), default="Guy (Energetic)")
    voice_pitch = Column(String(20), default="+0Hz")
    voice_rate = Column(String(20), default="+5%")
    
    # Asset paths
    avatar_url = Column(String(500), nullable=True)
    mouth_open_url = Column(String(500), nullable=True)
    mouth_closed_url = Column(String(500), nullable=True)
    expression_shock_url = Column(String(500), nullable=True)
    expression_happy_url = Column(String(500), nullable=True)
    
    project = relationship("Project", back_populates="characters")


class Scene(Base):
    __tablename__ = "scenes"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    duration = Column(Float, default=4.0) # In seconds
    location = Column(String(200), default="Classroom")
    visual_prompt = Column(Text, default="")
    action_desc = Column(Text, default="")
    dialogue_text = Column(Text, default="")
    speaker_name = Column(String(100), default="Narrator")
    camera_motion = Column(String(100), default="slow zoom in") # slow zoom in, pan right, pan left, whip pan, dramatic push, static
    transition = Column(String(50), default="cut") # cut, whip_left, zoom_in, fade
    sfx_json = Column(Text, default="[]") # List of SFX like ["whoosh", "vine_boom", "bell"]
    emotion = Column(String(50), default="comedy")
    
    # Rendered Asset Paths
    background_url = Column(String(500), nullable=True)
    scene_image_url = Column(String(500), nullable=True)
    audio_url = Column(String(500), nullable=True)
    video_clip_url = Column(String(500), nullable=True)
    subtitles_json = Column(Text, nullable=True)
    
    project = relationship("Project", back_populates="scenes")


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="Queued") # Queued, Running, Completed, Failed, Cancelled
    progress_percent = Column(Integer, default=0)
    current_stage = Column(String(100), default="Initializing")
    stage_message = Column(String(255), default="Preparing short generation pipeline...")
    log_messages_json = Column(Text, default="[]")
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="jobs")


class SettingModel(Base):
    __tablename__ = "settings"

    key = Column(String(100), primary_key=True, index=True)
    value = Column(Text, nullable=False)
    category = Column(String(50), default="general")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
