#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script ETL para la Red Nacional de Museos Universitarios (RNMU).
Transforma la base consolidada cruda (data-raw/, ignorada por git) en los
archivos JSON públicos y sanitizados de src/data/.

REGLA CRÍTICA DE PRIVACIDAD Y HABEAS DATA (Ley 1581 de 2012):
El repositorio es público. Solo se exportan los 12 campos de la lista blanca.
Los correos solo se publican si son buzones institucionales genéricos del
museo; cualquier correo que identifique a una persona queda en null.

Uso:
    python scripts/limpiar_base.py

Al terminar ejecuta las mismas validaciones de scripts/validar_json.py sobre
los datos generados y sale con código 1 si alguna falla (no escribe archivos
inválidos).
"""

import sys

sys.dont_write_bytecode = True

import csv
import json
import re
from collections import Counter
from pathlib import Path

import rnmu_rules as R
import validar_json

# ---------------------------------------------------------------------------
# Normalización de texto
# ---------------------------------------------------------------------------
TITLECASE_EXCEPTIONS_LOWER = {
    "de", "del", "la", "las", "el", "los", "y", "e", "en", "a", "al", "por", "para", "con", "o", "u",
    "como",
}

TITLECASE_EXCEPTIONS_UPPER = {
    "UPTC", "UIS", "UNAL", "ITM", "UNIMINUTO", "UDES", "UNAB", "UAO", "UNAD", "MHNUD-M", "MUA",
    "CRAI", "BIC", "IMUC", "RNC", "SIMCO", "RNMU", "D.C.", "DC", "MUUA", "MUNAD", "MAPUKA",
}

# Correcciones de palabras sin tilde o con erratas de la fuente.
# Se aplican sobre nombre y tipología respetando mayúscula inicial.
WORD_FIXES = {
    "gárcia": "garcía", "garcia": "garcía", "santnader": "santander",
    "intitucional": "institucional", "ingienería": "ingeniería", "ingieneria": "ingeniería",
    "marinkellel": "marinkelle", "garcës": "garcés", "layva": "leyva", "moniquirá": "monquirá",
    "arqueologíco": "arqueológico", "medellïn": "medellín", "gaitan": "gaitán",
    "eliecer": "eliécer", "clinica": "clínica", "gutierrez": "gutiérrez", "calderon": "calderón",
    "agustin": "agustín", "entomologico": "entomológico", "pedagogico": "pedagógico",
    "contemporaneo": "contemporáneo", "historico": "histórico", "historicos": "históricos",
    "historicas": "históricas", "jose": "josé", "plasticas": "plásticas", "ceramica": "cerámica",
    "litico": "lítico", "biologia": "biología", "biologica": "biológica",
    "biologicas": "biológicas", "entomologia": "entomología", "ecologia": "ecología",
    "etnografia": "etnografía", "etnograficas": "etnográficas", "geologicas": "geológicas",
    "paleontologicas": "paleontológicas", "paleontólogica": "paleontológica",
    "antropologicas": "antropológicas", "artistico": "artístico",
    "blibliografíco": "bibliográfico", "fotografias": "fotografías", "navegacion": "navegación",
    "astronomia": "astronomía", "astronomicas": "astronómicas", "astronomico": "astronómico",
    "medicas": "médicas", "musica": "música", "convencion": "convención",
    "benjamin": "benjamín", "coleccion": "colección",
}

# Correcciones de frase (se aplican después del title-case y de WORD_FIXES).
PHRASE_FIXES = {
    "C.j.": "C. J.",
    "Museo de la Historia Natural C. J.": "Museo de Historia Natural C. J.",
    "Museo de la Ciencias y Juego": "Museo de la Ciencia y el Juego",
    "Museo de Ciencia Natural de la Salle": "Museo de Ciencias Naturales de La Salle",
    "Parque Museo Arqueológico de Monquirá Villa de Leyva": "Parque Museo Arqueológico de Monquirá, Villa de Leyva",
    "Laboratorio Entomologico": "Laboratorio Entomológico",
    "Museo de la Salle": "Museo de La Salle",
    "Universidad del Bosque": "Universidad El Bosque",
}

DIRECCION_FIXES = {
    "Tunjal": "Tunja",
    "MANURE": "MANAURE",
}

# ---------------------------------------------------------------------------
# Universidades: mapeo canónico (patrón sobre texto sin tildes -> nombre oficial)
# El orden importa: los patrones más específicos van primero.
# ---------------------------------------------------------------------------
UNIVERSIDAD_CANONICA = [
    (r"^universidad nacional abierta", "Universidad Nacional Abierta y a Distancia"),
    (r"^universidad nacional de colombia", "Universidad Nacional de Colombia"),
    (r"^universidad pedagogica y tecnologica", "Universidad Pedagógica y Tecnológica de Colombia"),
    (r"^universidad pedagogica", "Universidad Pedagógica Nacional"),
    (r"^universidad industrial de santander", "Universidad Industrial de Santander"),
    (r"^uniminuto", "Corporación Universitaria Minuto de Dios (UNIMINUTO)"),
    (r"^instituto tecnologico metropolitano", "Instituto Tecnológico Metropolitano"),
    (r"^(museo )?universidad del rosario", "Universidad del Rosario"),
    (r"^universidad (de los )?andes", "Universidad de los Andes"),
    (r"^universidad autonoma de bucaramanga", "Universidad Autónoma de Bucaramanga"),
    (r"^universidad autonoma de occidente", "Universidad Autónoma de Occidente"),
    (r"^universidad autonoma$", "Universidad Autónoma de Colombia"),
    (r"^universidad colegio mayor de cundinamarca", "Universidad Colegio Mayor de Cundinamarca"),
    (r"^universidad de america", "Universidad de América"),
    (r"^universidad de antioquia", "Universidad de Antioquia"),
    (r"^universidad de caldas", "Universidad de Caldas"),
    (r"^universidad de ibague", "Universidad de Ibagué"),
    (r"^universidad de la salle", "Universidad de La Salle"),
    (r"^universidad de santander", "Universidad de Santander"),
    (r"^universidad de cordoba", "Universidad de Córdoba"),
    (r"^universidad del atlantico", "Universidad del Atlántico"),
    (r"^universidad (del|el) bosque", "Universidad El Bosque"),
    (r"^universidad del cauca", "Universidad del Cauca"),
    (r"^universidad del magdalena", "Universidad del Magdalena"),
    (r"^universidad del norte", "Universidad del Norte"),
    (r"^universidad del tolima", "Universidad del Tolima"),
    (r"^universidad del valle", "Universidad del Valle"),
    (r"^universidad distrital", "Universidad Distrital Francisco José de Caldas"),
    (r"^universidad externado", "Universidad Externado de Colombia"),
    (r"^universidad jorge tadeo lozano", "Universidad Jorge Tadeo Lozano"),
    (r"^universidad libre", "Universidad Libre"),
    (r"^universidad mariana", "Universidad Mariana"),
    (r"^universidad militar", "Universidad Militar Nueva Granada"),
    (r"^universidad surcolombiana", "Universidad Surcolombiana"),
    (r"^universidad (unillanos|de los llanos)", "Universidad de los Llanos"),
    (r"^pontificia universidad javeriana", "Pontificia Universidad Javeriana"),
    (r"^universidad santo tomas", "Universidad Santo Tomás"),
    (r"^universidad tecnologica del choco", "Universidad Tecnológica del Chocó Diego Luis Córdoba"),
    (r"^corporacion museo de la sal ichi", "Corporación Museo de la Sal Ichi"),
]

CITY_CANONICAL = {
    "pasca": "Pasca", "cajica": "Cajicá", "barranquilla": "Barranquilla", "tunja": "Tunja",
    "villa de leyva": "Villa de Leyva", "sogamoso": "Sogamoso", "neiva": "Neiva",
    "santa marta": "Santa Marta", "aracataca": "Aracataca", "pasto": "Pasto", "ibague": "Ibagué",
    "cali": "Cali", "palmira": "Palmira", "manizales": "Manizales", "popayan": "Popayán",
    "bucaramanga": "Bucaramanga", "floridablanca": "Floridablanca", "medellin": "Medellín",
    "bogota": "Bogotá D.C.", "leticia": "Leticia", "quibdo": "Quibdó", "manaure": "Manaure",
    "manure": "Manaure", "villavicencio": "Villavicencio", "monteria": "Montería",
}


def clean_text(val):
    """Quita saltos de línea reales y secuencias escapadas literales (\\n, \\r, \\t)."""
    if val is None:
        return ""
    val = str(val)
    for seq in ("\\r\\n", "\\n", "\\r", "\\t"):
        val = val.replace(seq, " ")
    val = val.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    return re.sub(r"\s+", " ", val).strip()


def split_parts(val):
    return [p.strip() for p in clean_text(val).split("|") if p.strip()]


def _capitalize_word(word):
    """Pone en mayúscula la primera letra, también tras comillas, paréntesis o guiones."""
    out, cap_next = [], True
    for ch in word.lower():
        if ch.isalpha():
            out.append(ch.upper() if cap_next else ch)
            cap_next = False
        else:
            out.append(ch)
            if ch in "-/(\"'«":
                cap_next = True
    return "".join(out)


def title_case_es(text):
    text = clean_text(text)
    if not text:
        return ""
    # Normaliza espacios dentro de comillas: '"Diego Luis Córdoba "' -> '"Diego Luis Córdoba"'
    text = re.sub(r'"\s*([^"]*?)\s*"', r'"\1"', text)
    words = text.split(" ")
    formatted = []
    for i, word in enumerate(words):
        clean_word = re.sub(r"[^\w\.-]", "", word)
        if clean_word.upper() in TITLECASE_EXCEPTIONS_UPPER:
            formatted.append(word.upper())
        elif i > 0 and clean_word.lower() in TITLECASE_EXCEPTIONS_LOWER:
            formatted.append(word.lower())
        else:
            formatted.append(_capitalize_word(word))
    return " ".join(formatted)


def apply_word_fixes(text):
    if not text:
        return text

    def repl(m):
        word = m.group(0)
        fixed = WORD_FIXES.get(word.lower())
        if fixed is None:
            return word
        return fixed[0].upper() + fixed[1:] if word[0].isupper() else fixed

    return re.sub(r"[^\W\d_]+", repl, text)


def apply_phrase_fixes(text):
    for wrong, right in PHRASE_FIXES.items():
        text = text.replace(wrong, right)
    return text


def polish(text):
    return apply_phrase_fixes(apply_word_fixes(title_case_es(text)))


# ---------------------------------------------------------------------------
# Normalizadores por campo
# ---------------------------------------------------------------------------
def normalize_naturaleza(val):
    v = R.fold(val)
    if "public" in v:
        return "Pública"
    if "privad" in v:
        return "Privada"
    return "No especificada"


DEPT_PATTERNS = [
    (r"distrito capital|bogot", "Bogotá D.C."),
    (r"valle del cauca", "Valle del Cauca"),
    (r"norte de santander", "Norte de Santander"),
    (r"cordoba|codoba", "Córdoba"),
    (r"antioquia", "Antioquia"),
    (r"atlantico", "Atlántico"),
    (r"boyaca", "Boyacá"),
    (r"caldas", "Caldas"),
    (r"cauca", "Cauca"),
    (r"cundinamarca", "Cundinamarca"),
    (r"huila", "Huila"),
    (r"magdalena", "Magdalena"),
    (r"narino", "Nariño"),
    (r"santander", "Santander"),
    (r"tolima", "Tolima"),
    (r"amazonas", "Amazonas"),
    (r"choco", "Chocó"),
    (r"guajira", "La Guajira"),
    (r"\bmeta\b", "Meta"),
]


def normalize_departamento(val):
    parts = split_parts(val)
    if not parts:
        return "No especificado"
    v = re.sub(r"^\d+\.\s*", "", parts[0])
    folded = R.fold(v)
    for pattern, canonical in DEPT_PATTERNS:
        if re.search(pattern, folded):
            return canonical
    return title_case_es(v)


def _city_candidates(part):
    folded = R.fold(part).replace("-", " ").replace("/", " ").replace(",", " ")
    found = []
    for key, canonical in CITY_CANONICAL.items():
        m = re.search(r"\b" + re.escape(key) + r"\b", folded)
        if m:
            found.append((m.start(), canonical))
    return [c for _, c in sorted(found)]


def normalize_ciudad(val, departamento):
    """
    Resuelve la ciudad validándola contra el departamento ya normalizado.
    Ante valores en conflicto separados por '|', gana el candidato cuya
    ciudad pertenece al departamento del registro.
    """
    parts = split_parts(val)
    candidates = []
    for part in parts:
        for c in _city_candidates(part):
            if c not in candidates:
                candidates.append(c)

    consistent = [c for c in candidates if R.CITY_DEPT.get(c) == departamento]
    if consistent:
        return consistent[0]
    if departamento == "Bogotá D.C.":
        return "Bogotá D.C."
    if candidates:
        # Ningún candidato cuadra con el departamento: se conserva el primero,
        # y el validador lo reportará como inconsistencia.
        return candidates[0]
    if not parts:
        return "Por definir"
    dept_words = set(R.fold(departamento).split())
    tokens = [w for w in parts[0].split(" ") if R.fold(w) not in dept_words]
    return title_case_es(" ".join(tokens) or parts[0])


def normalize_estado(val):
    v = R.fold(val)
    if not v:
        return "Sin información"
    if "cita previa" in v or "programacion" in v:
        return "Cita previa"
    if "temporal" in v:
        return "Cerrado temporalmente"
    if "cerrad" in v or "cierre" in v:
        return "Cerrado"
    if "abierto" in v or "permanente" in v:
        return "Abierto"
    return "Sin información"


def normalize_simco(val):
    v = R.fold(clean_text(val))
    if not v:
        return "Sin información"
    if any(x in v for x in ("no sabe", "no responde", "no se sabe", "desconoce", "sin informacion")):
        return "Sin información"
    if any(x in v for x in ("proceso", "tramite", "tal vez", "posiblemente")):
        return "En proceso / Por confirmar"
    if v in ("si", "simco") or v.startswith("si") or re.search(r"\b20\d\d\b", v):
        return "Sí"
    if v.startswith("no"):
        return "No"
    return "Sin información"


def clean_url(val):
    parts = split_parts(val)
    if not parts:
        return None
    v = parts[0].split(" ")[0]
    if not v or v.lower() in ("n/a", "no", "en proceso", "none"):
        return None
    if not v.startswith(("http://", "https://")):
        if "." in v and "@" not in v:
            v = "https://" + v
        else:
            return None
    return v


def clean_email(row, nombre_museo, person_tokens):
    """
    Devuelve el mejor buzón institucional genérico del registro, o None.

    Candidatos: columna 'Correo electrónico' y columna de correo alternativo.
    Un correo se descarta si su usuario coincide con nombres de directores o
    enlaces, si el dominio es comercial (gmail, hotmail, yahoo...), si está
    malformado o si no es identificable como buzón genérico (ver rnmu_rules).
    """
    sources = [row.get("Correo electrónico") or ""]
    sources += [v for k, v in row.items() if k and k.startswith("¿Cuál es su correo") and v]
    best = None
    for text in sources:
        for email in R.extract_emails(clean_text(text)):
            email = R.normalize_email(email)
            ok, priority, _ = R.email_decision(email, nombre_museo, person_tokens)
            if ok and (best is None or priority > best[0]):
                best = (priority, email)
    return best[1] if best else None


def clean_nombre(val):
    parts = split_parts(val)
    v = parts[0] if parts else ""
    v = re.sub(r"^MuUYSEO\b", "MUSEO", v, flags=re.IGNORECASE)
    return polish(v).rstrip(" .")


def clean_universidad(val):
    parts = split_parts(val)
    if not parts:
        return ""
    folded = R.fold(parts[0])
    folded = re.sub(r"[\"'()]", " ", folded)
    folded = re.sub(r"\s+", " ", folded).strip()
    for pattern, canonical in UNIVERSIDAD_CANONICA:
        if re.search(pattern, folded):
            return canonical
    raise ValueError(
        f"Universidad sin mapeo canónico: {parts[0]!r}. "
        "Agréguela a UNIVERSIDAD_CANONICA en scripts/limpiar_base.py."
    )


def clean_tipologia(val):
    parts = split_parts(val)
    if not parts:
        return None
    v = parts[-1] if len(parts[-1]) > len(parts[0]) else parts[0]
    return polish(v) or None


def clean_direccion(val):
    v = clean_text(val)
    if not v or v.lower() in ("n/a", "no", "sin direccion", "sin dirección", "por definir"):
        return None
    for wrong, right in DIRECCION_FIXES.items():
        v = re.sub(r"\b" + re.escape(wrong) + r"\b", right, v)
    return v


# ---------------------------------------------------------------------------
# Estadísticas
# ---------------------------------------------------------------------------
def compute_stats(museos):
    dept = Counter(m["departamento"] for m in museos)
    universidades = {m["universidad"] for m in museos if m["universidad"]}
    return {
        "totalMuseos": len(museos),
        "totalUniversidades": len(universidades - R.NON_IES),
        "totalEntidadesAliadas": len(universidades & R.NON_IES),
        "totalDepartamentos": len(dept),
        "distribucionPorDepartamento": dict(sorted(dept.items(), key=lambda x: (-x[1], x[0]))),
        "porNaturaleza": {v: sum(1 for m in museos if m["naturaleza"] == v) for v in R.NATURALEZA_VALUES},
        "porEstadoAtencion": {v: sum(1 for m in museos if m["estadoAtencion"] == v) for v in R.ESTADO_VALUES},
        "porSimco": {v: sum(1 for m in museos if m["registroSimco"] == v) for v in R.SIMCO_VALUES},
    }


# ---------------------------------------------------------------------------
# Proceso principal
# ---------------------------------------------------------------------------
def procesar_base(input_csv_path, output_dir):
    print(f"[ETL] Leyendo base cruda desde: {input_csv_path}")
    person_tokens = R.load_person_tokens(input_csv_path)
    museos = []

    with open(input_csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            nombre_raw = row.get("Museo / entidad cultural") or ""
            if not nombre_raw.strip():
                continue

            nombre = clean_nombre(nombre_raw)
            departamento = normalize_departamento(row.get("Departamento"))
            item = {
                "id": int(row.get("ID consolidado") or i),
                "nombre": nombre,
                "universidad": clean_universidad(row.get("Universidad / IES")),
                "naturaleza": normalize_naturaleza(row.get("Naturaleza jurídica")),
                "departamento": departamento,
                "ciudad": normalize_ciudad(row.get("Ciudad / municipio"), departamento),
                "direccion": clean_direccion(row.get("Dirección")),
                "tipologia": clean_tipologia(row.get("Colección / tipología")),
                "estadoAtencion": normalize_estado(row.get("Estado / atención al público")),
                "registroSimco": normalize_simco(row.get("Registro SIMCO")),
                "paginaWeb": clean_url(row.get("Página web")),
                "correoInstitucional": clean_email(row, nombre, person_tokens),
            }
            museos.append(item)

    museos.sort(key=lambda x: (R.fold(x["nombre"]), x["id"]))
    stats = compute_stats(museos)

    output_dir = Path(output_dir)
    faq_path = output_dir / "faq.json"
    faq = json.loads(faq_path.read_text(encoding="utf-8")) if faq_path.exists() else None

    errors = validar_json.validate(museos, stats, faq, person_tokens)
    if errors:
        print("[ETL ERROR] Los datos generados no superan la validación. No se escribió ningún archivo:")
        for e in errors:
            print(f"  - {e}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    museos_path = output_dir / "museos.json"
    stats_path = output_dir / "stats.json"
    museos_path.write_text(json.dumps(museos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    con_correo = sum(1 for m in museos if m["correoInstitucional"])
    print(f"[ETL ÉXITO] {stats['totalMuseos']} museos, {stats['totalUniversidades']} IES, "
          f"{stats['totalEntidadesAliadas']} entidad(es) aliada(s), {stats['totalDepartamentos']} departamentos.")
    print(f"[ETL ÉXITO] Correos publicados: {con_correo} buzones genéricos; "
          f"{len(museos) - con_correo} registros quedan con correoInstitucional = null.")
    print(f"[ETL ÉXITO] Archivos generados: {museos_path} y {stats_path}")
    print("[ETL VALIDACIÓN] validar_json: todas las reglas superadas.")
    return 0


if __name__ == "__main__":
    if not R.RAW_CSV.exists():
        print(f"Error: No se encontró el archivo de datos crudos en {R.RAW_CSV}")
        sys.exit(1)
    sys.exit(procesar_base(R.RAW_CSV, R.DATA_DIR))
