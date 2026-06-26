# Presentación SALCI — 20 minutos

## Distribución del tiempo (5 min por integrante)

| Integrante | Slides | Tiempo | Tema |
|------------|--------|--------|------|
| **A** | 1, 2, 3 | 5 min | Introducción, Contexto, Objetivos |
| **B** | 4, 5 | 5 min | Planificación, Metodología, Requisitos |
| **C** | 6, 7 | 5 min | Diseño, Funcionalidades clave, Demo |
| **D** | 8, 9, 10 | 5 min | Ética, Recomendaciones, Conclusiones |

---

## Slide 1 — Portada (30s)
**A**
- Título: Sistema de Alertas Logísticas y Control de Inventario
- Curso: Análisis y Diseño de Sistemas
- Fecha: Junio 2026
- Integrantes: [Nombre1, Nombre2, Nombre3, Nombre4]

## Slide 2 — Problema y Contexto (2 min)
**A**
- PyMEs multi-sucursal: sin control de stock en tiempo real
- Consecuencias: quiebres de stock, pérdidas, procesos manuales
- Foto/diagrama de contexto: 3 sucursales conectadas a un sistema central

## Slide 3 — Solución Propuesta (2.5 min)
**A**
- SALCI: plataforma web de gestión de inventario
- Características principales (6 íconos): stock en vivo, alertas, multi-sucursal, dashboard, trazabilidad, transferencias
- Stack tecnológico: Python + FastAPI + SQLite + JS vanilla

## Slide 4 — Planificación y Metodología (2.5 min)
**B**
- Ciclo de vida: iterativo-incremental
- Metodología: Scrum adaptado (7 sprints de 1 semana)
- Mostrar tabla de sprints (semana 1→7 con hitos)

## Slide 5 — Requisitos (2.5 min)
**B**
- 3 actores: Admin, Trabajador, Sistema
- 20 RF, 8 RNF
- Mostrar tabla resumida de RF (solo IDs y nombres, no descripciones largas)
- Destacar: 42 tests automatizados

## Slide 6 — Diseño de la Solución (2.5 min)
**C**
- Arquitectura 3 capas: Cliente → Servidor → BD
- Diagrama de arquitectura (simple)
- 5 funcionalidades clave: login, ingreso, salida/POS, dashboard, transferencias

## Slide 7 — Demostración en Vivo (2.5 min)
**C**
- **NO es slide, es demo** — abrir navegador y mostrar:
  1. Login como admin
  2. Dashboard con KPIs
  3. Ingreso de producto con lote
  4. Venta POS que dispara alerta de stock bajo
  5. Transferencia entre sucursales
  6. Badge de notificaciones actualizado

## Slide 8 — Análisis Ético y Legal (2.5 min)
**D**
- Privacidad: Ley 19.628 Chile (datos personales)
- Transparencia: trazabilidad completa (created_by, historial)
- No discriminación: mismo sistema para todas las sucursales
- Sin IA: todas las decisiones son deterministas

## Slide 9 — Recomendaciones (1.5 min)
**D**
- 3 eventos reales: bcrypt, token simulación, filtro globales
- Lección: probar dependencias temprano, no hardcodear secretos, diseñar segmentación desde el inicio

## Slide 10 — Conclusiones (1 min)
**D**
- Objetivos cumplidos: 20/20 RF implementados, 42 tests
- Lecciones: requisitos evolucionan, tests salvan, ética importa
- Cierre: agradecimientos, ¿preguntas?

---

## Consejos para la presentación

- **Todos participan**: respetar los tiempos asignados (5 min c/u).
- **Demo**: tener el servidor local funcionando y el navegador listo con pestañas abiertas (login, dashboard, stock).
- **No leer diapositivas**: usar las slides como apoyo visual, hablar naturalmente.
- **Preparar respuestas**: posibles preguntas — "¿por qué SQLite y no PostgreSQL?", "¿cómo manejan la concurrencia?", "¿qué pasa si el servidor se cae?".
- **Vestimenta**: formal o semi-formal (depende de la exigencia del profesor).
