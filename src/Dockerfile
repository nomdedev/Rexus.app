# ====================================================
# REXUS APP - DOCKERFILE PARA PRODUCCIÓN
# ====================================================
# Multi-stage build para optimizar el tamaño de imagen

# ===== STAGE 1: Builder =====
FROM python:3.11-slim as builder

# Metadatos
LABEL maintainer="Rexus Team"
LABEL version="2.0.0"
LABEL description="Rexus - Sistema de gestión empresarial"

# Variables de entorno para build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    make \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# ===== STAGE 2: Runtime =====
FROM python:3.11-slim as runtime

# Variables de entorno para runtime
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV APP_ENV=production

# Instalar dependencias runtime mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root con UID específico
RUN groupadd -r appuser --gid=1001 && \
    useradd -r -g appuser --uid=1001 --create-home --shell /bin/bash appuser

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/uploads /app/backups /app/temp && \
    chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser
WORKDIR /app

# Copiar dependencias Python del builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copiar código fuente
COPY --chown=appuser:appuser . .

# Crear archivo .env por defecto si no existe
RUN if [ ! -f .env ]; then \
        cp .env.example .env && \
        sed -i 's/DB_PASSWORD=tu_contraseña_segura_aqui/DB_PASSWORD=default_docker_password/' .env; \
    fi

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import src.core.config; print('OK')" || exit 1

# Puerto de la aplicación
EXPOSE 8000

# Punto de entrada
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Comando por defecto
CMD ["python", "src/main/app.py"]

# ===== STAGE 3: Development =====
FROM runtime as development

# Cambiar a root temporalmente para instalar dependencias de desarrollo
USER root

# Instalar dependencias de desarrollo
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Instalar herramientas de desarrollo Python
USER appuser
RUN pip install --user --no-warn-script-location \
    pytest>=8.2.0 \
    pytest-cov>=4.0.0 \
    pytest-mock>=3.12.0 \
    pytest-qt>=4.3.0 \
    black>=24.0.0 \
    isort>=5.13.0 \
    flake8>=7.0.0 \
    mypy>=1.8.0 \
    bandit>=1.7.0

# Variables de entorno para desarrollo
ENV APP_ENV=development
ENV APP_DEBUG=true

# Comando por defecto para desarrollo
CMD ["python", "-m", "pytest", "tests/", "-v"]

# ===== STAGE 4: Testing =====
FROM development as testing

# Variables de entorno para testing
ENV APP_ENV=testing
ENV QT_QPA_PLATFORM=offscreen

# Instalar dependencias adicionales para testing UI
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    && rm -rf /var/lib/apt/lists/*

USER appuser

# Comando para ejecutar tests con cobertura
CMD ["python", "-m", "pytest", "tests/", "-v", "--cov=src", "--cov-report=html", "--cov-report=term"]
