# Política Estricta de Privacidad y Habeas Data

## 1. Contexto Legal y Obligaciones
El repositorio del portal de la RNMU es de acceso **PÚBLICO** y abierto a la comunidad universitaria y ciudadana. Conforme a la Ley Estatutaria 1581 de 2012 de Colombia (Habeas Data) y principios éticos de protección de datos:
- **PROHIBICIÓN TOTAL:** NUNCA versionar en git archivos brutos `.xlsx`, `.xls` o `.csv` con datos personales o sensibles. El CI falla si detecta alguno.
- Los archivos en `data-raw/` deben permanecer exclusivamente en el entorno local del operador o gestor de datos.
- Ningún script, log, informe o archivo de `docs/` puede reproducir nombres de personas, teléfonos o correos personales tomados de la base cruda.

## 2. Datos Sensibles Excluidos
Bajo ninguna circunstancia se deben publicar en el frontend los siguientes datos:
1. Teléfonos celulares personales o directos de directores, curadores o delegados.
2. Estado de membresía en el grupo privado de WhatsApp de la Red.
3. Presupuestos monetarios, fuentes financieras privadas o porcentajes internos de gastos.
4. Indicadores de gestión (KPIs) o evaluaciones cualitativas internas.
5. Comentarios de diagnóstico o debilidades reportadas por las instituciones.
6. Nombres de directores, coordinadores, curadores o enlaces, **incluidos los que aparecen dentro de una dirección de correo**.
7. Direcciones de correo personales (Gmail, Hotmail, Yahoo, Outlook, etc.).
8. Registros de autorización de contacto o consentimientos internos.

Los canales oficiales de la Red (`reddemuseosuniversitarios@gmail.com` y la línea de WhatsApp de caracterización) son datos institucionales de la propia Red, no de personas, y sí pueden publicarse.

## 3. Política de Correos (`correoInstitucional`)
Solo se publican **buzones institucionales genéricos del museo o de su unidad** (p. ej. `museo@`, `info@`, `herbario@`, `cultura@`, `proyeccioncultural@`). En cualquier otro caso el valor es `null`.

Un correo queda en `null` si cumple cualquiera de estas condiciones:
1. El dominio es comercial o personal (`gmail`, `hotmail`, `yahoo`, `outlook`, `live`, `icloud`, etc.), incluso si es la cuenta del propio museo.
2. Está malformado o contiene caracteres no ASCII (p. ej. tildes en el usuario).
3. El usuario contiene nombres o apellidos de directores o enlaces registrados en la base cruda (p. ej. `nombre.apellido@`, `inicialapellido@`).
4. No contiene ningún término institucional genérico ni un término propio del nombre del museo, salvo que figure en la lista de buzones revisados manualmente (`MAILBOX_ALLOWLIST`).
5. Tiene forma `nombre.apellido` sin ningún término institucional.

Las reglas viven en `scripts/rnmu_rules.py` y las aplican tanto el ETL como el validador. Solo se corrigen dominios con errores evidentes (`DOMAIN_FIXES`); nunca se inventan buzones.

## 4. Consentimientos Vacíos
La columna de autorización de tratamiento de datos está vacía en una parte de los registros. Tratamiento:
- Un consentimiento vacío **no** se interpreta como autorización.
- Como el portal solo publica datos institucionales (nombre del museo, IES, ubicación, tipología, estado, SIMCO, web y buzón genérico) y ningún dato personal, los registros sin consentimiento se publican sin restricción adicional.
- Si en el futuro se quisiera publicar cualquier dato de una persona, solo podrá hacerse con consentimiento expreso "Sí" registrado en la base y previa actualización de esta política.

## 5. Lista Blanca Estricta para `museos.json`
Solo se permiten las siguientes 12 propiedades:
- `id` (entero único)
- `nombre` (nombre formal del museo o entidad cultural)
- `universidad` (nombre canónico de la IES o entidad aliada a la que pertenece)
- `naturaleza` ("Pública" | "Privada" | "No especificada")
- `departamento` (departamento colombiano sin prefijos numéricos)
- `ciudad` (municipio canónico, coherente con el departamento)
- `direccion` (dirección física o `null`)
- `tipologia` (área temática de la colección o `null`; nunca un texto inventado)
- `estadoAtencion` ("Abierto" | "Cita previa" | "Cerrado temporalmente" | "Cerrado" | "Sin información")
- `registroSimco` ("Sí" | "No" | "En proceso / Por confirmar" | "Sin información")
- `paginaWeb` (URL `http://` o `https://`, o `null`)
- `correoInstitucional` (buzón genérico según la sección 3, o `null`)

### Valor "Sin información" en SIMCO
- Campo vacío, "no sabe", "no responde" o equivalentes → `"Sin información"`.
- "Tal vez", "Posiblemente", "En trámite / proceso" → `"En proceso / Por confirmar"`.
- "Sí" o un año de registro → `"Sí"`; "No" → `"No"`.

## 6. Entidades Aliadas que no son IES
Las entidades que no son Instituciones de Educación Superior (p. ej. "Corporación Museo de la Sal Ichi") se listan en `NON_IES` dentro de `scripts/rnmu_rules.py`. Aparecen en el directorio, pero se cuentan en `totalEntidadesAliadas` y no en `totalUniversidades`.

## 7. Validación Obligatoria
`python scripts/validar_json.py` debe terminar con código 0 antes de cualquier commit que modifique `src/data/`. El ETL lo ejecuta automáticamente y el CI lo ejecuta en cada push a `main`. Con la base cruda disponible localmente, el validador también compara los correos contra los nombres reales de directores y enlaces (solo en memoria; nunca los imprime ni los escribe).
