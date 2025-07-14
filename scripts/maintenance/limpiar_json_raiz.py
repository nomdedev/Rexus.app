"""
Script para limpiar la raiz del proyecto de archivos JSON redundantes
"""
# Directorio raíz del proyecto
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Verificar si los archivos de config_usuarios_columns existen en ambas ubicaciones
def verificar_y_limpiar_config_usuarios():
import json
import os
import shutil

    """Verifica y limpia archivos de configuración de columnas de usuarios"""
    archivos = [
        "config_usuarios_columns_default.json",
        "config_usuarios_columns_test.json"
    ]

    for archivo in archivos:
        ruta_raiz = os.path.join(ROOT_DIR, archivo)
        ruta_destino = os.path.join(ROOT_DIR, "config", "usuarios", archivo)

        # Verificar si existe en la raíz
        if os.path.exists(ruta_raiz):
            # Verificar si existe en destino
            if os.path.exists(ruta_destino):
                print(f"El archivo {archivo} ya existe en config/columnas/. Verificando contenido...")

                # Leer ambos archivos
                try:
                    with open(ruta_raiz, 'r', encoding='utf-8') as f:
                        contenido_raiz = json.load(f)

                    with open(ruta_destino, 'r', encoding='utf-8') as f:
                        contenido_destino = json.load(f)

                    # Comparar contenido
                    if contenido_raiz == contenido_destino:
                        print(f"El contenido de {archivo} es idéntico. Eliminando archivo de la raíz...")
                        os.remove(ruta_raiz)
                        print(f"Archivo {archivo} eliminado de la raíz")
                    else:
                        print(f"¡Advertencia! El contenido de {archivo} es diferente en ambas ubicaciones.")
                        print(f"Eliminando archivo de la raíz y manteniendo el de la carpeta config/columnas/...")
                        os.remove(ruta_raiz)
                        print(f"Archivo {archivo} eliminado de la raíz")

                except Exception as e:
                    print(f"Error al procesar {archivo}: {str(e)}")
            else:
                # No existe en destino, moverlo
                print(f"Moviendo {archivo} a config/columnas/...")
                try:
                    # Crear directorios si no existen
                    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                    shutil.move(ruta_raiz, ruta_destino)
                    print(f"Archivo {archivo} movido correctamente")
                except Exception as e:
                    print(f"Error al mover {archivo}: {str(e)}")
        else:
            print(f"El archivo {archivo} no existe en la raíz")

# Limpiar archivos .table_columns temporales de la raíz
def limpiar_archivos_temporales():
    """Elimina archivos temporales .table_columns de la raíz"""
    for archivo in os.listdir(ROOT_DIR):
        if archivo.startswith(".table_columns_") and archivo.endswith(".json"):
            ruta_archivo = os.path.join(ROOT_DIR, archivo)
            try:
                os.remove(ruta_archivo)
                print(f"Archivo temporal {archivo} eliminado de la raíz")
            except Exception as e:
                print(f"Error al eliminar {archivo}: {str(e)}")

def main():
    """Función principal"""
    print("=== Limpieza de archivos JSON redundantes en la raíz ===")

    verificar_y_limpiar_config_usuarios()
    limpiar_archivos_temporales()

    print("=== Limpieza completada ===")

if __name__ == "__main__":
    main()
