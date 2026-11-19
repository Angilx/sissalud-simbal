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
    ) -> Cita:
        """Programa una cita verificando existencia de actores y ausencia de cruces horarios."""
        if any(c.id_cita == id_cita for c in self._citas):
            raise ValueError(f"Ya existe una cita registrada con el código {id_cita}.")

        paciente = self.buscar_paciente_por_doc(documento_paciente)
        if paciente is None:
            raise LookupError("No se encontró ningún paciente con ese documento.")

        profesional = self._profesionales.get(id_profesional)
        if profesional is None or not profesional.activo:
            raise LookupError("Profesional no encontrado o inactivo.")

        # Validación RF2: un profesional no puede tener dos citas activas a la misma hora
        cruce = any(
            cita.es_activa()
            and cita.profesional.id_profesional == id_profesional
            and cita.fecha_hora == fecha_hora
            for cita in self._citas
        )
        if cruce:
            raise ValueError(
                f"Cruce de horario: {profesional.nombre} ya tiene una cita activa en {fecha_hora}."
            )

        nueva_cita = Cita(
            id_cita=id_cita,
            paciente=paciente,
            profesional=profesional,
            fecha_hora=fecha_hora,
            motivo=motivo,
        )
        self._citas.append(nueva_cita)
        return nueva_cita

    def cancelar_cita(self, id_cita: str) -> None:
        """Cancela una cita existente liberando el horario del profesional."""
        for cita in self._citas:
            if cita.id_cita == id_cita:
                cita.cancelar()
                return
        raise LookupError(f"No se encontró la cita con código {id_cita}.")

    def guardar_local(self) -> None:
        """Guarda pacientes, profesionales y citas en un archivo JSON local."""
        estructura = {
            "pacientes": [p.a_diccionario() for p in self._pacientes.values()],
            "profesionales": [pr.a_diccionario() for pr in self._profesionales.values()],
            "citas": [c.a_diccionario() for c in self._citas],
        }
        self._ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        self._ruta_archivo.write_text(
            json.dumps(estructura, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def cargar_local(self) -> None:
        """Carga los registros desde el archivo JSON local si existe."""
        if not self._ruta_archivo.exists():
            return
        contenido = json.loads(self._ruta_archivo.read_text(encoding="utf-8"))
        self._pacientes = {
            item["id_paciente"]: Paciente.desde_diccionario(item)
            for item in contenido.get("pacientes", [])
        }
        self._profesionales = {
            item["id_profesional"]: ProfesionalSalud.desde_diccionario(item)
            for item in contenido.get("profesionales", [])
        }
        self._citas = []
        for item in contenido.get("citas", []):
            paciente = self._pacientes[item["id_paciente"]]
            profesional = self._profesionales[item["id_profesional"]]
            self._citas.append(
                Cita(
                    id_cita=item["id_cita"],
                    paciente=paciente,
                    profesional=profesional,
                    fecha_hora=datetime.fromisoformat(item["fecha_hora"]),
                    motivo=item["motivo"],
                    estado=item["estado"],
                )
            )
        