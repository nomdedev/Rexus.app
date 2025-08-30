"""
Ejemplo de uso del nuevo sistema de Dependency Injection para DatabaseManager.

Este archivo demuestra cómo usar la nueva arquitectura sin Singletons globales.
"""

from rexus.core.database_manager import DatabaseManagerFactory, DatabaseManagerContext
import logging

logger = logging.getLogger(__name__)

# ===== EJEMPLO 1: USO BÁSICO CON FACTORY =====

def ejemplo_factory():
    """Ejemplo de uso básico con DatabaseManagerFactory."""

    # Crear instancia con nombre específico
    db = DatabaseManagerFactory.create_manager(
        db_path="data/app.db",
        name="main_db"
    )

    try:
        # Usar la instancia
        users = db.execute_query("SELECT * FROM users WHERE active = 1")
        logger.info(f"Encontrados {len(users)} usuarios activos")

        # Crear otra instancia para otra base de datos
        backup_db = DatabaseManagerFactory.create_manager(
            db_path="data/backup.db",
            name="backup_db"
        )

        # Usar la segunda instancia
        stats = backup_db.get_database_stats()
        logger.info(f"Estadísticas de backup: {stats}")

    finally:
        # Limpiar instancias
        DatabaseManagerFactory.close_manager("main_db")
        DatabaseManagerFactory.close_manager("backup_db")


# ===== EJEMPLO 2: USO CON CONTEXT MANAGER =====

def ejemplo_context_manager():
    """Ejemplo de uso con context manager (recomendado)."""

    with DatabaseManagerContext("data/app.db", "temp_db") as db:
        # La conexión se maneja automáticamente
        products = db.execute_query("SELECT * FROM products LIMIT 10")
        logger.info(f"Primeros 10 productos: {len(products)}")

        # Crear backup automáticamente
        db.backup_database("data/backup_auto.db")


# ===== EJEMPLO 3: INYECCIÓN DE DEPENDENCIAS EN CLASES =====

class UserService:
    """Servicio de usuarios con inyección de dependencias."""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_active_users(self):
        """Obtiene usuarios activos."""
        return self.db.execute_query("SELECT * FROM users WHERE active = 1")

    def create_user(self, name: str, email: str):
        """Crea un nuevo usuario."""
        return self.db.execute_query(
            "INSERT INTO users (name, email, active) VALUES (?, ?, 1)",
            (name, email)
        )


class ProductService:
    """Servicio de productos con inyección de dependencias."""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_low_stock_products(self):
        """Obtiene productos con stock bajo."""
        return self.db.execute_query("SELECT * FROM products WHERE stock < 10")


def ejemplo_dependency_injection():
    """Ejemplo de inyección de dependencias."""

    # Crear instancias de servicios con la misma DB
    db = DatabaseManagerFactory.create_manager("data/app.db", "services_db")

    try:
        user_service = UserService(db)
        product_service = ProductService(db)

        # Usar servicios
        active_users = user_service.get_active_users()
        low_stock = product_service.get_low_stock_products()

        logger.info(f"Usuarios activos: {len(active_users)}")
        logger.info(f"Productos con stock bajo: {len(low_stock)}")

    finally:
        DatabaseManagerFactory.close_manager("services_db")


# ===== EJEMPLO 4: TESTING CON MOCKS =====

def ejemplo_testing_con_mocks():
    """Ejemplo de cómo hacer testing con el nuevo sistema."""

    # En tests, puedes crear instancias separadas
    test_db = DatabaseManagerFactory.create_manager(
        db_path=":memory:",  # SQLite en memoria para tests
        name="test_db"
    )

    try:
        # Crear tablas de test
        test_db.execute_query("""
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        """)

        # Insertar datos de test
        test_db.execute_query(
            "INSERT INTO test_users (name, email) VALUES (?, ?)",
            ("Test User", "test@example.com")
        )

        # Verificar datos
        users = test_db.execute_query("SELECT * FROM test_users")
        assert len(users) == 1
        assert users[0]['name'] == "Test User"

        logger.info("✅ Test pasado exitosamente")

    finally:
        DatabaseManagerFactory.close_manager("test_db")


# ===== FUNCIÓN PRINCIPAL =====

def main():
    """Función principal con ejemplos."""
    logging.basicConfig(level=logging.INFO)

    print("🚀 Ejemplos de Dependency Injection con DatabaseManager")
    print("=" * 60)

    try:
        print("\n1. 📋 Ejemplo con Factory:")
        ejemplo_factory()

        print("\n2. 🔄 Ejemplo con Context Manager:")
        ejemplo_context_manager()

        print("\n3. 💉 Ejemplo con Dependency Injection:")
        ejemplo_dependency_injection()

        print("\n4. 🧪 Ejemplo para Testing:")
        ejemplo_testing_con_mocks()

        print("\n✅ Todos los ejemplos completados exitosamente!")

    except Exception as e:
        logger.error(f"Error en ejemplos: {e}", exc_info=True)

    finally:
        # Asegurar que todas las instancias se cierren
        DatabaseManagerFactory.close_all()
        print("\n🧹 Todas las conexiones limpiadas")


if __name__ == "__main__":
    main()
