import sys

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, settings: Settings = Depends(get_settings)):
    context = {"request": request, "debug": settings.DEBUG}
    return templates.TemplateResponse("index.html", context)


@app.get("/root", response_class=HTMLResponse)
@app.post("/root", response_class=HTMLResponse)
async def path_contents(request: Request, settings: Settings = Depends(get_settings)):
    path = settings.BASE_PATH
    # NOTE: path_data is only the sub-path relative_to BASE_PATH
    if request.method == "POST":
        form_data = await request.form()
        path_data = form_data.get("path", "")

        if path_data and isinstance(path_data, str):
            path /= path_data.strip("/")

    logger.debug(f"Request path: {path} (BASE_PATH={settings.BASE_PATH})")

    contents = (File.from_path(p) for p in path.glob("*"))
    contents = sorted(contents, key=lambda f: f.name)
    context = {
        "request": request,
        "contents": contents,
        "path": path,
        "base_path": settings.BASE_PATH,
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
