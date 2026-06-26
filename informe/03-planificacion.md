# 3. Planificación

## 3.1 Ciclo de Vida del Sistema

Se adoptó un **ciclo de vida iterativo-incremental**, donde cada iteración produce un incremento funcional del sistema. Este enfoque permite obtener retroalimentación temprana y ajustar requisitos sobre la marcha.

| Fase | Descripción |
|------|-------------|
| **Análisis** | Identificación de requisitos funcionales y no funcionales a partir del problema planteado. Definición de actores y casos de uso. |
| **Diseño** | Arquitectura del sistema (FastAPI + SQLAlchemy + SQLite), diseño de la base de datos (Modelo Entidad-Relación), diseño de interfaz (HTML+CSS+JS vanilla, tema oscuro). |
| **Implementación** | Codificación incremental por sprint: cada sprint agrega entre 2 y 4 RF completos. |
| **Pruebas** | Pruebas automatizadas con pytest para cada RF implementado. 42 tests al final del proyecto. |

## 3.2 Metodología de Desarrollo

Se seleccionó una **metodología ágil adaptada (Scrum simplificado)** por las siguientes razones:

- El sistema involucró requisitos que evolucionaron durante el desarrollo (ej: se agregaron RF17, RF20, RF23, RF24 en etapas tardías).
- Se requería retroalimentación continua sobre la usabilidad de la interfaz.
- El equipo era pequeño (4 personas), ideal para ciclos cortos con reuniones sincrónicas mínimas.

**Justificación frente a alternativas:**
- **Cascada**: descartada porque los requisitos no estaban completamente definidos al inicio (ej: el filtro por sucursal con inclusión de registros globales surgió durante pruebas).
- **Prototipado**: usado de forma complementaria para la interfaz de usuario, pero no como metodología principal por la falta de estructura formal.

## 3.3 Planificación Temporal

El proyecto se desarrolló en 7 sprints de 1 semana cada uno:

| Sprint | Período | Entregable |
|--------|---------|------------|
| **Sprint 1** | Semana 1 | RF01-RF04: endpoints de stock (ingreso, salida, POS, alerta), health check. |
| **Sprint 2** | Semana 2 | RF05-RF07: autenticación JWT, roles, CRUD de usuarios y sucursales. |
| **Sprint 3** | Semana 3 | RF08-RF11: datos de proveedor/comprador, filtro por sucursal, dashboard. |
| **Sprint 4** | Semana 4 | RF12-RF16: seed admin, página login, interfaz principal, wizard, protección rutas. |
| **Sprint 5** | Semana 5 | Pruebas de integración, corrección de bugs (filtro con or_ para globales, sucursal en dashboard). |
| **Sprint 6** | Semana 6 | RF17 (transferencias), RF24 (auditoría), RF20 (exportación CSV), RF23 (notificaciones UI). |
| **Sprint 7** | Semana 7 | Documentación (REQUIREMENTS.md, README.md), tests finales (42 tests), preparación del informe. |

### Hitos

| Hito | Fecha | Criterio de éxito |
|------|-------|-------------------|
| MVP funcional | Fin Sprint 3 | CRUD completo de stock + auth + sucursales |
| Sistema completo | Fin Sprint 5 | Todos los RF originales funcionando + tests pasando |
| Versión extendida | Fin Sprint 6 | 4 nuevos RF implementados |
| Entrega | Fin Sprint 7 | Informe, diagramas y presentación |

## 3.4 Herramientas Utilizadas

- **Lenguaje**: Python 3.12
- **Framework web**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy 2.0
- **Base de datos**: SQLite (preparado para PostgreSQL)
- **Autenticación**: JWT (PyJWT, HS256)
- **Frontend**: HTML5 + CSS3 + JavaScript vanilla + Lucide icons
- **Testing**: pytest + httpx
- **Control de versiones**: Git
- **Entorno**: Windows, PowerShell, VS Code
