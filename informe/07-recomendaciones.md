# 7. Recomendaciones del Ingeniero Informático

Basado en incidentes reales ocurridos durante el desarrollo del proyecto, se presentan las siguientes recomendaciones profesionales para garantizar un desarrollo ético y responsable.

## 7.1 Evento 1: Fallo de Dependencia Tercerizada (bcrypt)

**Problema**: durante las primeras pruebas de autenticación, la librería `passlib` con `bcrypt` fallaba en Windows debido a problemas de compilación de dependencias nativas. Esto bloqueó el desarrollo del módulo de login durante 2 días.

**Solución**: se reemplazó bcrypt por `hashlib.sha256` con salt configurable (`PWD_SALT`), eliminando la dependencia problemática.

**Recomendación**: al iniciar un proyecto, verificar que todas las dependencias críticas funcionen en el sistema operativo objetivo. Preferir bibliotecas en Python puro (sin extensiones C) cuando la portabilidad sea importante. Documentar las dependencias alternativas en caso de fallo.

## 7.2 Evento 2: Token de Simulación Heredado

**Problema**: el código contenía un token de simulación fijo (`simulacion-jwt-token-123`) que permitía acceder como admin sin autenticación real. Este token fue útil durante el desarrollo temprano pero representaba un riesgo de seguridad si se olvidaba en producción.

**Solución**: se mantuvo el token de simulación pero solo para entornos de test. El código verifica que si el token es el de simulación, solo se use en `TestClient`. En producción, el token no funciona porque `JWT_SECRET` es diferente al default.

**Recomendación**: nunca incluir backdoors, tokens fijos o cuentas de administrador por defecto en código que pueda llegar a producción. Usar variables de entorno para diferenciar entornos (desarrollo vs producción). Implementar un pipeline de CI que verifique que no haya secretos hardcodeados antes de hacer deploy.

## 7.3 Evento 3: Trabajador No Veía Productos Globales

**Problema**: al implementar el filtro por sucursal, los trabajadores solo veían los productos creados en su sucursal. Los productos creados por el administrador (con `sucursal_id = NULL`) eran invisibles para ellos, dejando vistas vacías.

**Solución**: se modificaron todos los endpoints de listado para usar `or_(columna.sucursal_id == sid, columna.sucursal_id.is_(None))`, incluyendo registros globales en todos los filtros por sucursal. Esto aplica a admin con filtro y a trabajadores.

**Recomendación**: al diseñar sistemas multi-tenant o multi-sucursal, considerar desde el inicio el modelo de datos para registros "globales" vs "específicos". Una decisión temprana sobre cómo manejar datos compartidos evita refactorizaciones costosas. Documentar claramente la regla de visibilidad de datos en las especificaciones del sistema.

## 7.4 Recomendaciones Generales

1. **Pruebas automatizadas desde el día 1**: los tests permitieron detectar el problema del filtro de sucursal antes de que afectara a usuarios reales. Se recomienda escribir tests simultáneamente con el código de cada funcionalidad.
2. **Mantener la BD liviana**: SQLite es adecuado para PyMEs (< 10 sucursales, < 100k transacciones/mes). Si el sistema escala, migrar a PostgreSQL manteniendo la misma capa ORM (SQLAlchemy lo abstrae).
3. **Capacitación de usuarios**: el sistema asume que los operadores saben qué SKU ingresar. Se recomienda crear una guía rápida de uso y sesión de capacitación de 30 minutos para nuevos trabajadores.
4. **Plan de continuidad**: respaldar periódicamente el archivo `logistica.db`. Un script simple puede copiarlo a un servicio cloud (Google Drive, Dropbox) cada noche.
