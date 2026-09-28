# Instrucciones para agentes

Antes de implementar un bloque, leer `docs/agent-guides/README.md`, la guía común y la guía de ese bloque. Aplicar también `CONSTITUTION.md`, `docs/ADR-0001-pipeline-local-docker-first.md` y `docs/ROADMAP.md`.

Trabajar únicamente en el bloque solicitado y sus dependencias necesarias. Mantener Docker Compose con dos servicios (`app` y `db`) y ejecutar las comprobaciones dentro de Docker.

Crear un commit únicamente cuando el usuario lo solicite de forma explícita. No interpretar una petición de implementación, validación o publicación previa como autorización para crear commits nuevos.

Al terminar cada tarea, actualizar obligatoriamente `docs/ROADMAP.md` antes de emitir la respuesta final: marcar `[x]` solo las tareas completadas, mantener `[ ]` en las parciales o bloqueadas y anotar qué falta cuando corresponda. Nunca marcar la validación de cierre de un bloque.
