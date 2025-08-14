"""SQL Script Loader Utility"""

import logging
from pathlib import Path

class SQLScriptLoader:
    def __init__(self, scripts_dir=None):
        if scripts_dir is None:
            # Auto-detect scripts directory relative to the project root
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent  # Go up from rexus/utils/
            scripts_dir = project_root / "scripts" / "sql"

        self.scripts_dir = Path(scripts_dir)
        self.logger = logging.getLogger(__name__)

    def load_script(self, script_name):
        try:
            script_path = self.scripts_dir / f"{script_name}.sql"
            if script_path.exists():
                with open(script_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                self.logger.warning(f"Script SQL no encontrado: {script_path}")
                return None
        except Exception as e:
            self.logger.error(f"Error cargando script {script_name}: {e}")
            return None

    def execute_script(self, cursor, script_name, params=None):
        script = self.load_script(script_name)
        if script:
            try:
                if params:
                    cursor.execute(script, params)
                else:
                    cursor.execute(script)
                return True
            except Exception as e:
                self.logger.error(f"Error ejecutando script {script_name}: {e}")
                return False
        return False

sql_script_loader = SQLScriptLoader()
