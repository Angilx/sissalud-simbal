"""Menú interactivo en terminal para SisSalud Simbal (datos de prueba/demostración)."""

from datetime import datetime
from src.fabrica import FabricaEntidades
from src.gestor import GestorClinico
from src.reportes import GeneradorReportes


def pedir_texto(mensaje: str) -> str:
    """Solicita un texto por terminal eliminando espacios extremos."""
    return input(mensaje).strip()


def registrar_paciente_interactivo(gestor: GestorClinico) -> None:
    """Permite ingresar los datos de un paciente desde la terminal."""
    print("\n--- Registrar Paciente ---")
    id_pac = pedir_texto("Código del paciente (ej. PAC-003): ")
    nombre = pedir_texto("Apellidos y nombres: ")
    documento = pedir_texto("Documento de identidad (8 o 9 dígitos): ")
    telefono = pedir_texto("Teléfono (9 dígitos): ")
    caserio = pedir_texto("Caserío o sector (ej. Simbal Centro, Cumbray): ")

    paciente = FabricaEntidades.crear_paciente(
        id_paciente=id_pac,
        nombre=nombre,
        documento=documento,
        telefono=telefono,
        caserio=caserio,
    )
    gestor.registrar_paciente(paciente)
    gestor.guardar_local()
    print(f"Paciente registrado correctamente: {paciente.resumen()}")


def registrar_profesional_interactivo(gestor: GestorClinico) -> None:
    """Permite ingresar los datos de un profesional de salud desde la terminal."""
    print("\n--- Registrar Profesional de Salud ---")
    id_prof = pedir_texto("Código del profesional (ej. PRO-003): ")
    nombre = pedir_texto("Apellidos y nombres: ")
    documento = pedir_texto("Documento de identidad (8 o 9 dígitos): ")
    telefono = pedir_texto("Teléfono (9 dígitos): ")
    caserio = pedir_texto("Caserío o sede (ej. Simbal): ")
    especialidad = pedir_texto("Especialidad (ej. Medicina General, Obstetricia): ")

    profesional = FabricaEntidades.crear_profesional(
        id_profesional=id_prof,
        nombre=nombre,
        documento=documento,
        telefono=telefono,
        caserio=caserio,
        especialidad=especialidad,
    )
    gestor.registrar_profesional(profesional)
    gestor.guardar_local()
    print(f"Profesional registrado correctamente: {profesional.resumen()}")


def buscar_paciente_interactivo(gestor: GestorClinico) -> None:
    """Busca un paciente por documento mostrando solo datos enmascarados."""
    print("\n--- Buscar Paciente ---")
    documento = pedir_texto("Ingrese el documento de identidad a buscar: ")
    paciente = gestor.buscar_paciente_por_doc(documento)
    if paciente is None:
        print("No se encontró ningún paciente con ese documento.")
    else:
        print("Resultado:", paciente.resumen())


def programar_cita_interactiva(gestor: GestorClinico) -> None:
    """Programa una cita validando disponibilidad horaria del profesional."""
    print("\n--- Programar Cita ---")
    id_cita = pedir_texto("Código de cita (ej. CIT-003): ")
    doc_pac = pedir_texto("Documento del paciente: ")
    id_prof = pedir_texto("Código del profesional (ej. PRO-001): ")
    fecha_str = pedir_texto("Fecha y hora (formato AAAA-MM-DD HH:MM, ej. 2026-11-25 09:30): ")
    motivo = pedir_texto("Motivo de consulta: ")

    fecha_hora = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
    cita = gestor.programar_cita(
        id_cita=id_cita,
        documento_paciente=doc_pac,
        id_profesional=id_prof,
        fecha_hora=fecha_hora,
        motivo=motivo,
    )
    gestor.guardar_local()
    print(f"Cita programada: {cita.id_cita} | Estado: {cita.estado} | Fecha: {cita.fecha_hora}")


def cancelar_cita_interactiva(gestor: GestorClinico) -> None:
    """Cancela una cita por su código."""
    print("\n--- Cancelar Cita ---")
    id_cita = pedir_texto("Ingrese el código de la cita a cancelar: ")
    gestor.cancelar_cita(id_cita)
    gestor.guardar_local()
    print(f"Cita {id_cita} cancelada y horario liberado.")


def ver_reportes_interactivo(gestor: GestorClinico) -> None:
    """Muestra reportes por especialidad y por mes excluyendo citas canceladas."""
    print("\n--- Reportes (sin citas canceladas) ---")
    reportes = GeneradorReportes(gestor.citas)
    print("Por especialidad:", reportes.reporte_por_especialidad())
    print("Por mes:", reportes.reporte_por_mes())


def menu_principal() -> None:
    """Ejecuta el bucle principal del menú en terminal."""
    gestor = GestorClinico("datos_simbal.json")
    gestor.cargar_local()

    while True:
        print("\n=== SIS-SALUD SIMBAL (MENÚ CONSOLA) ===")
        print("1. Registrar paciente")
        print("2. Registrar profesional de salud")
        print("3. Buscar paciente por documento")
        print("4. Programar cita")
        print("5. Cancelar cita")
        print("6. Ver reportes por especialidad y mes")
        print("0. Salir")

        opcion = pedir_texto("Elige una opción: ")

        try:
            if opcion == "1":
                registrar_paciente_interactivo(gestor)
            elif opcion == "2":
                registrar_profesional_interactivo(gestor)
            elif opcion == "3":
                buscar_paciente_interactivo(gestor)
            elif opcion == "4":
                programar_cita_interactiva(gestor)
            elif opcion == "5":
                cancelar_cita_interactiva(gestor)
            elif opcion == "6":
                ver_reportes_interactivo(gestor)
            elif opcion == "0":
                gestor.guardar_local()
                print("Datos guardados localmente. ¡Hasta luego!")
                break
            else:
                print("Opción no válida. Intenta nuevamente.")
        except (ValueError, LookupError) as error:
            print(f"[Error de validación/operación]: {error}")


if __name__ == "__main__":
    menu_principal()