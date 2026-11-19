"""Patrón Factory para la creación validada de entidades de SisSalud Simbal."""

from __future__ import annotations
from src.modelos import Paciente, ProfesionalSalud


class FabricaEntidades:
    """Fábrica centralizada que valida datos de entrada antes de crear entidades."""

    @staticmethod
    def _validar_campos_persona(
        nombre: str, documento: str, telefono: str, caserio: str
    ) -> None:
        if not nombre or len(nombre.strip()) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres.")
        doc_limpio = documento.strip()
        if not doc_limpio.isdigit() or len(doc_limpio) not in (8, 9):
            raise ValueError("El documento debe contener 8 o 9 dígitos numéricos.")
        tel_limpio = telefono.strip()
        if not tel_limpio.isdigit() or len(tel_limpio) != 9:
            raise ValueError("El teléfono debe contener exactamente 9 dígitos.")
        if not caserio or not caserio.strip():
            raise ValueError("El caserío o sector de procedencia es obligatorio.")

    @classmethod
    def crear_paciente(
        cls,
        id_paciente: str,
        nombre: str,
        documento: str,
        telefono: str,
        caserio: str,
        fecha_registro: str | None = None,
    ) -> Paciente:
        """Crea y valida una instancia de Paciente."""
        if not id_paciente or not id_paciente.strip():
            raise ValueError("El código del paciente es obligatorio.")
        cls._validar_campos_persona(nombre, documento, telefono, caserio)
        return Paciente(
            id_paciente=id_paciente,
            nombre=nombre,
            documento=documento,
            telefono=telefono,
            caserio=caserio,
            fecha_registro=fecha_registro,
        )

    @classmethod
    def crear_profesional(
        cls,
        id_profesional: str,
        nombre: str,
        documento: str,
        telefono: str,
        caserio: str,
        especialidad: str,
        activo: bool = True,
    ) -> ProfesionalSalud:
        """Crea y valida una instancia de ProfesionalSalud."""
        if not id_profesional or not id_profesional.strip():
            raise ValueError("El código del profesional es obligatorio.")
        if not especialidad or not especialidad.strip():
            raise ValueError("La especialidad del profesional es obligatoria.")
        cls._validar_campos_persona(nombre, documento, telefono, caserio)
        return ProfesionalSalud(
            id_profesional=id_profesional,
            nombre=nombre,
            documento=documento,
            telefono=telefono,
            caserio=caserio,
            especialidad=especialidad,
            activo=activo,
        )