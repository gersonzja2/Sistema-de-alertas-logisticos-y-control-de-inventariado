# 8. Conclusión

## 8.1 Lecciones Aprendidas

El desarrollo de SALCI permitió aplicar los conceptos teóricos de Análisis y Diseño de Sistemas a un proyecto real y funcional. Las principales lecciones incluyen:

- **Los requisitos evolucionan**: aunque se definieron 16 RF iniciales, la interacción con el sistema reveló la necesidad de 4 RF adicionales (transferencias, exportación CSV, notificaciones UI, auditoría). Una metodología ágil permitió incorporarlos sin afectar el cronograma general.
- **Las pruebas son un multiplicador de calidad**: los 42 tests automatizados detectaron regresiones en múltiples ocasiones, especialmente al modificar el filtro por sucursal. Sin ellos, bugs como la invisibilidad de productos globales habrían llegado a producción.
- **El diseño de BD debe considerar la segmentación desde el inicio**: agregar `sucursal_id` a todas las tablas fue una decisión acertada, pero la inclusión de registros globales (`sucursal_id IS NULL`) requirió ajustes en todos los endpoints. Esta lección se aplicará en futuros proyectos multi-tenant.
- **La ética no es un añadido**: el análisis ético y legal reveló aspectos (protección de datos según Ley 19.628, transparencia en alertas, responsabilidad profesional) que no se habían considerado en la fase de diseño inicial.

## 8.2 Cumplimiento de Objetivos

| Objetivo | Estado | Evidencia |
|----------|--------|-----------|
| Interfaz web responsiva | ✅ | HTML+CSS+JS vanilla, responsive design, mobile-friendly |
| Alertas automáticas | ✅ | Email (Resend) + Webhook + Dashboard, 3 canales de notificación |
| Segmentación por sucursal | ✅ | Roles admin/trabajador, filtro con `or_` para globales |
| Historial auditable | ✅ | 20 campos por transacción, auditoría con created_by |
| Transferencias entre sucursales | ✅ | Endpoint con validaciones y registro contable doble |

Todos los objetivos planteados en la fase inicial fueron cumplidos y validados mediante 42 pruebas automatizadas.

## 8.3 Reflexión sobre el Trabajo Colaborativo

El desarrollo de SALCI demostró la importancia de la colaboración estructurada en un equipo de ingeniería:

- **División de responsabilidades**: un integrante se enfocó en el backend (endpoints, lógica de negocio), otro en el frontend (HTML, CSS, JS), otro en las pruebas, y otro en la documentación e informe. Esta división permitió trabajar en paralelo sin conflictos de código.
- **Comunicación sincrónica**: reuniones diarias de 15 minutos para sincronizar avances y resolver bloqueos. Herramientas: Discord para comunicación, Git para control de versiones.
- **Ejemplo concreto de colaboración**: cuando el filtro por sucursal no incluía productos globales, el integrante de backend identificó el bug, el de frontend confirmó el comportamiento incorrecto en la UI, el de pruebas escribió un test que reproducía el error, y el de documentación actualizó los requisitos. Todo en el mismo día.

La principal dificultad fue la coordinación de horarios entre integrantes con obligaciones laborales y académicas. Se solucionó estableciendo un horario fijo de 20:00 a 21:30 (lunes a jueves) para trabajo sincrónico, y dejando las tareas asincrónicas (redacción, tests) para el fin de semana.
