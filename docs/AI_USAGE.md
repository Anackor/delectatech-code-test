# Uso de herramientas de IA

Se utilizo un agente de programacion para analizar el enunciado, generar borradores de codigo y documentacion, y asistir en la inspeccion de salidas OCR. Las decisiones de arquitectura, los umbrales, la seleccion de muestra y las correcciones se revisaron durante el desarrollo.

No se usa ningun modelo de IA, servicio externo ni clave de API durante la ejecucion del proyecto. La POC de imagenes usa Tesseract local dentro del contenedor `app`; la alternativa multimodal descrita en `docs/IMAGE_POC.md` es una propuesta de produccion y no forma parte del codigo ejecutable.
