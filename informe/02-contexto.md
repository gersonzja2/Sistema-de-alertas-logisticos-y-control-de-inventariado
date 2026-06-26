# 2. Análisis de Contexto

## 2.1 El Problema

Las PyMEs con múltiples sucursales enfrentan desafíos críticos en la gestión de inventario: desconocimiento del stock real en cada ubicación, demoras en la detección de faltantes, procesos manuales propensos a errores, y ausencia de trazabilidad en las transacciones. Estos problemas generan pérdidas económicas por quiebres de stock, exceso de inventario o vencimientos no detectados.

## 2.2 La Solución Propuesta

SALCI es un sistema web de gestión de inventario multi-sucursal que ofrece:

- **Control de stock en tiempo real**: cada ingreso, salida o venta POS actualiza instantáneamente el inventario.
- **Alertas automáticas de reabastecimiento**: cuando un producto cae bajo su stock mínimo, se notifica vía email (Resend) y webhook.
- **Segmentación por sucursal**: cada trabajador opera exclusivamente sobre los datos de su sucursal, mientras el administrador tiene visión global con filtro por sucursal.
- **Trazabilidad completa**: todas las transacciones quedan registradas con datos del proveedor/comprador, fechas y responsable.
- **Dashboard ejecutivo**: KPIs de rotación, productos críticos y despachos pendientes.
- **Transferencias entre sucursales**: movimiento de stock entre ubicaciones con registro contable doble.

## 2.3 Objetivos

**Objetivo General:**
Desarrollar un sistema de información que permita a PyMEs con múltiples sucursales gestionar su inventario de forma centralizada, automatizada y trazable.

**Objetivos Específicos:**
1. Proveer una interfaz web responsiva accesible desde cualquier dispositivo.
2. Automatizar la detección y notificación de stock crítico.
3. Garantizar la segmentación de datos por sucursal con roles de acceso diferenciados.
4. Mantener un historial completo y auditable de todas las transacciones.
5. Permitir transferencias de stock entre sucursales con registro contable.

## 2.4 Relevancia

En Chile, las PyMEs representan el 98% de las empresas y generan el 65% del empleo. Muchas operan con sucursales múltiples pero carecen de sistemas integrados de inventario, dependiendo de planillas Excel y comunicación telefónica. SALCI aborda esta brecha con una solución de bajo costo (stack open-source, SQLite embebido) y fácil despliegue.
