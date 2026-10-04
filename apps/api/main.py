import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from apps.api.config import settings, STORAGE_DIR
from apps.api.database import init_db
from apps.api.routes import projects, settings as settings_route
from apps.api.services.job_runner import manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    await init_db()
    yield

app = FastAPI(
    title="ToonForge API",
    description="Autonomous AI Cartoon YouTube Shorts Generator",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Storage
app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")

# Include Routers
app.include_router(projects.router)
app.include_router(settings_route.router)

@app.websocket("/ws/projects/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await manager.connect(project_id, websocket)
    try:
        while True:
            # Keep socket alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(project_id, websocket)

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "ToonForge API"}

# Mount built frontend if available
web_dist = Path(__file__).resolve().parent.parent / "web" / "dist"
if web_dist.exists():
    from fastapi.responses import FileResponse
    
    # Mount assets subfolder
    assets_dir = web_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Ignore API and storage paths
        if full_path.startswith("api") or full_path.startswith("storage") or full_path.startswith("ws"):
            return None
        target_file = web_dist / full_path
        if target_file.is_file():
            return FileResponse(str(target_file))
        return FileResponse(str(web_dist / "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
