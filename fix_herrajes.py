#!/usr/bin/env python3
"""
Script para limpiar el archivo herrajes/controller.py
"""

def fix_herrajes_controller():
    filepath = 'rexus/modules/herrajes/controller.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar secciones problemáticas específicas
    fixes = [
        # Limpiar código fragmentado y mal indentado
        (
            """            # else: # Comentado - bloque huérfano
                # if self.model and hasattr(self.model, 'obtener_todos_herrajes'):
                    # herrajes = self.model.obtener_todos_herrajes()
                # else:
                    # herrajes = None

            # Actualizar vista
                    except Exception as e:
            logger.error(f"Error: {e}")

    def helper_cargar_herrajes(self):
        if self.view and hasattr(self.view, "cargar_herrajes"):
                self.view.cargar_herrajes(herrajes)

        except Exception as e:
            logger.info(f"[ERROR HERRAJES CONTROLLER] Error en búsqueda: {e}")
            logging.error(f"Error en búsqueda herrajes: {e}")""",
            """            else:
                # Obtener todos los herrajes si no hay filtros ni términos
                if self.model and hasattr(self.model, 'obtener_todos_herrajes'):
                    herrajes = self.model.obtener_todos_herrajes()
                else:
                    herrajes = []

            # Actualizar vista
            if self.view and hasattr(self.view, "cargar_herrajes"):
                self.view.cargar_herrajes(herrajes)

        except Exception as e:
            logger.info(f"[ERROR HERRAJES CONTROLLER] Error en búsqueda: {e}")
            logging.error(f"Error en búsqueda herrajes: {e}")

    def helper_cargar_herrajes(self, herrajes):
        """Método auxiliar para cargar herrajes en la vista."""
        if self.view and hasattr(self.view, "cargar_herrajes"):
            self.view.cargar_herrajes(herrajes)"""
        ),
        
        # Corregir línea incompleta de búsqueda
        (
            "herrajes = self.model.buscar_herrajes(termino.strip()",
            "herrajes = self.model.buscar_herrajes(termino.strip())"
        ),
        
        # Corregir comentarios mal indentados
        (
            "                # else: # Comentado - bloque huérfano\n                    # herrajes = None",
            "                else:\n                    herrajes = []"
        ),
        
        (
            "                # else: # Comentado - bloque huérfano\n                    # herrajes = None",
            "                else:\n                    herrajes = []"
        )
    ]
    
    # Aplicar correcciones
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            print(f"✅ Aplicada corrección: {old[:50]}...")
    
    # Escribir archivo corregido
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Archivo limpiado: {filepath}")

if __name__ == "__main__":
    fix_herrajes_controller()
