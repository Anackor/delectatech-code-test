# Bloque 5 — Dashboard y cierre del pipeline

Leer primero la [guía común](00-arquitectura-y-practicas.md).

## Contrato y diseño

Streamlit presenta resultados persistidos de los bloques 2 y 3. Separar consultas/agregaciones de widgets y presentación. La UI no ejecuta crawls ni recalcula matching o clasificación al cambiar un filtro.

Definir primero el significado de cada KPI. Restaurantes de Just Eat enlazados y locales Google únicos pueden tener recuentos distintos; mostrar etiquetas precisas. La oferta por categoría puede medir apariciones de platos o restaurantes que ofrecen una categoría: escoger y declarar la unidad para evitar conclusiones engañosas por duplicados.

## Pasos

1. Preparar un dataset de integración pequeño con dos restaurantes, varias categorías y un plato repetido entre menús. Calcular manualmente los KPI esperados según la granularidad elegida.
2. Implementar consultas parametrizadas que lean solo resultados vigentes. No mezclar ejecuciones parciales con la última ejecución completa sin indicarlo; usar la política de publicación establecida en los bloques anteriores.
3. Construir Streamlit con número de restaurantes enlazados, principales categorías y al menos una medida de cobertura/calidad. Añadir filtros útiles por restaurante o categoría y aplicar el mismo alcance a métricas y gráficos, salvo etiqueta explícita.
4. Gestionar base vacía, filtros sin resultados y error de conexión con estados distintos. No presentar un fallo SQL como cero restaurantes. Mostrar procedencia o fecha de actualización cuando ayude a interpretar los datos.
5. Si se añade caché, definir cuándo se invalida tras regenerar resultados. Cerrar conexiones por operación o usar recursos con ciclo de vida claro; evitar una conexión global mutable compartida sin necesidad.
6. Añadir Streamlit a `app`, sustituir `sleep infinity` y publicar el puerto local. Implementar `make dashboard` manteniendo únicamente `app` y `db`; conservar comandos CLI por `docker compose exec`.
7. Completar `make pipeline` para ejecutar importación/matching/clasificación en el orden necesario, con fallo de etapa visible. No exigir un crawl en vivo para reconstruir el dashboard con los datos entregados.

## Comprobaciones y cierre

- Comparar KPI y filtros con los valores manuales de la fixture y las consultas SQL.
- Comprobar visualmente el estado sin datos, un filtro con resultados y otro vacío. Automatizar interacción de UI solo si cubre un riesgo concreto; no añadir una suite de navegador por defecto.
- Verificar que una actualización de datos llega al dashboard y que repetir el pipeline no infla métricas.
- Guardar capturas y muestra final en rutas versionables y enlazarlas desde el README.

Para cerrar la entrega, recorrer las instrucciones desde un volumen de pruebas nuevo sin borrar el volumen del usuario: arranque, pruebas, pipeline, POC y dashboard. Documentar dependencias, decisiones, evaluación, fallos conocidos e informe de uso de IA. El evaluador debe poder seguir el README sin depender de estas guías técnicas.
