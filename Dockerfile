# Dockerfile para Rexus.app
FROM python:3.11-slim

# Variables de entorno para evitar prompts y mejorar logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para PyQt6 y pyodbc
RUN apt-get update && \
    apt-get install -y build-essential libgl1 libegl1 libglib2.0-0 libpq-dev unixodbc-dev libxkbcommon0 libxkbcommon-x11-0 libfontconfig1 libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del código fuente
COPY . .

# Exponer el puerto si tu app lo usa (ajusta si es necesario)
# EXPOSE 8000

# Comando por defecto para ejecutar la app
CMD ["python", "main.py"]
