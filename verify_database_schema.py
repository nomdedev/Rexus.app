#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def verify_obras_schema():
    try:
        from rexus.core.database import InventarioDatabaseConnection
        db = InventarioDatabaseConnection()
        
        # Verificar y agregar columnas si no existen
        add_columns_sql = '''
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'codigo')
            ALTER TABLE obras ADD codigo NVARCHAR(50) NULL;
        
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'responsable')
            ALTER TABLE obras ADD responsable NVARCHAR(100) NULL;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'fecha_inicio')
            ALTER TABLE obras ADD fecha_inicio DATE NULL;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'fecha_fin_estimada')
            ALTER TABLE obras ADD fecha_fin_estimada DATE NULL;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'presupuesto_total')
            ALTER TABLE obras ADD presupuesto_total DECIMAL(18,2) NULL;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'progreso')
            ALTER TABLE obras ADD progreso DECIMAL(5,2) NULL DEFAULT 0.00;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'descripcion')
            ALTER TABLE obras ADD descripcion NVARCHAR(MAX) NULL;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'ubicacion')
            ALTER TABLE obras ADD ubicacion NVARCHAR(200) NULL;
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'created_at')
            ALTER TABLE obras ADD created_at DATETIME DEFAULT GETDATE();
            
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'obras' AND COLUMN_NAME = 'updated_at')
            ALTER TABLE obras ADD updated_at DATETIME DEFAULT GETDATE();
        '''
        
        db.ejecutar_query(add_columns_sql)
        print("✅ Esquema de tabla 'obras' verificado y actualizado")
        
        # Crear tabla detalles_obra si no existe
        create_detalles_sql = '''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='detalles_obra' AND xtype='U')
        BEGIN
            CREATE TABLE detalles_obra (
                id INT IDENTITY(1,1) PRIMARY KEY,
                obra_id INT NOT NULL,
                detalle NVARCHAR(MAX),
                categoria NVARCHAR(100),
                cantidad DECIMAL(10,2),
                precio_unitario DECIMAL(18,2),
                precio_total DECIMAL(18,2),
                fecha_creacion DATETIME DEFAULT GETDATE(),
                usuario_creador INT,
                FOREIGN KEY (obra_id) REFERENCES obras(id)
            );
        END
        '''
        
        db.ejecutar_query(create_detalles_sql)
        print("✅ Tabla 'detalles_obra' verificada y creada si es necesario")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando esquema BD: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Verificando y corrigiendo esquema de base de datos...")
    if verify_obras_schema():
        print("✅ Verificación completada exitosamente")
    else:
        print("❌ Error en verificación")
