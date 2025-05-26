from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import cv2
import numpy as np
from PIL import Image
import easyocr
import io
import os

app = FastAPI()

# CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MONTAJE DE ARCHIVOS ESTÁTICOS Y PLANTILLAS
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")  # ✅ ESTA RUTA ES CORRECTA

# ✅ Inicializar EasyOCR usando modelos locales
reader = easyocr.Reader(
    ['en'],
    download_enabled=False,
    model_storage_directory='models'  # carpeta que subirás junto al proyecto
)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/procesar-operacion/")
async def procesar_operacion(file: UploadFile = File(...)):
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    textos = reader.readtext(binary, detail=0)
    detectado = ''.join(textos).replace('x', '*').replace('X', '*').replace('÷', '/').replace('=', '')

    try:
        if any(op in detectado for op in ['+', '-', '*', '/']):
            resultado = eval(detectado)
            return {"expresion": detectado, "resultado": resultado}
        else:
            return JSONResponse(status_code=400, content={"error": "No se detectó una operación válida."})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Error en evaluación: {str(e)}"})
