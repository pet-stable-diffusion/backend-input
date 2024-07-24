from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
from PIL import Image

app = FastAPI()

UPLOAD_DIRECTORY = "uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

RESIZED_DIRECTORY = "resized"
if not os.path.exists(RESIZED_DIRECTORY):
    os.makedirs(RESIZED_DIRECTORY)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIRECTORY), name="uploads")
app.mount("/resized", StaticFiles(directory=RESIZED_DIRECTORY), name="resized")

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    allowed_extensions = {"image/jpeg", "image/png"}
    
    if file.content_type not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only JPG and PNG files are allowed.")

    image_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1]
    file_path = os.path.join(UPLOAD_DIRECTORY, f"{image_id}.{file_extension}")
    
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
        
    resized_path = os.path.join(RESIZED_DIRECTORY, f"{image_id}.{file_extension}")
    with Image.open(file_path) as img:
        original_size = img.size
        img = img.resize((600, 800))  
        img.save(resized_path)
        resized_size = img.size

    return RedirectResponse(url=f"/show/{image_id}.{file_extension}?original_size={original_size}&resized_size={resized_size}", status_code=302)

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

@app.get("/show/{filename}")
def show_image(filename: str, original_size: str, resized_size: str):
    original_image_url = f"/uploads/{filename}"
    resized_image_url = f"/resized/{filename}"
    content = f"""
    <html>
        <head>
            <title>Image Display</title>
        </head>
        <body>
            <h2>Original Image:</h2>
            <img src="{original_image_url}" alt="original image"/>
            <p>Original Size: {original_size}</p>
            <h2>Resized Image:</h2>
            <img src="{resized_image_url}" alt="resized image"/>
            <p>Resized Size: {resized_size}</p>
        </body>
    </html>
    """
    return HTMLResponse(content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.159.13", port=9562)
