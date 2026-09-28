# Arquitectura y prácticas comunes

## Límites y dependencias

Aplicar clean architecture a la dirección de las dependencias y a las responsabilidades. No es necesario crear cuatro carpetas o una clase por concepto. Empezar con módulos por ejercicio; separar un módulo cuando mezcle motivos de cambio o impida probar una regla de forma independiente.

| Responsabilidad | Contenido | Dependencias permitidas |
| --- | --- | --- |
| Reglas | Normalización, puntuación, clasificación, interpretación de texto y contratos de resultado | Tipos de datos y utilidades de cálculo; sin red, SQL, navegador, entorno ni UI. |
| Casos de uso | Orden de etapas, validación de resultados, política de errores y límites de transacción | Reglas y operaciones de entrada/salida recibidas explícitamente cuando haga falta sustituirlas. |
| Adaptadores | Playwright, JSON/XLSX, PostgreSQL, OCR y exportadores | Bibliotecas externas y contratos de las reglas/casos de uso. |
| Entrada y composición | CLI, Makefile, Streamlit | Construye dependencias concretas y llama al caso de uso. |

Ejemplo: la función que decide un matching recibe candidatos normalizados y devuelve una decisión con evidencia. Un lector prepara los candidatos y un escritor persiste el resultado. Esa función debe poder probarse sin PostgreSQL. La composición del comando puede conocer ambos adaptadores; las reglas nunca deben importar `app.db` o Streamlit.

Conservar `app/db.py` como punto común de conexión. Añadir un módulo de SQL específico cuando aparezca persistencia; evitar repartir conexiones y sentencias entre algoritmos y widgets. Extraer código compartido solo cuando tenga el mismo significado en varios ejercicios: el matching de restaurantes y el de platos pueden necesitar normalizaciones distintas.

## SOLID aplicado al ejercicio

| Principio | Aplicación comprobable |
| --- | --- |
| Responsabilidad única | Separar obtención de una página, interpretación y escritura. Cambiar un selector no debe alterar el algoritmo de matching. |
| Abierto/cerrado | Representar alias y reglas de categorías como datos cuando facilite añadir ejemplos. Introducir estrategias solo si existen algoritmos distintos que deban convivir. |
| Sustitución | Un sustituto de lector o escritor respeta la misma semántica, errores y formatos. Una fuente incompleta no se presenta como un resultado completo. |
| Segregación de interfaces | Si se necesita un contrato, describir solo las operaciones consumidas: por ejemplo, guardar decisiones, no un repositorio universal con CRUD. |
| Inversión de dependencias | Las reglas reciben datos y los casos de uso reciben las operaciones sustituibles. Una función o un `Protocol` pequeño basta cuando hay una frontera real; no introducir contenedores de inyección. |

Usar funciones para transformaciones y `dataclass` o tipos equivalentes cuando ayuden a expresar un contrato. No añadir herencia, fábricas, servicios genéricos, buses de eventos ni un ORM solo para mostrar patrones. La evidencia de arquitectura es poder cambiar o probar una parte sin rehacer las demás.

## Contratos de datos y persistencia

1. Validar formatos en los límites: tipos, IDs, coordenadas, valores ausentes y jerarquías. Diferenciar ausencia de cero; conservar texto y valores originales cuando se normalicen.
2. Preservar IDs de proveedores como texto, incluido CID de Google. Verificar el orden `[longitud, latitud]` de Just Eat. No usar un nombre comercial como clave ni asumir IDs de plato globalmente únicos.
3. Definir la granularidad antes de crear tablas: restaurante de una fuente, decisión de matching y aparición de un plato en un menú. Inspeccionar repeticiones entre secciones y menús antes de decidir las claves compuestas.
4. Usar claves primarias, foráneas y restricciones para invariantes estables. Parametrizar SQL; mantener importación y lectura separadas de la lógica de negocio.
5. Aplicar transacciones con un límite documentado. Usar operaciones repetibles y una política explícita para resultados obsoletos: un `upsert` por sí solo no elimina categorías o enlaces que ya no son válidos.
6. Versionar cambios de esquema necesarios mediante SQL ordenado o el mecanismo mínimo que el proyecto necesite. Probar una base vacía y la transición desde el esquema anterior; no introducir tablas futuras.
7. Escribir exportaciones completas de forma atómica cuando un fallo pueda dejar un archivo truncado. Registrar entradas, parámetros, versión de reglas y recuentos suficientes para reproducir cada ejecución.

Los precios requieren una representación decimal precisa al calcular o persistir. La exportación del crawler debe seguir el formato y tipos del ejemplo, sin convertir un precio desconocido en cero.

## Errores, recursos y operación

Un registro inválido puede rechazarse conservando ID y motivo; una configuración inválida o una base inaccesible deben hacer fallar el comando. Evitar `except Exception: continue` que oculte errores de programación. Cerrar navegador, imágenes, archivos, cursores y conexiones con gestores de contexto o `finally`.

Definir timeout y, donde tenga sentido, reintentos limitados para fallos transitorios. No reintentar datos inválidos. Los comandos deben emitir un resumen con procesados, correctos, rechazados y duración; salir con código no nulo ante un fallo de etapa. Distinguir éxito parcial de resultado completo. No registrar contraseñas ni respuestas completas innecesarias.

Mantener dos servicios Compose y ejecutar comandos dentro de `app`. `source/` sigue siendo de solo lectura. Las dependencias nuevas deben tener un uso inmediato, versión documentada y verificación en la imagen. Los artefactos necesarios para la entrega se incluirán en una ubicación versionable, por ejemplo `examples/`, porque `output/` está excluido de Git.

## Pruebas y evidencia

- Probar reglas puras con ejemplos pequeños y resultados esperados decididos de forma independiente. Incluir un caso normal y los errores que realmente puedan cambiar la decisión.
- Probar adaptadores mediante fixtures pequeñas; usar el ejemplo de Just Eat como referencia de contrato, sin confundirlo con el HTML de una página.
- Probar PostgreSQL con el servicio real: restricciones, rollback y repetición sin duplicados. Mantener los datos de prueba aislados mediante transacción revertida o un esquema de pruebas, sin vaciar tablas del usuario.
- Mantener las pruebas de red en vivo como comprobación explícita, separada de `make test`. Este debe poder pasar sin acceder a Just Eat, una vez construida la imagen.
- Empezar con `unittest`, ya disponible; añadir herramientas solo cuando reduzcan trabajo real. Hacer explícita la separación de pruebas unitarias e integración cuando crezca la suite.
- Registrar resultados de evaluación sobre una muestra manual fija. Separar ejemplos usados para ajustar reglas de ejemplos usados para evaluar; comunicar tamaño, selección y límites de la muestra. Cobertura y exactitud son métricas distintas.

## Revisión al cerrar el bloque

Comprobar que las reglas se pueden ejecutar sin infraestructura, los contratos y fallos son explícitos, el comando funciona en Docker y las pruebas cubren el riesgo principal. Revisar que no haya duplicación de lógica, dependencias circulares, capas sin función o importaciones con efectos secundarios. Actualizar README y roadmap con lo verificado; documentar limitaciones concretas y conservar una muestra de salida inspeccionable.
