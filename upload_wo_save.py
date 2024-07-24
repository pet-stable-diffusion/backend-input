from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
import uuid
from io import BytesIO
from PIL import Image

app = FastAPI()

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # 허용되는 파일 확장자
    allowed_extensions = {"image/jpeg", "image/png"}
    
    # 파일 확장자 검사
    if file.content_type not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only JPG and PNG files are allowed.")
    
    # 고유한 image_id 생성
    image_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1].upper()
    
    # 이미지 읽기
    image_bytes = await file.read()
    image = Image.open(BytesIO(image_bytes))
    original_size = image.size
    
    # 이미지 리사이즈
    resized_image = image.resize((800, 800))
    resized_size = resized_image.size
    
    # 이미지를 메모리에 저장
    original_image_bytes = BytesIO()
    resized_image_bytes = BytesIO()
    image.save(original_image_bytes, format=file_extension)
    resized_image.save(resized_image_bytes, format=file_extension)
    original_image_bytes.seek(0)
    resized_image_bytes.seek(0)
    
    # 메모리에 이미지 저장
    app.state.original_images[image_id] = original_image_bytes
    app.state.resized_images[image_id] = resized_image_bytes

    return HTMLResponse(f"""
    <html>
        <head>
            <title>Image Display</title>
        </head>
        <body>
            <h2>Original Image:</h2>
            <img src="/image/original/{image_id}.{file_extension.lower()}" alt="original image"/>
            <p>Original Size: {original_size}</p>
            <h2>Resized Image:</h2>
            <img src="/image/resized/{image_id}.{file_extension.lower()}" alt="resized image"/>
            <p>Resized Size: {resized_size}</p>
        </body>
    </html>
    """)

@app.get("/image/original/{filename}")
async def get_original_image(filename: str):
    image_id = filename.split('.')[0]
    if image_id not in app.state.original_images:
        raise HTTPException(status_code=404, detail="Image not found")
    return StreamingResponse(app.state.original_images[image_id], media_type=f"image/{filename.split('.')[-1]}")

@app.get("/image/resized/{filename}")
async def get_resized_image(filename: str):
    image_id = filename.split('.')[0]
    if image_id not in app.state.resized_images:
        raise HTTPException(status_code=404, detail="Image not found")
    return StreamingResponse(app.state.resized_images[image_id], media_type=f"image/{filename.split('.')[-1]}")

@app.on_event("startup")
async def startup_event():
    app.state.original_images = {}
    app.state.resized_images = {}

@app.on_event("shutdown")
async def shutdown_event():
    app.state.original_images.clear()
    app.state.resized_images.clear()

@app.get("/")
def main():
    content = """
    <html>
        <head>
            <title>Image Upload</title>
        </head>
        <body>
            <h1>Upload an Image</h1>
            <form action="/upload/" enctype="multipart/form-data" method="post">
                <input name="file" type="file">
                <input type="submit">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.159.13", port=8080)