import os
import uuid
import json
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel

from apps.api.database import get_db, AsyncSessionLocal
from apps.api.models.schema import Project, Character, Scene, GenerationJob
from apps.api.services.job_runner import start_generation_job
from apps.api.config import PROJECTS_DIR

router = APIRouter(prefix="/api/projects", tags=["projects"])

class ProjectCreateRequest(BaseModel):
    topic: str
    title: Optional[str] = None
    language: Optional[str] = "English"
    art_style: Optional[str] = "Modern 2D Cartoon"
    duration_seconds: Optional[int] = 45
    auto_generate: Optional[bool] = True

class ProjectResponse(BaseModel):
    id: str
    title: str
    topic: str
    status: str
    duration_seconds: float
    art_style: str
    language: str
    thumbnail_url: Optional[str]
    video_url: Optional[str]
    created_at: str

@router.get("")
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).order_by(desc(Project.created_at)))
    projects = result.scalars().all()
    
    out = []
    for p in projects:
        out.append({
            "id": p.id,
            "title": p.title,
            "topic": p.topic,
            "status": p.status,
            "duration_seconds": p.duration_seconds or 0.0,
            "art_style": p.art_style,
            "language": p.language,
            "thumbnail_url": p.thumbnail_url,
            "video_url": p.video_url,
            "created_at": p.created_at.isoformat() if p.created_at else ""
        })
    return out

@router.post("")
async def create_project(req: ProjectCreateRequest, db: AsyncSession = Depends(get_db)):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
        
    project_id = str(uuid.uuid4())
    title = req.title.strip() if (req.title and req.title.strip()) else req.topic[:50]
    
    project = Project(
        id=project_id,
        title=title,
        topic=req.topic,
        status="Queued",
        duration_seconds=req.duration_seconds,
        art_style=req.art_style or "Modern 2D Cartoon",
        language=req.language or "English"
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    if req.auto_generate:
        await start_generation_job(project_id)
        
    return {
        "id": project.id,
        "title": project.title,
        "topic": project.topic,
        "status": project.status
    }

@router.get("/{project_id}")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Get characters and scenes
    char_res = await db.execute(select(Character).where(Character.project_id == project_id))
    characters = char_res.scalars().all()
    
    scene_res = await db.execute(select(Scene).where(Scene.project_id == project_id).order_by(Scene.scene_number))
    scenes = scene_res.scalars().all()
    
    job_res = await db.execute(select(GenerationJob).where(GenerationJob.project_id == project_id).order_by(desc(GenerationJob.started_at)))
    job = job_res.scalars().first()
    
    story_data = json.loads(project.story_json) if project.story_json else None
    metadata = json.loads(project.metadata_json) if project.metadata_json else None
    
    return {
        "id": project.id,
        "title": project.title,
        "topic": project.topic,
        "status": project.status,
        "duration_seconds": project.duration_seconds,
        "art_style": project.art_style,
        "language": project.language,
        "width": project.width,
        "height": project.height,
        "thumbnail_url": project.thumbnail_url,
        "video_url": project.video_url,
        "audio_mix_url": project.audio_mix_url,
        "subtitles_url": project.subtitles_url,
        "error_message": project.error_message,
        "story": story_data,
        "metadata": metadata,
        "characters": [
            {
                "id": c.id,
                "name": c.name,
                "role": c.role,
                "age": c.age,
                "gender": c.gender,
                "body_type": c.body_type,
                "hair_style": c.hair_style,
                "hair_color": c.hair_color,
                "skin_tone": c.skin_tone,
                "outfit_desc": c.outfit_desc,
                "outfit_color": c.outfit_color,
                "personality": c.personality,
                "voice_name": c.voice_name,
                "avatar_url": c.avatar_url,
                "mouth_open_url": c.mouth_open_url,
                "mouth_closed_url": c.mouth_closed_url,
                "expression_shock_url": c.expression_shock_url,
                "expression_happy_url": c.expression_happy_url,
            } for c in characters
        ],
        "scenes": [
            {
                "id": s.id,
                "scene_number": s.scene_number,
                "duration": s.duration,
                "location": s.location,
                "action_desc": s.action_desc,
                "dialogue_text": s.dialogue_text,
                "speaker_name": s.speaker_name,
                "camera_motion": s.camera_motion,
                "transition": s.transition,
                "emotion": s.emotion,
                "sfx": json.loads(s.sfx_json or "[]"),
                "background_url": s.background_url,
                "scene_image_url": s.scene_image_url,
                "audio_url": s.audio_url
            } for s in scenes
        ],
        "job": {
            "id": job.id if job else None,
            "status": job.status if job else project.status,
            "progress_percent": job.progress_percent if job else (100 if project.status == "Completed" else 0),
            "current_stage": job.current_stage if job else "",
            "stage_message": job.stage_message if job else "",
            "logs": json.loads(job.log_messages_json or "[]") if job else []
        } if job else None,
        "created_at": project.created_at.isoformat() if project.created_at else ""
    }

@router.get("/{project_id}/status")
async def get_project_status(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    job_res = await db.execute(select(GenerationJob).where(GenerationJob.project_id == project_id).order_by(desc(GenerationJob.started_at)))
    job = job_res.scalars().first()
    
    return {
        "id": project.id,
        "status": project.status,
        "progress": job.progress_percent if job else (100 if project.status == "Completed" else 0),
        "stage": job.current_stage if job else "",
        "message": job.stage_message if job else "",
        "video_url": project.video_url,
        "thumbnail_url": project.thumbnail_url,
        "error": project.error_message or (job.error_message if job else None)
    }

@router.post("/{project_id}/generate")
async def trigger_generate(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    job_id = await start_generation_job(project_id)
    return {"message": "Generation started", "job_id": job_id}

@router.delete("/{project_id}")
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Delete folder from disk
    p_dir = PROJECTS_DIR / project_id
    if p_dir.exists():
        shutil.rmtree(p_dir, ignore_errors=True)
        
    await db.delete(project)
    await db.commit()
    return {"message": "Project deleted successfully"}
