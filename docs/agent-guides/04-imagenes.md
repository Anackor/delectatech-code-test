# Bloque 4 — Imágenes: enfoque técnico y POC

Leer primero la [guía común](00-arquitectura-y-practicas.md).

## Contrato y diseño

Entrada: una muestra limitada y fija de imágenes identificadas por CID. Salida JSON o CSV con imagen, CID, texto extraído, candidatos a platos, evidencia y estado. El OCR propuesto identifica texto de cartas; su alcance no equivale al reconocimiento visual de cualquier plato fotografiado.

Separar selección/lectura, preparación de imagen, ejecución de Tesseract y conversión de texto a candidatos. La interpretación del texto debe poder probarse sin ejecutar OCR. Los candidatos de esta POC no se incorporan automáticamente a los platos de Just Eat ni a los KPI como datos confirmados.

## Pasos

1. Inspeccionar las imágenes y escoger una muestra pequeña que incluya distintos niveles de legibilidad y un caso sin carta o sin texto útil. Conservar la lista exacta para repetir la evaluación.
2. Leer el directorio ya extraído o el ZIP mediante biblioteca estándar. Si se extrae, limitar rutas al destino previsto, validar tamaños y no volver a descomprimir todo en cada ejecución.
3. Incorporar Pillow, Tesseract y los idiomas `spa`/`eng` a la imagen Docker. Documentar versiones, límites de tamaño y timeout de procesamiento por imagen.
4. Aplicar el preprocesamiento mínimo sustentado por una imagen real: orientación, reducción de resolución o contraste. Preservar el original y registrar parámetros; no construir una cadena extensa de filtros sin medir su utilidad.
5. Ejecutar OCR, separar líneas/candidatos de encabezados, precios y ruido. Conservar el texto que respalda cada candidato y, si están disponibles, sus coordenadas. Una confianza de OCR mide reconocimiento de caracteres, no certeza de que el texto sea un plato.
6. Implementar `make images` con límite de muestra y salida por imagen. Una imagen corrupta debe producir un error identificable y permitir procesar las restantes.
7. Redactar la parte teórica: selección de OCR, límites ante escritura manual/fotos sin texto, evaluación y alternativa de visión para producción, con sus costes y riesgos de inventar contenido. Distinguir diseño propuesto de código implementado.

## Comprobaciones y cierre

- Pruebas de interpretación con texto fijo, precios solos, encabezados y texto vacío.
- Prueba real del OCR dentro de Docker sobre al menos una imagen de la muestra.
- Referencia manual de los platos legibles: contar candidatos correctos, falsos positivos y omisiones con una regla de comparación explicada.
- Registrar tiempo en CPU, tamaño de muestra y resultados no concluyentes. Un JSON vacío para todas las imágenes no demuestra extracción: investigar selección, OCR y parser y reflejar el límite si persiste.

Entregar el informe técnico y una muestra JSON/CSV reproducible. La POC es independiente de que exista matching para todos los CID de las imágenes.
