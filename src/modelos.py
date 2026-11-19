"""Módulo de modelos de dominio y protección de datos personales (Ley N.° 29733)."""

from __future__ import annotations
from datetime import datetime
import hashlib
import secrets


def generar_hash_seguro(valor: str, salt: str) -> str:
    """Genera una huella criptográfica SHA-256 usando un salt local."""
    contenido = f"{salt}:{valor.strip()}".encode("utf-8")
    return hashlib.sha256(contenido).hexdigest()


class Persona:
    """Clase base para personas del sistema con resguardo de datos sensibles."""

    def __init__(
        self,
        nombre: str,
        documento: str,
        telefono: str,
        caserio: str,
        salt: str | None = None,
    ) -> None:
        self.nombre = nombre.strip()
        self.caserio = caserio.strip()
        self._salt = salt or secrets.token_hex(8)
        self._hash_documento = generar_hash_seguro(documento, self._salt)
        self._ultimos4_documento = documento.strip()[-4:]
        self._hash_telefono = generar_hash_seguro(telefono, self._salt)
        self._ultimos4_telefono = telefono.strip()[-4:]

    def obtener_documento_enmascarado(self) -> str:
        """Devuelve el documento mostrando únicamente sus últimos cuatro dígitos."""
        return f"****{self._ultimos4_documento}"

    def obtener_telefono_enmascarado(self) -> str:
        """Devuelve el teléfono mostrando únicamente sus últimos cuatro dígitos."""
        return f"*****{self._ultimos4_telefono}"

    def coincide_documento(self, valor: str) -> bool:
        """Verifica si un documento ingresado coincide con la huella almacenada."""
        return generar_hash_seguro(valor, self._salt) == self._hash_documento

    def exportar_seguro(self) -> dict:
        """Serializa los datos de la persona sin exponer documento ni teléfono en claro."""
        return {
            "nombre": self.nombre,
            "caserio": self.caserio,
            "salt": self._salt,
            "hash_documento": self._hash_documento,
            "ultimos4_documento": self._ultimos4_documento,
            "hash_telefono": self._hash_telefono,
            "ultimos4_telefono": self._ultimos4_telefono,
        }


class Paciente(Persona):
    """Representa a un paciente registrado en el Centro de Salud de Simbal."""

    def __init__(
        self,
        id_paciente: str,
        nombre: str,
        documento: str,
        telefono: str,
        caserio: str,
        fecha_registro: str | None = None,
        salt: str | None = None,
    ) -> None:
        super().__init__(nombre, documento, telefono, caserio, salt=salt)
        self.id_paciente = id_paciente.strip()
        self.fecha_registro = fecha_registro or datetime.now().strftime("%Y-%m-%d")

    def resumen(self) -> dict:
        """Devuelve un resumen seguro para consulta en pantalla o reportes."""
        return {
            "id_paciente": self.id_paciente,
            "nombre": self.nombre,
            "documento": self.obtener_documento_enmascarado(),
            "telefono": self.obtener_telefono_enmascarado(),
            "caserio": self.caserio,
            "fecha_registro": self.fecha_registro,
        }

    def a_diccionario(self) -> dict:
        """Convierte el paciente a diccionario para almacenamiento local JSON."""
        datos = self.exportar_seguro()
        datos.update(
            {
                "id_paciente": self.id_paciente,
                "fecha_registro": self.fecha_registro,
            }
        )
        return datos

    @classmethod
    def desde_diccionario(cls, datos: dict) -> Paciente:
        """Reconstruye un paciente desde almacenamiento local sin perder sus hashes."""
        instancia = cls.__new__(cls)
        instancia.nombre = datos["nombre"]
        instancia.caserio = datos["caserio"]
        instancia._salt = datos["salt"]
        instancia._hash_documento = datos["hash_documento"]
        instancia._ultimos4_documento = datos["ultimos4_documento"]
        instancia._hash_telefono = datos["hash_telefono"]
        instancia._ultimos4_telefono = datos["ultimos4_telefono"]
        instancia.id_paciente = datos["id_paciente"]
        instancia.fecha_registro = datos["fecha_registro"]
        return instancia


