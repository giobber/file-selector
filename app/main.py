import sys

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
async def home(request: Request, sub_path: str = ""):
    context = {"request": request, "sub_path": sub_path}
    return templates.TemplateResponse("index.html", context)


@app.post("/search")
async def search(request: Request):
    form_data = await request.form()
    sub_path = form_data.get("sub_path", None)
    if isinstance(sub_path, str):
        return await home(request, sub_path)
    return RedirectResponse(url="/home")


@app.get("/root", response_class=HTMLResponse)
@app.post("/root", response_class=HTMLResponse)
@app.get("/root/{sub_path:path}", response_class=HTMLResponse)
async def path_contents(
    request: Request,
    sub_path: str = "",
    settings: Settings = Depends(get_settings),
):
    if request.method == "POST":
        form_data = await request.form()
        value = form_data.get("sub_path", "")
        if value and isinstance(value, str):
            sub_path = value

    path = settings.BASE_PATH / sub_path

    logger.debug(f"Request path: {sub_path}")
    logger.debug(f"Base path: {settings.BASE_PATH}")
    logger.debug(f"Full path: {path}")

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
    # Note: technically there should be something that tell where the request come from before setting this header
    headers = {"HX-Push-Url": f"/home/{sub_path}"}
    return templates.TemplateResponse("table.html", context, headers=headers)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
