# Implementation Plan: Caracterización y Contacto Institucional

- [x] 1. Página de caracterización con CTA de correo y WhatsApp, garantías y coordinación vigente
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Datos de preguntas frecuentes
  - [x] 2.1 Añadir `categoria` a las 12 preguntas de `faq.json`, ordenadas por categoría
  - [x] 2.2 Validación de claves, ids 1–12 y categorías en `validar_json.py`
  - _Requirements: 2.1, 2.2, 2.6_
  - [x] 2.3 Reemplazar `pregunta` y `respuesta` por el texto íntegro del documento fuente oficial (solo correcciones ortográficas evidentes)
  - _Requirements: 2.3_

- [x] 3. Isla `FaqAccordion`
  - [x] 3.1 Interfaz `FaqItem` con `categoria` tipada
  - [x] 3.2 Selector de categoría con opción "Todas" y agrupación por encabezados
  - [x] 3.3 Búsqueda y botones desplegar/colapsar
  - _Requirements: 2.4, 2.5_
  - [x] 3.4 `aria-expanded`, `aria-controls`, `aria-pressed` y foco visible
  - _Requirements: 3.1, 3.2, 3.3_
