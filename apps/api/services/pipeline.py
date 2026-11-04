"""
FastAPI Generation Pipeline Service
Bridges API Project requests to the core 3D Zack D. explainer engine.
"""

import os
import json
import uuid
import asyncio
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.api.config import settings, PROJECTS_DIR
from apps.api.models.schema import Project, Scene, GenerationJob
from core.pipeline import pipeline as core_pipeline


class GenerationPipeline:
    def __init__(self, **kwargs):
        pass

    async def execute_project_pipeline(
        self,
        project_id: str,
        db_session_factory,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        resume_stage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the 3D Zack D. explainer pipeline for a given project in the database.
        """
        async with db_session_factory() as session:
            project = await session.get(Project, project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            topic = project.topic or project.title or "Science Explainer"

        if progress_callback:
            await progress_callback({
                "project_id": project_id,
                "stage": "Script & Voice",
                "progress": 20,
                "message": "Generating viral 8-sentence script & neural voice..."
            })

        # Run core 3D pipeline in thread pool to prevent blocking async event loop
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(
            None,
            lambda: core_pipeline.run(topic=topic, publish=False, draft=False)
        )

        video_path = res["video_path"]
        cover_path = res["cover_path"]
        duration = res["duration"]

        if progress_callback:
            await progress_callback({
                "project_id": project_id,
                "stage": "Completed",
                "progress": 100,
                "message": "3D Explainer video ready!"
            })

        # Update Project record in DB
        async with db_session_factory() as session:
            proj = await session.get(Project, project_id)
            if proj:
                proj.status = "Completed"
                proj.duration_seconds = duration
                # Web relative URLs
                try:
                    rel_video = Path(video_path).resolve().relative_to(settings.ROOT_DIR)
                    proj.video_url = f"/{rel_video.as_posix()}"
                except Exception:
                    proj.video_url = video_path

                try:
                    rel_cover = Path(cover_path).resolve().relative_to(settings.ROOT_DIR)
                    proj.thumbnail_url = f"/{rel_cover.as_posix()}"
                except Exception:
                    proj.thumbnail_url = cover_path

            # Update GenerationJob
            job_res = await session.execute(
                select(GenerationJob).where(GenerationJob.project_id == project_id)
            )
            job = job_res.scalars().first()
            if job:
                job.status = "Completed"
                job.progress_percent = 100
                job.current_stage = "Completed"
                job.stage_message = "Master 1080x1920 MP4 rendered successfully."
                job.completed_at = datetime.datetime.utcnow()

            await session.commit()

        return res
