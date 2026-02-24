"""
SkillExecutorAgent - Agente que integra y ejecuta skills del sistema
Responsable de orquestar skills de Claude Code
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
from ..core.base_agent import BaseAgent, AgentConfig, AgentResponse


class SkillExecutorAgent(BaseAgent):
    """
    Agente especializado en ejecución de skills

    Responsabilidades:
    - Detectar skills disponibles
    - Ejecutar skills apropiados
    - Encadenar skills
    - Manejar resultados de skills
    """

    # Skills disponibles en el sistema
    AVAILABLE_SKILLS = [
        'keybindings-help',
        'frontend-design',
        'remotion-best-practices',
        'skill-creator',
        'vercel-react-best-practices',
        'web-design-guidelines'
    ]

    def __init__(self, config: Optional[AgentConfig] = None):
        """Inicializar agente de skills"""
        if config is None:
            config = AgentConfig(
                name="SkillExecutorAgent",
                description="Agente especializado en ejecución de skills",
                tags=['skills', 'automation', 'orchestration']
            )

        super().__init__(config)
        self.skill_results = {}

    async def analyze(
        self,
        target: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """
        Analizar qué skills son necesarios

        Args:
            target: Tipo de tarea (ej: 'frontend', 'refactoring', 'testing')
            context: Contexto de la tarea
        """
        try:
            self.logger.info(f"Analizando skills para: {target}")

            # Detectar skills aplicables
            applicable_skills = await self._detect_applicable_skills(target, context)

            analysis = {
                'target': target,
                'applicable_skills': applicable_skills,
                'skill_count': len(applicable_skills),
                'recommendations': await self._recommend_skill_sequence(applicable_skills, context)
            }

            return AgentResponse(
                agent_name=self.config.name,
                status='success',
                content=f"Análisis completado: {len(applicable_skills)} skills aplicables",
                metadata={'analysis': analysis}
            )

        except Exception as e:
            return AgentResponse(
                agent_name=self.config.name,
                status='error',
                content=f"Error: {str(e)}",
                metadata={'error': str(e)}
            )

    async def _detect_applicable_skills(
        self,
        target: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """Detectar qué skills son aplicables"""
        applicable = []

        target_lower = target.lower()

        # Mapeo de targets a skills
        skill_map = {
            'frontend': ['frontend-design', 'vercel-react-best-practices'],
            'ui': ['frontend-design', 'web-design-guidelines'],
            'design': ['frontend-design', 'web-design-guidelines'],
            'react': ['vercel-react-best-practices'],
            'refactoring': [],  # Skills específicos de refactoring
            'testing': [],  # Skills específicos de testing
            'video': ['remotion-best-practices'],
            'shortcuts': ['keybindings-help']
        }

        for key, skills in skill_map.items():
            if key in target_lower:
                applicable.extend(skills)

        return list(set(applicable))  # Eliminar duplicados

    async def _recommend_skill_sequence(
        self,
        skills: List[str],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Recomendar secuencia de ejecución de skills"""
        recommendations = []

        # Prioridades de ejecución
        priority_map = {
            'frontend-design': 1,
            'vercel-react-best-practices': 2,
            'web-design-guidelines': 3
        }

        # Ordenar por prioridad
        sorted_skills = sorted(
            skills,
            key=lambda s: priority_map.get(s, 99)
        )

        for skill in sorted_skills:
            recommendations.append({
                'skill': skill,
                'priority': priority_map.get(skill, 99),
                'description': self._get_skill_description(skill),
                'expected_outcome': self._get_skill_outcome(skill)
            })

        return recommendations

    def _get_skill_description(self, skill: str) -> str:
        """Obtener descripción de un skill"""
        descriptions = {
            'keybindings-help': 'Ayuda para personalizar atajos de teclado',
            'frontend-design': 'Crear interfaces frontend de alta calidad',
            'remotion-best-practices': 'Mejores prácticas para Remotion',
            'skill-creator': 'Crear nuevos skills personalizados',
            'vercel-react-best-practices': 'Optimización de React/Next.js',
            'web-design-guidelines': 'Revisión de UI contra mejores prácticas'
        }
        return descriptions.get(skill, 'Skill desconocido')

    def _get_skill_outcome(self, skill: str) -> str:
        """Obtener resultado esperado de un skill"""
        outcomes = {
            'keybindings-help': 'Configuración optimizada de atajos',
            'frontend-design': 'Interfaz moderna y funcional',
            'remotion-best-practices': 'Video optimizado',
            'skill-creator': 'Nuevo skill creado',
            'vercel-react-best-practices': 'Código React optimizado',
            'web-design-guidelines': 'UI conforme a estándares'
        }
        return outcomes.get(skill, 'Resultado no especificado')

    async def execute_skill(
        self,
        skill_name: str,
        params: Dict[str, Any]
    ) -> AgentResponse:
        """
        Ejecutar un skill específico

        Args:
            skill_name: Nombre del skill a ejecutar
            params: Parámetros para el skill
        """
        try:
            self.logger.info(f"Ejecutando skill: {skill_name}")

            # Aquí iría la integración real con el sistema de skills
            result = await self._run_skill(skill_name, params)

            self.skill_results[skill_name] = result

            return AgentResponse(
                agent_name=self.config.name,
                status='success',
                content=f"Skill {skill_name} ejecutado",
                metadata={'result': result}
            )

        except Exception as e:
            return AgentResponse(
                agent_name=self.config.name,
                status='error',
                content=f"Error ejecutando skill: {str(e)}",
                metadata={'error': str(e)}
            )

    async def _run_skill(
        self,
        skill_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecutar un skill (implementación simulada)

        En la implementación real, esto llamaría a Skill tool
        """
        return {
            'skill': skill_name,
            'params': params,
            'status': 'executed',
            'timestamp': datetime.now().isoformat(),
            'output': f"Resultado de {skill_name}"
        }

    async def generate_report(self, analysis_data: Dict[str, Any]) -> str:
        """Generar reporte de skills"""
        report = {
            'tipo': 'REPORTE_SKILLS',
            'fecha': datetime.now().isoformat(),
            'agente': self.config.name,
            'analisis': analysis_data,
            'skills_disponibles': self.AVAILABLE_SKILLS,
            'skills_ejecutados': list(self.skill_results.keys())
        }

        return json.dumps(report, indent=2, ensure_ascii=False)

    async def propose_improvements(
        self,
        analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Proponer mejoras (nuevos skills a crear)"""
        improvements = []

        # Analizar gaps en skills
        target = analysis_data.get('target', '')
        applicable = analysis_data.get('applicable_skills', [])

        if len(applicable) == 0:
            improvements.append({
                'id': 'SKILL-001',
                'titulo': 'Crear nuevo skill',
                'descripcion': f'No hay skills disponibles para: {target}',
                'prioridad': 'media',
                'impacto': 'automatización',
                'esfuerzo': 'alto'
            })

        return improvements

    async def execute_approved_changes(
        self,
        changes: List[Dict[str, Any]],
        approval_metadata: Dict[str, Any]
    ) -> AgentResponse:
        """Ejecutar cambios (crear nuevos skills)"""
        try:
            results = []
            for change in changes:
                result = await self._execute_change(change)
                results.append(result)

            return AgentResponse(
                agent_name=self.config.name,
                status='success',
                content=f"{len(results)} cambios ejecutados",
                metadata={'results': results}
            )

        except Exception as e:
            return AgentResponse(
                agent_name=self.config.name,
                status='error',
                content=f"Error: {str(e)}",
                metadata={'error': str(e)}
            )

    async def _execute_change(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar cambio específico"""
        return {
            'change_id': change.get('id'),
            'status': 'executed',
            'timestamp': datetime.now().isoformat()
        }
