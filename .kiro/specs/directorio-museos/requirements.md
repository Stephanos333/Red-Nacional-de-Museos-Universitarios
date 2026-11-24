# Requirements Document: Directorio Interactivo de Museos

## Introduction

El directorio permite a estudiantes, investigadores, directores museales y público general explorar, filtrar y consultar los museos y colecciones universitarias registrados por la RNMU. Los datos provienen de `src/data/museos.json`, generado por el ETL (`scripts/limpiar_base.py`) y verificado por `scripts/validar_json.py`. El directorio solo muestra datos institucionales permitidos por `.kiro/steering/data-privacy.md`.

## Requirements

### Requirement 1: Búsqueda en tiempo real

**User Story:** Como visitante, quiero buscar museos por texto, para encontrar rápidamente una colección concreta.

#### Acceptance Criteria

1. WHEN el usuario escribe en el campo de búsqueda THEN el sistema SHALL filtrar los museos cuyo nombre, universidad, ciudad o tipología contengan el texto, sin distinguir mayúsculas.
2. WHEN un museo tiene `tipologia = null` THEN el sistema SHALL tratarlo como texto vacío en la búsqueda sin generar errores.
3. WHEN el usuario borra la búsqueda THEN el sistema SHALL mostrar de nuevo todos los museos que cumplan los demás filtros.

### Requirement 2: Filtros por facetas

**User Story:** Como investigador, quiero combinar filtros, para analizar subconjuntos del ecosistema museal.

#### Acceptance Criteria

1. THE sistema SHALL ofrecer un filtro por departamento con el conteo de museos de cada uno, calculado a partir de los datos.
2. THE sistema SHALL ofrecer un filtro por naturaleza jurídica (Pública, Privada).
3. THE sistema SHALL ofrecer un filtro por estado de atención con todos los valores del catálogo: Abierto, Cita previa, Cerrado temporalmente, Cerrado y Sin información.
4. THE sistema SHALL ofrecer un filtro por registro SIMCO con todos los valores del catálogo: Sí, En proceso / Por confirmar, No y Sin información.
5. WHEN se cambia cualquier filtro THEN el sistema SHALL volver a la página 1 de resultados.
6. WHEN hay filtros activos THEN el sistema SHALL mostrar un botón "Limpiar filtros" que los restablezca.

### Requirement 3: Tarjetas y tabla de museos

**User Story:** Como visitante, quiero ver la información clave de cada museo, para decidir si visitarlo o contactarlo.

#### Acceptance Criteria

1. THE sistema SHALL mostrar nombre, universidad, ciudad, departamento, dirección (si existe) y tipología (o "Sin información" si es `null`).
2. THE sistema SHALL mostrar una insignia de estado para cada valor del catálogo; solo el estado "Abierto" SHALL llevar el punto verde de actividad.
3. WHEN `registroSimco = "Sí"` THEN el sistema SHALL mostrar la insignia "SIMCO ✓".
4. WHEN existe `paginaWeb` THEN el sistema SHALL enlazarla con `target="_blank"` y `rel="noopener noreferrer"`.
5. WHEN existe `correoInstitucional` THEN el sistema SHALL ofrecer un enlace `mailto:`; WHEN es `null` THEN no SHALL mostrar ningún correo.
6. THE sistema SHALL permitir alternar entre vista de cuadrícula y vista de tabla.

### Requirement 4: Estado vacío y paginación

**User Story:** Como visitante, quiero saber cuándo no hay resultados y navegar listas largas, para no perderme.

#### Acceptance Criteria

1. WHEN ningún museo cumple los criterios THEN el sistema SHALL mostrar un mensaje claro y un botón para ver todos los museos.
2. THE sistema SHALL paginar los resultados de 12 en 12 con controles Anterior/Siguiente.

### Requirement 5: Privacidad

**User Story:** Como coordinación de la Red, quiero que el directorio cumpla la Ley 1581 de 2012, para proteger a las personas de contacto.

#### Acceptance Criteria

1. THE sistema SHALL consumir únicamente los 12 campos de la lista blanca de `museos.json`.
2. THE sistema SHALL NOT mostrar nombres de personas, teléfonos ni correos personales.
3. WHEN `validar_json.py` detecta un incumplimiento THEN el CI SHALL fallar antes del build.