class ProfesionalSalud(Persona):
    """Representa a un profesional de salud que brinda atenciones en el establecimiento."""

    def __init__(
        self,
        id_profesional: str,
        nombre: str,
        documento: str,
        telefono: str,
        caserio: str,
        especialidad: str,
        activo: bool = True,
        salt: str | None = None,
    ) -> None:
        super().__init__(nombre, documento, telefono, caserio, salt=salt)
        self.id_profesional = id_profesional.strip()
        self.especialidad = especialidad.strip()
        self.activo = activo

    def resumen(self) -> dict:
        """Devuelve un resumen seguro del profesional de salud."""
        return {
            "id_profesional": self.id_profesional,
            "nombre": self.nombre,
            "especialidad": self.especialidad,
            "documento": self.obtener_documento_enmascarado(),
            "activo": self.activo,
        }

    def a_diccionario(self) -> dict:
        """Convierte el profesional a diccionario para almacenamiento local JSON."""
        datos = self.exportar_seguro()
        datos.update(
            {
                "id_profesional": self.id_profesional,
                "especialidad": self.especialidad,
                "activo": self.activo,
            }
        )
        return datos

    @classmethod
    def desde_diccionario(cls, datos: dict) -> ProfesionalSalud:
        """Reconstruye un profesional de salud desde almacenamiento local."""
        instancia = cls.__new__(cls)
        instancia.nombre = datos["nombre"]
        instancia.caserio = datos["caserio"]
        instancia._salt = datos["salt"]
        instancia._hash_documento = datos["hash_documento"]
        instancia._ultimos4_documento = datos["ultimos4_documento"]
        instancia._hash_telefono = datos["hash_telefono"]
        instancia._ultimos4_telefono = datos["ultimos4_telefono"]
        instancia.id_profesional = datos["id_profesional"]
        instancia.especialidad = datos["especialidad"]
        instancia.activo = datos["activo"]
        return instancia


class Cita:
    """Representa una cita médica programada entre un paciente y un profesional."""

    ESTADOS_VALIDOS = ("PROGRAMADA", "ATENDIDA", "CANCELADA")

    def __init__(
        self,
        id_cita: str,
        paciente: Paciente,
        profesional: ProfesionalSalud,
        fecha_hora: datetime,
        motivo: str,
        estado: str = "PROGRAMADA",
    ) -> None:
        if estado not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado de cita inválido: {estado}")
        self.id_cita = id_cita.strip()
        self.paciente = paciente
        self.profesional = profesional
        self.fecha_hora = fecha_hora
        self.motivo = motivo.strip()
        self.estado = estado

    def cancelar(self) -> None:
        """Cambia el estado de la cita a CANCELADA."""
        if self.estado == "ATENDIDA":
            raise ValueError("No se puede cancelar una cita que ya fue atendida.")
        self.estado = "CANCELADA"

    def marcar_atendida(self) -> None:
        """Cambia el estado de la cita a ATENDIDA."""
        if self.estado == "CANCELADA":
            raise ValueError("No se puede atender una cita cancelada.")
        self.estado = "ATENDIDA"

    def es_activa(self) -> bool:
        """Indica si la cita ocupa horario y cuenta en los reportes (no cancelada)."""
        return self.estado != "CANCELADA"

    def a_diccionario(self) -> dict:
        """Serializa la cita referenciando identificadores de paciente y profesional."""
        return {
            "id_cita": self.id_cita,
            "id_paciente": self.paciente.id_paciente,
            "id_profesional": self.profesional.id_profesional,
            "fecha_hora": self.fecha_hora.isoformat(),
            "motivo": self.motivo,
            "estado": self.estado,
        }