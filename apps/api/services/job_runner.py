import asyncio
import uuid
import datetime
from typing import Dict, Any, Set
from fastapi import WebSocket
from apps.api.database import AsyncSessionLocal
from apps.api.models.schema import Project, GenerationJob
from apps.api.services.pipeline import GenerationPipeline

# Active WebSocket connections per project
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, project_id: str, websocket: WebSocket):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        self.active_connections[project_id].add(websocket)

    def disconnect(self, project_id: str, websocket: WebSocket):
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]

    async def broadcast_progress(self, data: Dict[str, Any]):
        project_id = data.get("project_id")
        if project_id and project_id in self.active_connections:
            dead_sockets = set()
            for ws in self.active_connections[project_id]:
                try:
                    await ws.send_json(data)
                except Exception:
                    dead_sockets.add(ws)
            for ws in dead_sockets:
                self.active_connections[project_id].discard(ws)

manager = ConnectionManager()
pipeline_instance = GenerationPipeline()

# Background task runner
async def start_generation_job(project_id: str):
    job_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        job = GenerationJob(
            id=job_id,
            project_id=project_id,
            status="Running",
            progress_percent=0,
            current_stage="Initializing",
            stage_message="Starting generation engine...",
            started_at=datetime.datetime.utcnow()
        )
        session.add(job)
        
        proj = await session.get(Project, project_id)
        if proj:
            proj.status = "Generating"
        await session.commit()

    # Launch pipeline asynchronously in background
    asyncio.create_task(
        _run_pipeline_task(project_id)
    )
    return job_id

async def _run_pipeline_task(project_id: str):
    try:
        await pipeline_instance.execute_project_pipeline(
            project_id=project_id,
            db_session_factory=AsyncSessionLocal,
            progress_callback=manager.broadcast_progress
        )
    except Exception as e:
        print(f"[JobRunner] Task failed for {project_id}: {e}")
        await manager.broadcast_progress({
            "project_id": project_id,
            "stage": "Failed",
            "progress": 0,
            "error": str(e)
        })
