"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

WebEngine Manager - Gestión robusta de QtWebEngine con fallbacks
"""

import logging
import os
import tempfile
from typing import Optional, Callable, Any, Dict
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextBrowser


class WebEngineManager:
    """Gestor robusto para QtWebEngine con fallbacks automáticos."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._webengine_available = None
        self._initialization_attempted = False
        self._webengine_view_class = None
        self._fallback_reasons = []
    
    def is_webengine_available(self) -> bool:
        """
        Verifica si QtWebEngine está disponible de forma robusta.
        
        Returns:
            True si QtWebEngine está disponible, False caso contrario
        """
        if self._webengine_available is not None:
            return self._webengine_available
        
        try:
            # Intentar importar QtWebEngine
            from PyQt6.QtWebEngine import QtWebEngine
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            
            # Verificar que la inicialización sea posible
            if not self._initialization_attempted:
                try:
                    QtWebEngine.initialize()
                    self._initialization_attempted = True
                    self.logger.info("QtWebEngine inicializado correctamente")
                except Exception as e:
                    self.logger.warning(f"Error inicializando QtWebEngine: {e}")
                    self._fallback_reasons.append(f"Inicialización falló: {e}")
                    self._webengine_available = False
                    return False
            
            self._webengine_view_class = QWebEngineView
            self._webengine_available = True
            return True
            
        except ImportError as e:
            self.logger.warning(f"QtWebEngine no disponible: {e}")
            self._fallback_reasons.append(f"Import falló: {e}")
            self._webengine_available = False
            return False
        
        except Exception as e:
            self.logger.error(f"Error inesperado verificando QtWebEngine: {e}")
            self._fallback_reasons.append(f"Error inesperado: {e}")
            self._webengine_available = False
            return False
    
    def create_web_view(self, fallback_message: str = None) -> QWidget:
        """
        Crea un widget de vista web con fallback automático.
        
        Args:
            fallback_message: Mensaje personalizado para el fallback
            
        Returns:
            QWebEngineView si está disponible, QTextBrowser como fallback
        """
        if self.is_webengine_available():
            try:
                web_view = self._webengine_view_class()
                self.logger.debug("QWebEngineView creado exitosamente")
                return web_view
            except Exception as e:
                self.logger.error(f"Error creando QWebEngineView: {e}")
                self._fallback_reasons.append(f"Creación falló: {e}")
        
        # Fallback a QTextBrowser
        return self._create_fallback_browser(fallback_message)
    
    def _create_fallback_browser(self, message: str = None) -> QTextBrowser:
        """
        Crea un navegador fallback usando QTextBrowser.
        
        Args:
            message: Mensaje personalizado a mostrar
            
        Returns:
            QTextBrowser configurado como fallback
        """
        browser = QTextBrowser()
        
        if message:
            fallback_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
                    <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px;">
                        <h3 style="color: #495057; margin-top: 0;">Vista Web No Disponible</h3>
                        <p style="color: #6c757d;">{message}</p>
                        <div style="margin-top: 20px; padding: 10px; background: #e9ecef; border-radius: 4px;">
                            <small style="color: #495057;">
                                Razones: {'; '.join(self._fallback_reasons[-3:]) if self._fallback_reasons else 'No especificadas'}
                            </small>
                        </div>
                    </div>
                </body>
            </html>
            """
        else:
            fallback_html = """
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
                    <div style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px;">
                        <h3 style="color: #495057; margin-top: 0;">Contenido Web</h3>
                        <p style="color: #6c757d;">Vista simplificada disponible</p>
                    </div>
                </body>
            </html>
            """
        
        browser.setHtml(fallback_html)
        browser.setMinimumHeight(300)
        self.logger.info("Usando QTextBrowser como fallback para vista web")
        return browser
    
    def load_url(self, widget: QWidget, url: str) -> bool:
        """
        Carga una URL en el widget de forma robusta.
        
        Args:
            widget: Widget donde cargar la URL
            url: URL a cargar
            
        Returns:
            True si se cargó exitosamente, False caso contrario
        """
        try:
            if self.is_webengine_available() and hasattr(widget, 'setUrl'):
                widget.setUrl(QUrl(url))
                return True
            elif hasattr(widget, 'setSource'):
                # Para QTextBrowser
                widget.setSource(QUrl(url))
                return True
            else:
                self.logger.warning(f"Widget no soporta carga de URL: {type(widget)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error cargando URL {url}: {e}")
            return False
    
    def load_html(self, widget: QWidget, html: str, base_url: str = None) -> bool:
        """
        Carga contenido HTML en el widget.
        
        Args:
            widget: Widget donde cargar el HTML
            html: Contenido HTML
            base_url: URL base para recursos relativos
            
        Returns:
            True si se cargó exitosamente, False caso contrario
        """
        try:
            if hasattr(widget, 'setHtml'):
                if base_url:
                    widget.setHtml(html, QUrl(base_url))
                else:
                    widget.setHtml(html)
                return True
            else:
                self.logger.warning(f"Widget no soporta carga de HTML: {type(widget)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error cargando HTML: {e}")
            return False
    
    def load_file(self, widget: QWidget, file_path: str) -> bool:
        """
        Carga un archivo local en el widget.
        
        Args:
            widget: Widget donde cargar el archivo
            file_path: Ruta al archivo
            
        Returns:
            True si se cargó exitosamente, False caso contrario
        """
        if not os.path.exists(file_path):
            self.logger.error(f"Archivo no encontrado: {file_path}")
            return False
        
        try:
            file_url = QUrl.fromLocalFile(os.path.abspath(file_path))
            return self.load_url(widget, file_url.toString())
            
        except Exception as e:
            self.logger.error(f"Error cargando archivo {file_path}: {e}")
            return False
    
    def create_map_widget(self, fallback_content: str = None) -> QWidget:
        """
        Crea un widget específico para mapas con fallback.
        
        Args:
            fallback_content: Contenido a mostrar si no hay mapa disponible
            
        Returns:
            Widget para mostrar mapas
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if self.is_webengine_available():
            try:
                map_view = self.create_web_view("Vista de mapa interactivo")
                map_view.setMinimumHeight(400)
                layout.addWidget(map_view)
                return container
                
            except Exception as e:
                self.logger.error(f"Error creando widget de mapa: {e}")
        
        # Fallback para mapas
        fallback = QLabel()
        if fallback_content:
            fallback.setText(fallback_content)
        else:
            fallback.setText("""
🗺️ Mapa Interactivo No Disponible

Para habilitar mapas interactivos, instale:
• PyQt6-WebEngine: pip install PyQt6-WebEngine
• folium: pip install folium

Motivos: {}
            """.format('; '.join(self._fallback_reasons[-2:]) if self._fallback_reasons else 'No especificados'))
        
        fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fallback.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                padding: 40px;
                color: #6c757d;
                font-size: 14px;
                font-family: Arial, sans-serif;
            }
        """)
        fallback.setMinimumHeight(400)
        layout.addWidget(fallback)
        
        return container
    
    def get_status_info(self) -> Dict[str, Any]:
        """
        Obtiene información del estado del WebEngine.
        
        Returns:
            Diccionario con información del estado
        """
        return {
            'available': self.is_webengine_available(),
            'initialized': self._initialization_attempted,
            'fallback_reasons': self._fallback_reasons.copy(),
            'view_class': str(self._webengine_view_class) if self._webengine_view_class else None
        }
    
    def cleanup_temp_files(self):
        """Limpia archivos temporales creados por el WebEngine."""
        try:
            # Limpiar archivos temporales del directorio temporal
            temp_dir = tempfile.gettempdir()
            for filename in os.listdir(temp_dir):
                if filename.startswith('rexus_map_') and filename.endswith('.html'):
                    try:
                        os.remove(os.path.join(temp_dir, filename))
                        self.logger.debug(f"Archivo temporal eliminado: {filename}")
                    except Exception as e:
                        self.logger.warning(f"No se pudo eliminar {filename}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error limpiando archivos temporales: {e}")


# Instancia global del gestor
webengine_manager = WebEngineManager()


# Funciones de conveniencia
def is_webengine_available() -> bool:
    """Función de conveniencia para verificar disponibilidad."""
    return webengine_manager.is_webengine_available()


def create_web_view(fallback_message: str = None) -> QWidget:
    """Función de conveniencia para crear vista web."""
    return webengine_manager.create_web_view(fallback_message)


def create_map_widget(fallback_content: str = None) -> QWidget:
    """Función de conveniencia para crear widget de mapa."""
    return webengine_manager.create_map_widget(fallback_content)


def load_url_safe(widget: QWidget, url: str) -> bool:
    """Función de conveniencia para cargar URL de forma segura."""
    return webengine_manager.load_url(widget, url)


def load_html_safe(widget: QWidget, html: str, base_url: str = None) -> bool:
    """Función de conveniencia para cargar HTML de forma segura."""
    return webengine_manager.load_html(widget, html, base_url)


def get_webengine_status() -> Dict[str, Any]:
    """Función de conveniencia para obtener estado del WebEngine."""
    return webengine_manager.get_status_info()