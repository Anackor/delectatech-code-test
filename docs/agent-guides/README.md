# Guías técnicas locales para los agentes

## Propósito y lectura

El ejercicio debe demostrar decisiones de arquitectura y buenas prácticas mediante código comprensible, contratos claros y pruebas útiles. Estas guías convierten el ADR en pasos de implementación.

Leer primero el [ADR](../ADR-0001-pipeline-local-docker-first.md), la [constitución](../../CONSTITUTION.md), el [roadmap](../ROADMAP.md) y la [guía común](00-arquitectura-y-practicas.md). Después leer el bloque solicitado:

| Bloque | Guía | Resultado que debe poder demostrarse |
| --- | --- | --- |
| 1 | [Crawler](01-crawler.md) | Una URL produce el JSON del ejemplo y los fallos se reconocen. |
| 2 | [Matching](02-matching.md) | Enlaces explicables, estados de ambigüedad y persistencia repetible. |
| 3 | [Clasificación](03-clasificacion.md) | Platos enlazados a categorías válidas con evidencias y cobertura conocida. |
| 4 | [Imágenes](04-imagenes.md) | POC en CPU con candidatos trazables, evaluación y límites. |
| 5 | [Dashboard](05-dashboard.md) | Métricas verificables e interacción sobre los resultados de PostgreSQL. |

El bloque 0 ya tiene Compose, Makefile, conexión a PostgreSQL y una prueba de integración. Las dependencias de cada ejercicio se incorporan a la imagen `app` cuando se necesitan. El bloque 5 ejecuta Streamlit en `app`.

## Forma de ejecutar un bloque

1. Inspeccionar código, datos y pruebas existentes; confirmar entradas, salidas y criterio de finalización.
2. Escribir el contrato mínimo y escoger un ejemplo representativo antes de implementar.
3. Completar una ejecución pequeña de extremo a extremo: entrada, regla, resultado y evidencia.
4. Añadir los casos de error relevantes y las comprobaciones indicadas en la guía.
5. Ejecutar en Docker con el volumen de datos del tamaño necesario para comprobar la solución.
6. Actualizar README, roadmap y registro de uso de IA con lo realmente realizado.
7. Entregar una explicación breve de la decisión, su evidencia y sus límites. Las propuestas futuras deben distinguirse de las funciones implementadas.

Si una guía entra en conflicto con el enunciado o con una instrucción posterior del usuario, prevalecen estos últimos. Si una decisión requiere modificar el ADR, documentar el cambio concreto. No convertir la revisión de decisiones en una solicitud de aprobación para elecciones rutinarias ya autorizadas.

Mantener el README de entrega centrado en la ejecución. Las decisiones necesarias para el evaluador deben aparecer también en el ADR o README.
