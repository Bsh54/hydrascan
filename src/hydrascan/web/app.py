"""FastAPI backend exposing the scan engine over HTTP."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ..depsdev import ResolutionError
from ..lockfile import LockfileError
from .bot import router as bot_router
from .github import RepositoryError
from .pipeline import ScanInputError, run_scan

app = FastAPI(title="HydraScan API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    repo_url: str | None = Field(default=None, alias="repoUrl")
    lockfile: dict | None = None
    requirements: str | None = None

    model_config = {"populate_by_name": True}


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/scan")
def scan(request: ScanRequest) -> dict:
    try:
        return run_scan(
            repo_url=request.repo_url,
            lockfile=request.lockfile,
            requirements=request.requirements,
        )
    except ScanInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (LockfileError, ResolutionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


app.include_router(bot_router)

_static = os.environ.get("HYDRASCAN_STATIC_DIR")
if _static and Path(_static).is_dir():
    app.mount("/", StaticFiles(directory=_static, html=True), name="static")
