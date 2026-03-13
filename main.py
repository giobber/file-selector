import sys

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from config.settings import Settings, get_settings, log_settings

# Setup logger
logger.remove()
logger.add(sys.stderr, level=get_settings().LOG_LEVEL)
log_settings()

# Initialize FastAPI app
app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, settings: Settings = Depends(get_settings)):
    context = {"request": request, "debug": settings.DEBUG}
    return templates.TemplateResponse("index.html", context)


@app.get("/path", response_class=HTMLResponse)
async def path_contents(request: Request, settings: Settings = Depends(get_settings)):
    contents = ({"name": p.stem} for p in settings.BASE_PATH.glob("*"))
    context = {"request": request, "contents": contents}
    return templates.TemplateResponse("table.j2.html", context)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
