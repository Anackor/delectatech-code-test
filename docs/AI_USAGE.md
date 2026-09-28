# Uso de herramientas de IA

Se utilizo un agente de programacion para generar borradores de codigo y documentacion, generar los umbrales y la selección de muestra y asistir en la inspeccion de salidas OCR. Las decisiones de arquitectura y las correcciones no se realizaron con IA.

La documentación se establece con un muy simplificado SDD (últimamente he visto que ampliar la definición técnica con más detalles repercute en el gasto de tokens sin aumentar necesariamente la calidad del entregable).

No se usa ningun modelo de IA, servicio externo ni clave de API durante la ejecucion del proyecto. La POC de imagenes usa Tesseract local dentro del contenedor `app`; la alternativa multimodal descrita en `docs/IMAGE_POC.md` es una propuesta de produccion y no forma parte del codigo ejecutable.
