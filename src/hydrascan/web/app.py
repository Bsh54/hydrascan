"""FastAPI backend exposing the scan engine over HTTP."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ..depsdev import ResolutionError, resolve_from_package_json
from ..lockfile import LockfileError, parse_lockfile_data
from ..maintainers import analyze_ownership
from ..models import DependencyGraph
from ..pypi import resolve_from_requirements
from ..service import scan_graph
from ..typosquat import detect_typosquats
from .github import (
    RepositoryError,
    fetch_lockfile,
    fetch_manifest,
    fetch_requirements,
)
from .serialize import serialize_scan

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
    graph, source, ecosystem = _build_graph(request)
    result = scan_graph(graph, ecosystem=ecosystem)

    payload = serialize_scan(result, ecosystem)
    payload["source"] = source
    payload["ecosystem"] = ecosystem
    payload["engine"] = result.engine

    compromised_coords = [
        result.graph.packages[node_id].coordinate for node_id in result.report.compromised
    ]
    if ecosystem == "npm":
        names = [pkg.name for pkg in result.graph.packages.values()]
        payload["typosquats"] = detect_typosquats(names)
        ownership = analyze_ownership(compromised_coords)
        payload["sharedMaintainers"] = ownership["maintainers"]
        payload["sharedInfrastructure"] = ownership["infrastructure"]
    else:
        payload["typosquats"] = []
        payload["sharedMaintainers"] = []
        payload["sharedInfrastructure"] = []
    return payload


def _build_graph(request: ScanRequest) -> tuple[DependencyGraph, str, str]:
    """Build the graph from a lockfile, package.json, or requirements.txt."""
    if request.lockfile is not None:
        return _parse(request.lockfile), "lockfile", "npm"
    if request.requirements is not None:
        try:
            return resolve_from_requirements(request.requirements), "deps.dev", "PyPI"
        except ResolutionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not request.repo_url:
        raise HTTPException(status_code=400, detail="provide repoUrl, lockfile, or requirements")

    try:
        lockfile = fetch_lockfile(request.repo_url)
        if lockfile is not None:
            return _parse(lockfile), "lockfile", "npm"

        requirements = fetch_requirements(request.repo_url)
        if requirements is not None:
            return resolve_from_requirements(requirements), "deps.dev", "PyPI"

        manifest = fetch_manifest(request.repo_url)
        return resolve_from_package_json(manifest), "deps.dev", "npm"
    except RepositoryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ResolutionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _parse(lockfile: dict) -> DependencyGraph:
    try:
        return parse_lockfile_data(lockfile)
    except LockfileError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


_static = os.environ.get("HYDRASCAN_STATIC_DIR")
if _static and Path(_static).is_dir():
    app.mount("/", StaticFiles(directory=_static, html=True), name="static")
