"""Módulo de reportes estadísticos usando programación funcional (filter, map, reduce)."""

from __future__ import annotations
from functools import reduce
from src.modelos import Cita


class GeneradorReportes:
    """Genera reportes mensuales y por especialidad excluyendo citas canceladas."""

    def __init__(self, citas: list[Cita]) -> None:
        self._citas = citas

    def filtrar_activas(self) -> list[Cita]:
        """Filtra únicamente citas no canceladas usando filter()."""
        return list(filter(lambda cita: cita.es_activa(), self._citas))

    def resumen_consultas_enmascaradas(self) -> list[dict]:
        """Transforma las citas activas en diccionarios seguros usando map()."""
        activas = self.filtrar_activas()
        return list(
            map(
                lambda c: {
                    "id_cita": c.id_cita,
                    "paciente": c.paciente.nombre,
                    "documento": c.paciente.obtener_documento_enmascarado(),
                    "especialidad": c.profesional.especialidad,
                    "fecha": c.fecha_hora.strftime("%Y-%m-%d %H:%M"),
                    "estado": c.estado,
                },
                activas,
            )
        )

    def reporte_por_especialidad(self) -> dict[str, int]:
        """Agrupa y cuenta citas activas por especialidad usando filter, map y reduce."""
        especialidades = map(
            lambda c: c.profesional.especialidad, self.filtrar_activas()
        )

        def acumular(conteo: dict[str, int], especialidad: str) -> dict[str, int]:
            nuevo = dict(conteo)
            nuevo[especialidad] = nuevo.get(especialidad, 0) + 1
            return nuevo

        return reduce(acumular, especialidades, {})

    def reporte_por_mes(self, anio_mes: str | None = None) -> dict[str, int]:
        """Agrupa citas activas por mes (YYYY-MM), opcionalmente filtrando un mes específico."""
        activas = self.filtrar_activas()
        if anio_mes:
            activas = list(
                filter(lambda c: c.fecha_hora.strftime("%Y-%m") == anio_mes, activas)
            )
        meses = map(lambda c: c.fecha_hora.strftime("%Y-%m"), activas)

        def acumular_mes(conteo: dict[str, int], mes: str) -> dict[str, int]:
            nuevo = dict(conteo)
            nuevo[mes] = nuevo.get(mes, 0) + 1
            return nuevo

        return reduce(acumular_mes, meses, {})