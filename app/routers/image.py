from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from PIL import Image
from io import BytesIO
import os
import uuid
from sqlalchemy.orm import Session
from ..auth import get_current_user  # 상대 경로 사용
from ..database import get_db
from .. import schemas  # 상대 경로 사용

router = APIRouter()

UPLOAD_DIRECTORY = "app/static/uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@router.post("/upload/", response_class=HTMLResponse)
async def upload_image(
    request: Request,
    file: UploadFile = File(...), 
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed_extensions = {"image/jpeg", "image/png"}
    
    if file.content_type not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only JPG and PNG files are allowed.")
    
    image_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1].lower()
    
    image_bytes = await file.read()
    image = Image.open(BytesIO(image_bytes))
    original_size = image.size
    
    resized_image = image.resize((800, 800))
    resized_size = resized_image.size
    
    original_image_path = os.path.join(UPLOAD_DIRECTORY, f"{image_id}.{file_extension}")
    resized_image_path = os.path.join(UPLOAD_DIRECTORY, f"{image_id}_resized.{file_extension}")
    
    image.save(original_image_path)
    resized_image.save(resized_image_path)
    
    return HTMLResponse(f"""
    <html>
        <head>
            <title>Image Display</title>
        </head>
        <body>
            <h2>Original Image:</h2>
            <img src="/static/uploads/{image_id}.{file_extension}" alt="original image"/>
            <p>Original Size: {original_size}</p>
            <h2>Resized Image:</h2>
            <img src="/static/uploads/{image_id}_resized.{file_extension}" alt="resized image"/>
            <p>Resized Size: {resized_size}</p>
        </body>
    </html>
    """)

@router.get("/images/original/{filename}")
async def get_original_image(request: Request, filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return StreamingResponse(open(file_path, "rb"), media_type=f"image/{filename.split('.')[-1]}")

@router.get("/images/resized/{filename}")
async def get_resized_image(request: Request, filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return StreamingResponse(open(file_path, "rb"), media_type=f"image/{filename.split('.')[-1]}")
