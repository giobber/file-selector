import sys
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from app.models import File, format_size

from .settings import Settings, get_settings, log_settings

# Setup logger
logger.remove()
logger.add(sys.stderr, level=get_settings().LOG_LEVEL)
log_settings()

# Initialize FastAPI app
app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["formatsize"] = format_size(get_settings().BYTE_SIZE)


@app.get("/")
async def base(request: Request):
    return RedirectResponse(url="/home")


@app.get("/home")
@app.get("/home/{sub_path:path}", response_class=HTMLResponse)
async def home(request: Request, sub_path: Path = Path("")):
    context = {"request": request, "sub_path": sub_path}
    return templates.TemplateResponse("index.html", context)


@app.get("/root/{sub_path:path}", response_class=HTMLResponse)
async def path_contents(
    sub_path: Path, request: Request, settings: Settings = Depends(get_settings)
):
    path = settings.BASE_PATH / sub_path
    logger.debug(f"Request path: {sub_path} (BASE_PATH={settings.BASE_PATH}")

    contents = (File.from_path(p) for p in path.glob("*"))
    contents = sorted(contents, key=lambda f: f.name)
    context = {
        "request": request,
        "path": path,
        "sub_path": sub_path,
        "base_path": settings.BASE_PATH,
        "contents": contents,
        # Return the sub-path only if there is a sub-path
        "back_path": (
            path.parent.relative_to(settings.BASE_PATH)
            if path > settings.BASE_PATH
            else None
        ),
    }
    return templates.TemplateResponse("table.html", context)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
