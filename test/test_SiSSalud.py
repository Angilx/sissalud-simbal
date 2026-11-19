"""Pruebas unitarias automatizadas con pytest para SisSalud Simbal."""

from datetime import datetime
import pytest
from src.fabrica import FabricaEntidades
from src.gestor import GestorClinico
from src.reportes import GeneradorReportes


def _preparar_gestor(tmp_path) -> tuple[GestorClinico, dict[str, str]]:
    """Crea un gestor vacío y registra entidades genéricas de prueba."""
    gestor = GestorClinico(tmp_path / "prueba_local.json")
    datos = {
        "doc_1": "70000001",
        "tel_1": "900000001",
        "doc_2": "70000002",
        "tel_2": "900000002",
        "doc_prof": "40000001",
        "tel_prof": "900000003",
        "id_prof": "PRO-TEST-1",
        "esp_1": "Especialidad A",
    }
    pac1 = FabricaEntidades.crear_paciente(
        "PAC-TEST-1", "Registro Prueba Uno", datos["doc_1"], datos["tel_1"], "Sector Uno"
    )
    pac2 = FabricaEntidades.crear_paciente(
        "PAC-TEST-2", "Registro Prueba Dos", datos["doc_2"], datos["tel_2"], "Sector Dos"
    )
    prof = FabricaEntidades.crear_profesional(
        datos["id_prof"],
        "Registro Profesional Uno",
        datos["doc_prof"],
        datos["tel_prof"],
        "Sede Local",
        datos["esp_1"],
    )
    gestor.registrar_paciente(pac1)
    gestor.registrar_paciente(pac2)
    gestor.registrar_profesional(prof)
    return gestor, datos


def test_rf1_registro_y_busqueda_protegida(tmp_path):
    gestor, datos = _preparar_gestor(tmp_path)
    encontrado = gestor.buscar_paciente_por_doc(datos["doc_1"])
    assert encontrado is not None
    assert encontrado.obtener_documento_enmascarado() == "****0001"
    assert encontrado.obtener_telefono_enmascarado() == "*****0001"


def test_rf2_evita_cruce_de_horario_y_libera_al_cancelar(tmp_path):
    gestor, datos = _preparar_gestor(tmp_path)
    hora = datetime(2026, 11, 21, 10, 30)
    gestor.programar_cita("CIT-1", datos["doc_1"], datos["id_prof"], hora, "Motivo prueba")

    with pytest.raises(ValueError):
        gestor.programar_cita("CIT-2", datos["doc_2"], datos["id_prof"], hora, "Motivo prueba")

    gestor.cancelar_cita("CIT-1")
    cita_reprogramada = gestor.programar_cita(
        "CIT-3", datos["doc_2"], datos["id_prof"], hora, "Motivo prueba"
    )
    assert cita_reprogramada.id_cita == "CIT-3"


def test_rf3_reportes_excluyen_canceladas(tmp_path):
    gestor, datos = _preparar_gestor(tmp_path)
    gestor.programar_cita(
        "CIT-1", datos["doc_1"], datos["id_prof"], datetime(2026, 11, 5, 8, 0), "Consulta"
    )
    gestor.programar_cita(
        "CIT-2", datos["doc_2"], datos["id_prof"], datetime(2026, 11, 6, 9, 0), "Consulta"
    )
    gestor.cancelar_cita("CIT-2")

    reportes = GeneradorReportes(gestor.citas)
    assert reportes.reporte_por_especialidad() == {datos["esp_1"]: 1}
    assert reportes.reporte_por_mes("2026-11") == {"2026-11": 1}


def test_rnf1_y_rnf2_persistencia_sin_texto_plano(tmp_path):
    archivo = tmp_path / "persistencia_test.json"
    gestor, datos = _preparar_gestor(tmp_path)
    gestor._ruta_archivo = archivo
    gestor.guardar_local()

    contenido_json = archivo.read_text(encoding="utf-8")
    assert datos["doc_1"] not in contenido_json
    assert datos["tel_1"] not in contenido_json

    gestor_recargado = GestorClinico(archivo)
    gestor_recargado.cargar_local()
    assert gestor_recargado.buscar_paciente_por_doc(datos["doc_1"]) is not None