from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from .. import schemas, crud, database, auth

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/signup/", response_class=HTMLResponse)
def signup(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = schemas.UserCreate(username=username, password=password)
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    crud.create_user(db=db, user=user)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@router.post("/login/", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = OAuth2PasswordRequestForm(username=username, password=password)
    db_user = crud.authenticate_user(db, user.username, user.password)
    if not db_user:
        error_message = "Incorrect username or password"
        return templates.TemplateResponse("login.html", {"request": request, "error": error_message})
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/upload", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@router.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user
