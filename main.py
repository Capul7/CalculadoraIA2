from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
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
try:
    reader = easyocr.Reader(
        ['en'],
        download_enabled=False,
        model_storage_directory='models'
    )
except Exception as e:
    raise RuntimeError(f"❌ Error cargando modelos de EasyOCR: {e}")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/procesar-operacion/")
async def procesar_operacion(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Archivo vacío o no recibido.")

        npimg = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("No se pudo decodificar la imagen.")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        textos = reader.readtext(binary, detail=0)
        if not textos:
            raise ValueError("No se pudo extraer texto de la imagen.")

        detectado = ''.join(textos).replace('x', '*').replace('X', '*').replace('÷', '/').replace('=', '')

        if any(op in detectado for op in ['+', '-', '*', '/']):
            resultado = eval(detectado)
            return {"expresion": detectado, "resultado": resultado}
        else:
            return JSONResponse(status_code=400, content={"error": "No se detectó una operación válida."})

    except UnidentifiedImageError:
        return JSONResponse(status_code=400, content={"error": "Archivo de imagen inválido."})
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error al procesar la imagen: {str(e)}"})
