# -*- coding: utf-8 -*-
"""
Encoding Fix Utilities - Rexus.app
Soluciona problemas de encoding en Windows y logging
"""

import sys
import os
import logging
import codecs


class SafeStreamHandler(logging.StreamHandler):
    """Handler que maneja caracteres Unicode de forma segura en Windows."""
    
    def __init__(self, stream=None):
        super().__init__(stream)
        self.encoding = 'utf-8'
    
    def emit(self, record):
        """Emite un registro de log de forma segura."""
        try:
            msg = self.format(record)
            
            # Limpiar caracteres problemáticos para Windows console
            if sys.platform.startswith('win'):
                # Reemplazar emojis y caracteres especiales problemáticos
                replacements = {
                    '🚀': '[ROCKET]',
                    '✅': '[OK]',
                    '❌': '[ERROR]',
                    '⚠️': '[WARNING]',
                    '📊': '[CHART]',
                    '🔧': '[TOOL]',
                    '🎯': '[TARGET]',
                    '📈': '[GRAPH]',
                    '💡': '[IDEA]',
                    '🔍': '[SEARCH]',
                    '📋': '[LIST]',
                    '🎮': '[GAME]',
                    '🖥️': '[COMPUTER]',
                    '🗄️': '[DATABASE]',
                    '🏁': '[FINISH]',
                    '🎉': '[PARTY]',
                    '📄': '[DOCUMENT]',
                    '🔄': '[REFRESH]',
                    '➕': '[PLUS]',
                    '✏️': '[EDIT]',
                    '🗑️': '[TRASH]',
                    '👁️': '[VIEW]',
                    '🏢': '[COMPANY]'
                }
                
                for emoji, replacement in replacements.items():
                    msg = msg.replace(emoji, replacement)
                
                # Convertir caracteres acentuados si es necesario
                try:
                    msg.encode('cp1252')
                except UnicodeEncodeError:
                    # Si no se puede codificar en cp1252, usar ASCII
                    msg = msg.encode('ascii', 'replace').decode('ascii')
            
            stream = self.stream
            if hasattr(stream, 'write'):
                stream.write(msg + self.terminator)
                if hasattr(stream, 'flush'):
                    stream.flush()
                    
        except Exception:
            # En caso de error, usar el handler base
            super().emit(record)


def setup_safe_console_encoding():
    """Configura encoding seguro para la consola."""
    if sys.platform.startswith('win'):
        try:
            # Intentar configurar UTF-8 en Windows
            import locale
            locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
        except:
            try:
                # Fallback a configuración por defecto
                locale.setlocale(locale.LC_ALL, '')
            except:
                pass
        
        # Configurar stdout y stderr para UTF-8 si es posible
        try:
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
            if hasattr(sys.stderr, 'buffer'):
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
        except:
            pass


def clean_text_for_console(text):
    """Limpia texto para mostrar en consola de Windows."""
    if not isinstance(text, str):
        text = str(text)
    
    if sys.platform.startswith('win'):
        # Reemplazar caracteres problemáticos
        replacements = {
            '🚀': '[ROCKET]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARNING]',
            '📊': '[CHART]',
            '🔧': '[TOOL]',
            '🎯': '[TARGET]',
            '📈': '[GRAPH]',
            '💡': '[IDEA]',
            '🔍': '[SEARCH]',
            '📋': '[LIST]',
            '🎮': '[GAME]',
            '🖥️': '[COMPUTER]',
            '🗄️': '[DATABASE]',
            '🏁': '[FINISH]',
            '🎉': '[PARTY]'
        }
        
        for emoji, replacement in replacements.items():
            text = text.replace(emoji, replacement)
        
        # Asegurarse de que sea compatible con cp1252
        try:
            text.encode('cp1252')
        except UnicodeEncodeError:
            text = text.encode('ascii', 'replace').decode('ascii')
    
    return text


def safe_print(text, **kwargs):
    """Función print segura para caracteres Unicode."""
    cleaned_text = clean_text_for_console(text)
    print(cleaned_text, **kwargs)


class UnicodeFileHandler(logging.FileHandler):
    """Handler de archivo que siempre usa UTF-8."""
    
    def __init__(self, filename, mode='a', encoding='utf-8', delay=False, errors='replace'):
        super().__init__(filename, mode, encoding=encoding, delay=delay, errors=errors)


def configure_logging_encoding():
    """Configura el sistema de logging para manejar UTF-8 correctamente."""
    # Obtener el logger raíz
    root_logger = logging.getLogger()
    
    # Remover handlers existentes de consola
    handlers_to_remove = []
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            handlers_to_remove.append(handler)
    
    for handler in handlers_to_remove:
        root_logger.removeHandler(handler)
    
    # Agregar handler seguro
    safe_handler = SafeStreamHandler(sys.stdout)
    safe_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    safe_handler.setFormatter(formatter)
    
    root_logger.addHandler(safe_handler)
    
    return safe_handler


# Aplicar configuración automáticamente al importar
setup_safe_console_encoding()

# Funciones de utilidad para usar en lugar de print
def info(msg):
    safe_print(f"[INFO] {msg}")

def warning(msg):
    safe_print(f"[WARNING] {msg}")

def error(msg):
    safe_print(f"[ERROR] {msg}")

def success(msg):
    safe_print(f"[OK] {msg}")