# Makefile para desarrollo rápido
.PHONY: dev dev-docker build clean install help

# Desarrollo local con hot-reload
dev:
	@echo "🔥 Iniciando desarrollo local con hot-reload..."
	@python dev-server.py

# Desarrollo con Docker
dev-docker:
	@echo "🐳 Iniciando desarrollo con Docker..."
	@docker-compose up --build

# Solo build del container
build:
	@echo "🔨 Construyendo imagen Docker..."
	@docker-compose build

# Instalar dependencias locales
install:
	@echo "📦 Instalando dependencias..."
	@pip install -r requirements.txt
	@pip install watchdog python-dotenv folium PyQt6-WebEngine

# Limpiar containers y volúmenes
clean:
	@echo "🧹 Limpiando containers y volúmenes..."
	@docker-compose down -v
	@docker system prune -f

# Mostrar ayuda
help:
	@echo "Comandos disponibles:"
	@echo "  make dev        - Desarrollo local con hot-reload"
	@echo "  make dev-docker - Desarrollo con Docker"
	@echo "  make build      - Construir imagen Docker"
	@echo "  make install    - Instalar dependencias"
	@echo "  make clean      - Limpiar containers"
	@echo "  make help       - Mostrar esta ayuda"

# Comando por defecto
.DEFAULT_GOAL := help
