"""
API Server - Rexus.app
Servidor API REST para comunicación con el frontend
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import threading

# Sistema de logging
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, HTTPException, Depends, status, Request, Body
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI no disponible - usando fallback")
    FASTAPI_AVAILABLE = False
    
    # Fallback clases
    class FastAPI:
        def __init__(self, *args, **kwargs):
            pass
    
    class HTTPBearer:
        def __init__(self, *args, **kwargs):
            pass

    class HTTPAuthorizationCredentials:
        def __init__(self, scheme: str, credentials: str):
            self.scheme = scheme
            self.credentials = credentials

class RexusAPIServer:
    """Servidor API principal de Rexus."""
    
    def __init__(self):
        self.app = FastAPI(
            title="Rexus API",
            description="API REST para Rexus.app",
            version="1.0.0"
        ) if FASTAPI_AVAILABLE else None
        
        if self.app:
            self._setup_middleware()
            self._setup_routes()
    
    def _setup_middleware(self):
        """Configura middleware de la API."""
        if not self.app:
            return
        
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Configura rutas de la API."""
        if not self.app:
            return
        
        @self.app.get("/")
        async def root():
            return {"message": "Rexus API Server", "version": "1.0.0"}
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": "2025-08-23"}
    
    def start(self, host: str = "127.0.0.1", port: int = 8000):
        """Inicia el servidor API."""
        if not FASTAPI_AVAILABLE:
            logger.error("No se puede iniciar API server - FastAPI no disponible")
            return False
        
        try:
            logger.info(f"Iniciando API server en {host}:{port}")
            uvicorn.run(self.app, host=host, port=port)
            return True
        except Exception as e:
            logger.exception(f"Error iniciando API server: {e}")
            return False

def create_app() -> Optional[FastAPI]:
    """Factory para crear aplicación FastAPI."""
    if not FASTAPI_AVAILABLE:
        return None
    
    server = RexusAPIServer()
    return server.app

if __name__ == "__main__":
    server = RexusAPIServer()
    server.start()