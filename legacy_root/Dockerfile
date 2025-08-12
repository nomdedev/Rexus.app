# Dockerfile para desarrollo rápido con hot-reload
FROM python:3.10-slim

# Instalar dependencias del sistema para PyQt6 y bases de datos
RUN apt-get update && apt-get install -y \
    qt6-base-dev \
    qt6-webengine-dev \
    libqt6webengine6 \
    libqt6webenginewidgets6 \
    xvfb \
    x11vnc \
    fluxbox \
    wget \
    unixodbc-dev \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Instalar Microsoft ODBC Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Configurar display virtual para PyQt6
ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=xcb

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar dependencias adicionales para desarrollo
RUN pip install watchdog python-dotenv folium PyQt6-WebEngine

# Copiar código fuente
COPY . .

# Crear script de inicio con hot-reload
RUN echo '#!/bin/bash\n\
# Iniciar Xvfb en background\n\
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &\n\
\n\
# Iniciar VNC server para debugging (opcional)\n\
x11vnc -display :99 -nopw -listen localhost -xkb > /dev/null 2>&1 &\n\
\n\
# Iniciar la aplicación con watchdog para hot-reload\n\
python -c "\n\
import sys\n\
import time\n\
import subprocess\n\
from watchdog.observers import Observer\n\
from watchdog.events import FileSystemEventHandler\n\
\n\
class RestartHandler(FileSystemEventHandler):\n\
    def __init__(self):\n\
        self.process = None\n\
        self.restart_app()\n\
    \n\
    def on_modified(self, event):\n\
        if event.src_path.endswith(\".py\"):\n\
            print(f\"Archivo modificado: {event.src_path}\")\n\
            self.restart_app()\n\
    \n\
    def restart_app(self):\n\
        if self.process:\n\
            self.process.terminate()\n\
            self.process.wait()\n\
        print(\"Reiniciando aplicación...\")\n\
        self.process = subprocess.Popen([sys.executable, \"main.py\"])\n\
\n\
if __name__ == \"__main__\":\n\
    event_handler = RestartHandler()\n\
    observer = Observer()\n\
    observer.schedule(event_handler, \"./rexus\", recursive=True)\n\
    observer.start()\n\
    \n\
    try:\n\
        while True:\n\
            time.sleep(1)\n\
    except KeyboardInterrupt:\n\
        observer.stop()\n\
        if event_handler.process:\n\
            event_handler.process.terminate()\n\
    observer.join()\n\
"\n\
' > /app/start-dev.sh && chmod +x /app/start-dev.sh

EXPOSE 5900
CMD ["/app/start-dev.sh"]
