# Implementation Plan: Directorio Interactivo de Museos

- [x] 1. Pipeline de datos del directorio
  - [x] 1.1 Reglas compartidas en `scripts/rnmu_rules.py` (lista blanca, catálogos, política de correos, NON_IES, ciudad → departamento)
  - [x] 1.2 ETL `scripts/limpiar_base.py` con unificación canónica de universidades, corrección de ciudad contra departamento, limpieza de `\n` literales, diccionario de erratas y `tipologia = null` cuando falta
  - [x] 1.3 Validador `scripts/validar_json.py` integrado al final del ETL y en el CI
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 2. Isla React `DirectorioMuseos`
  - [x] 2.1 Interfaz `Museo` con `tipologia: string | null` y SIMCO con "Sin información"
  - [x] 2.2 Búsqueda tolerante a `tipologia = null`
  - _Requirements: 1.1, 1.2, 1.3_
  - [x] 2.3 Filtros de departamento, naturaleza, estado (5 valores) y SIMCO (4 valores)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  - [x] 2.4 Componente `EstadoBadge`; punto verde solo para "Abierto"
  - _Requirements: 3.1, 3.2, 3.3_
  - [x] 2.5 Enlaces web y `mailto:` condicionados a valores no nulos
  - _Requirements: 3.4, 3.5_
  - [x] 2.6 Alternancia Vista de Cuadrícula / Vista de Tabla
  - _Requirements: 3.6_
  - [x] 2.7 Estado vacío y paginación de 12 elementos
  - _Requirements: 4.1, 4.2_

- [x] 3. Integración en la página y en la portada
  - [x] 3.1 `src/pages/directorio.astro` con aviso de Habeas Data
  - [x] 3.2 Portada sin cifras escritas a mano: totales leídos de `stats.json`
  - _Requirements: 2.1_

- [ ] 4. Pendientes de datos (decisión del comité de la Red)
  - [ ] 4.1 Resolver posibles duplicados listados en `docs/analisis_duplicados_y_urls.md`
  - [ ] 4.2 Reemplazar URLs no institucionales por las oficiales
  - [ ] 4.3 Obtener buzones genéricos para los registros con `correoInstitucional = null`
