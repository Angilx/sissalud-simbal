# SisSalud Simbal

Módulo de software libre y local para el registro de pacientes, programación de citas y generación de reportes del **Centro de Salud de Simbal** (Trujillo, La Libertad).

## Estructura del proyecto
- `src/modelos.py`: Clases `Persona`, `Paciente`, `ProfesionalSalud` y `Cita` con protección de datos personales (Ley N.° 29733).
- `src/fabrica.py`: Patrón *Factory* (`FabricaEntidades`) para validación y creación de entidades.
- `src/gestor.py`: Gestión de registros, prevención de cruces de horario y persistencia local en JSON.
- `src/reportes.py`: Reportes mensuales y por especialidad con funciones de orden superior (`filter`, `map`, `reduce`).
- `tests/test_sissalud.py`: Pruebas automatizadas con `pytest`.

## Ejecución
```bash
python main.py
pytest -v
```