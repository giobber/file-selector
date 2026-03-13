from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config.settings import Settings, get_settings

app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, settings: Settings = Depends(get_settings)):
    print(settings)
    return templates.TemplateResponse(
        "index.html", {"request": request, "debug": settings.DEBUG}
    )


@app.post("/button-click", response_class=HTMLResponse)
async def button_click():
    return "<p>Hello from HTMX!</p>"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
