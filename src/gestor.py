"""Módulo de gestión clínica y persistencia local sin conexión a internet."""

from __future__ import annotations
from datetime import datetime
import json
from pathlib import Path
from src.modelos import Cita, Paciente, ProfesionalSalud


class GestorClinico:
    """Administra pacientes, profesionales, citas sin cruce de horario y almacenamiento local."""

    def __init__(self, ruta_archivo: str | Path = "datos_simbal.json") -> None:
        self._pacientes: dict[str, Paciente] = {}
        self._profesionales: dict[str, ProfesionalSalud] = {}
        self._citas: list[Cita] = []
        self._ruta_archivo = Path(ruta_archivo)

    @property
    def citas(self) -> list[Cita]:
        """Devuelve una copia de la lista de citas registradas."""
        return list(self._citas)

    def registrar_paciente(self, paciente: Paciente) -> None:
        """Registra un paciente verificando que no exista duplicidad."""
        if paciente.id_paciente in self._pacientes:
            raise ValueError(f"Ya existe un paciente con el código {paciente.id_paciente}.")
        self._pacientes[paciente.id_paciente] = paciente

    def registrar_profesional(self, profesional: ProfesionalSalud) -> None:
        """Registra un profesional de salud en el establecimiento."""
        if profesional.id_profesional in self._profesionales:
            raise ValueError(
                f"Ya existe un profesional con el código {profesional.id_profesional}."
            )
        self._profesionales[profesional.id_profesional] = profesional

    def buscar_paciente_por_doc(self, documento: str) -> Paciente | None:
        """Busca un paciente comparando el hash de su documento de identidad."""
        for paciente in self._pacientes.values():
            if paciente.coincide_documento(documento):
                return paciente
        return None

    def programar_cita(
        self,
        id_cita: str,
        documento_paciente: str,
        id_profesional: str,
        fecha_hora: datetime,
        motivo: str,
    ) 
        