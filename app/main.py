from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routers import auth_router, image_router
from .auth import get_current_user

app = FastAPI()

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router, prefix="/auth")
app.include_router(image_router, prefix="/images")

@app.on_event("startup")
async def startup_event():
    app.state.original_images = {}
    app.state.resized_images = {}

@app.on_event("shutdown")
async def shutdown_event():
    app.state.original_images.clear()
    app.state.resized_images.clear()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/upload", response_class=HTMLResponse)
def upload_form(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("upload.html", {"request": request, "current_user": current_user})
