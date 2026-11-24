# Análisis de posibles duplicados, URLs no institucionales y datos por verificar

**Destinatario:** Comité de la Red Nacional de Museos Universitarios (RNMU).
**Fuente:** `src/data/museos.json` generado a partir de la base consolidada de octubre de 2026.
**Propósito:** que el comité decida la depuración. Ningún registro se ha eliminado ni fusionado automáticamente.

> Este documento es público. Solo menciona datos institucionales ya publicados en el directorio; no incluye nombres de personas, teléfonos ni correos personales.

## 1. Posibles registros duplicados

| Grupo | IDs | Registros | Evidencia | Decisión sugerida |
|---|---|---|---|---|
| A | 23 y 89 | "Museo de Instrumentos Musicales Alfonso Viña Calderón" y "Colección Alfonso Viña Calderón" (Universidad de Ibagué) | Mismo buzón (`museodeinstrumentos.alfonsovina@unibague.edu.co`), misma tipología, misma ciudad. El id 89 no tiene dirección. | Confirmar si la colección es el mismo museo; si lo es, conservar el 23 y retirar el 89. |
| B | 55, 65 y 90 | "Museo Entomológico", "Laboratorio Entomológico" y "Museo Entomológico UNAB - Universidad Nacional Agronomía Bogotá" (Universidad Nacional de Colombia, Bogotá) | Los tres usan la misma URL (`.../museo-de-entomol%C3%B3gico-unab`); 65 y 90 comparten buzón y tipología "Artrópodos". | Confirmar con la Facultad de Ciencias Agrarias si es una sola colección (UNAB) y consolidar en un registro. |
| C | 8 y 92 | "Museo Arqueológico de Tunja UPTC" y "Parque Museo Arqueológico de Tunja" (UPTC) | Misma URL (`.../redmuseos/muartun/`), misma ciudad y mismo contacto en la base cruda. | Confirmar si el parque y el museo son una sola unidad; si lo son, conservar el 8. |

## 2. Datos de la fuente que requieren verificación

| ID | Registro | Observación |
|---|---|---|
| 48 | "Herbario Nacional Colombiano" en Medellín | El Herbario Nacional Colombiano está en Bogotá (id 56). El id 48 comparte dirección y buzón con el "Herbario Gabriel Gutiérrez Villegas" (id 49). Probable error de nombre o duplicado de 49. |
| 32 | "Panteón de los Próceres de Boyacá" (Universidad del Cauca, Popayán) | El nombre menciona Boyacá, pero el registro es de Popayán. Confirmar el nombre oficial. |
| 21 | Universidad Mariana | La base la registra con naturaleza "Pública". Confirmar la naturaleza jurídica de la institución. |
| 30 | Museo Samoga | La base cruda mezclaba datos de la sede Manizales y de Bogotá (Museo de la Ciencia y el Juego, id 61). El ETL publica Manizales, Caldas. Confirmar que no falte el registro de Bogotá. |
| 24, 85 | Museo Rozo, Museo Mundo del Agua | Sin tipología en la fuente: se publica `null`. |
| 87 | Museo de la Sal Ichi | Entidad aliada (no es IES). Se publica en el directorio pero se cuenta en `totalEntidadesAliadas`. |

## 3. URLs no institucionales

Todas las URLs publicadas empiezan por `http://` o `https://`, pero estas no son el sitio oficial del museo o de la IES:

| ID | Registro | Tipo de URL publicada | Acción sugerida |
|---|---|---|---|
| 3 | Museo de Anatomía (UMNG) | Publicación de Instagram (reel) | Reemplazar por la página del museo en `umng.edu.co`. |
| 88 | Museo de Historia Natural Unillanos | Perfil de Instagram | Reemplazar por una página en `unillanos.edu.co`, si existe. |
| 2 | Museo Nacional de las Telecomunicaciones (UMNG) | Directorio de terceros (museumspedia.net) | Reemplazar por la página oficial. |
| 30 | Museo Samoga (UNAL Manizales) | Directorio de terceros (museumspedia.net) | Reemplazar por la página en `unal.edu.co`. |
| 36 | Museo Geológico UIS | Directorio de terceros (museumspedia.net) | Reemplazar por la página en `uis.edu.co`. |
| 31 | Museo Universidad de Caldas | Artículo de prensa (lapatria.com) | Reemplazar por la página en `ucaldas.edu.co`. |
| 50 | Casa Museo Rafael Uribe Uribe (Universidad Libre) | Directorio de terceros (direccion.com.co) | Reemplazar por la página en `unilibre.edu.co`. |
| 51 | Museo y Archivo Histórico (Externado) | Directorio de terceros (museodata.com) | Reemplazar por la página en `uexternado.edu.co`. |
| 28 | Herbario José Cuatrecasas Arumi (UNAL Palmira) | Colección del repositorio institucional | Valorar si existe una página propia del herbario. |
| 20 | Casa Museo Gabriel García Márquez | Sitio de una fundación externa | Confirmar si es el canal oficial del museo. |
| 4 | Museo de Memoria Institucional (UMNG) | Página de inicio genérica de la universidad | Reemplazar por la página específica del museo. |

## 4. Registros sin correo publicado

En aplicación de la política de correos (`.kiro/steering/data-privacy.md`, sección 3), 26 registros quedan con `correoInstitucional = null`, porque la base solo traía correos personales, cuentas comerciales o correos malformados:

IDs: 1, 5, 6, 24, 25, 29, 36, 44, 46, 52, 53, 55, 59, 61, 68, 70, 71, 72, 78, 79, 84, 85, 86, 87, 92, 93.

**Acción sugerida:** solicitar a cada institución un buzón genérico (p. ej. `museo@…`, `info@…`) y registrarlo en la base cruda. El ETL lo publicará automáticamente. Si es un buzón sin términos institucionales reconocibles, agregarlo a `MAILBOX_ALLOWLIST` en `scripts/rnmu_rules.py` tras revisarlo.

Correos de la fuente con errores que no se corrigieron automáticamente por no poder verificarse:
- id 5: dominio `gmail.uniatlantico.edu.co` (probable error de `mail.uniatlantico.edu.co`).
- id 86: usuario con tilde (`contáctanos@utch.edu.co`); probablemente `contactenos@utch.edu.co`.

Confirmar con cada institución antes de agregar la corrección a `DOMAIN_FIXES` o a la base cruda.
