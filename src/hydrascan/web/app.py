"""FastAPI backend exposing the scan engine over HTTP."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ..depsdev import ResolutionError
from ..lockfile import LockfileError
from .badge import badge_for_scan, render_badge
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


@app.get("/api/badge")
def badge(repo: str) -> Response:
    """Live SVG status badge for a repo, embeddable in a README."""
    url = repo if "github.com" in repo else f"https://github.com/{repo}"
    try:
        message, color = badge_for_scan(run_scan(repo_url=url))
    except Exception:
        message, color = "unknown", "#9f9f9f"
    return Response(
        render_badge(message, color),
        media_type="image/svg+xml",
        headers={"Cache-Control": "max-age=1800"},
    )


app.include_router(bot_router)

_static = os.environ.get("HYDRASCAN_STATIC_DIR")
if _static and Path(_static).is_dir():
    app.mount("/", StaticFiles(directory=_static, html=True), name="static")
