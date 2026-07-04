import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app.core.logging import setup_logging, LOGGING_CONFIG
from src.app.api.endpoints import docx, pdf, csv, excel
from src.app.core.config import get_settings
from src.app.services.summerizer import Summarizer

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):

    setup_logging()
    logger = logging.getLogger(__name__)
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("Starting up File Comparison APPLICATION...")

    # Ensure output directory exists
    settings.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Outputs directory ready: %s", settings.OUTPUTS_DIR)

    # Eagerly validate the Gemini API key and warm up the client
    # so a missing key fails loud at boot, not silently on the first request
    try:
        Summarizer._get_client()
        logger.info("Gemini client initialised successfully.")
    except RuntimeError as e:
        logger.warning("Gemini client could not be initialised: %s", e)

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Shutting down File Comparison API.")


app = FastAPI(
    title="File Comparison API",
    description=(
        "Compare DOCX, PDF, CSV, and Excel files. "
        "Get similarity scores, line diffs, and AI-generated summaries via Gemini."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="src/app/static"), name="static")
templates = Jinja2Templates(directory="src/app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(docx.router,  prefix="/api/v1")
app.include_router(pdf.router,   prefix="/api/v1")
app.include_router(csv.router,   prefix="/api/v1")
app.include_router(excel.router, prefix="/api/v1")


@app.get("", tags=["Health"])
def root():
    return {"status": "ok", "docs": "/docs"}

@app.get("/")
def render_homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        reload_excludes=[
                        "logs/*",
                        "outputs/*",
                        ".venv/*",
                        "__pycache__/*",
                    ],
        log_config=LOGGING_CONFIG
    )