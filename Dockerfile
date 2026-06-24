# 1. Usar una imagen oficial de Python ligera
FROM python:3.11-slim

# 2. Crear la carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar el archivo de librerías e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar todo el código del proyecto a la carpeta /app
COPY . .

# 5. Indicar el puerto que usará FastAPI
EXPOSE 8000

# 6. Comando para arrancar el servidor de desarrollo/producción
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
