import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

load_dotenv()

from scanner import scan_repo
from summarizer import summarize_findings

app = FastAPI(title="VibeCheck API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
LANDING_DIR = Path(__file__).parent.parent / "landing"


class ScanRequest(BaseModel):
    github_url: str


@app.post("/api/scan")
async def scan(req: ScanRequest):
    url = req.github_url.strip().rstrip("/")

    if not url:
        raise HTTPException(status_code=400, detail="Please provide a GitHub URL.")

    if not url.startswith("http"):
        url = "https://" + url

    if "github.com" not in url:
        raise HTTPException(
            status_code=400, detail="Please provide a valid GitHub repository URL."
        )

    if url.endswith(".git"):
        url = url[:-4]

    try:
        scan_data = await asyncio.to_thread(scan_repo, url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan error: {str(e)}")

    findings = scan_data.get("findings", [])

    if not findings:
        return JSONResponse(
            {
                "clean": True,
                "score": 100,
                "label": "Safe to Ship 🚀",
                "color": "#3fb950",
                "findings": [],
                "message": "No obvious leaks, open database policies, or dangerous endpoints found. Good to ship!",
            }
        )

    enriched_findings = await summarize_findings(findings)

    return JSONResponse(
        {
            "clean": False,
            "score": scan_data["score"],
            "label": scan_data["label"],
            "color": scan_data["color"],
            "findings": enriched_findings,
            "message": f"Found {len(enriched_findings)} vulnerability risk(s) in your vibe-coded project.",
        }
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "gemini_configured": bool(os.environ.get("GEMINI_API_KEY")),
    }


if LANDING_DIR.exists():
    @app.get("/")
    async def root():
        return FileResponse(LANDING_DIR / "index.html")

if FRONTEND_DIR.exists():
    @app.get("/scan")
    async def scan_ui():
        return FileResponse(FRONTEND_DIR / "index.html")
