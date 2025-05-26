# Imagen base oficial de Python
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar todo el código fuente al contenedor
COPY . .

# Copiar explícitamente los modelos si están fuera del .gitignore
# (Asegúrate de no ignorarlos en el contexto de build si haces esto)
COPY models/ models/

# Instalar dependencias del sistema necesarias para OpenCV y EasyOCR
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que correrá FastAPI
EXPOSE 8000
# Comando de ejecución
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
