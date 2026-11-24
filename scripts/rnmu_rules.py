# -*- coding: utf-8 -*-
"""
Reglas compartidas del pipeline de datos de la RNMU.

Este módulo es la única fuente de verdad para:
  - la lista blanca de campos de museos.json,
  - los catálogos de valores permitidos,
  - la política de publicación de correos (Habeas Data),
  - la clasificación IES / entidades aliadas,
  - la correspondencia ciudad -> departamento.

Lo importan tanto `limpiar_base.py` (ETL) como `validar_json.py` (validador),
para que ambos apliquen exactamente las mismas reglas.

IMPORTANTE: este archivo es público. No debe contener nombres de personas,
teléfonos ni ningún otro dato personal.
"""

import csv
import re
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_CSV = BASE_DIR / "data-raw" / "Base_consolidada_museos_universitarios_octubre_2026.csv"
DATA_DIR = BASE_DIR / "src" / "data"

# ---------------------------------------------------------------------------
# Lista blanca y catálogos
# ---------------------------------------------------------------------------
WHITELIST_FIELDS = frozenset({
    "id", "nombre", "universidad", "naturaleza", "departamento", "ciudad",
    "direccion", "tipologia", "estadoAtencion", "registroSimco", "paginaWeb",
    "correoInstitucional",
})

NATURALEZA_VALUES = ("Pública", "Privada", "No especificada")
ESTADO_VALUES = ("Abierto", "Cita previa", "Cerrado temporalmente", "Cerrado", "Sin información")
SIMCO_VALUES = ("Sí", "No", "En proceso / Por confirmar", "Sin información")

FAQ_CATEGORIES = {
    "Marco Legal, Naturaleza y Vinculación": (1, 3, 5, 6),
    "Autonomía, Compromisos y Gratuidad": (2, 4, 9, 11),
    "Dinámica de Trabajo, Beneficios y Caracterización": (7, 8, 10, 12),
}

STATS_KEYS = frozenset({
    "totalMuseos", "totalUniversidades", "totalEntidadesAliadas", "totalDepartamentos",
    "distribucionPorDepartamento", "porNaturaleza", "porEstadoAtencion", "porSimco",
})

# Entidades que no son Instituciones de Educación Superior. Aparecen en el
# directorio, pero no cuentan en `totalUniversidades`.
NON_IES = frozenset({
    "Corporación Museo de la Sal Ichi",
})

# ---------------------------------------------------------------------------
# Ciudades canónicas y su departamento
# ---------------------------------------------------------------------------
CITY_DEPT = {
    "Pasca": "Cundinamarca",
    "Cajicá": "Cundinamarca",
    "Barranquilla": "Atlántico",
    "Tunja": "Boyacá",
    "Villa de Leyva": "Boyacá",
    "Sogamoso": "Boyacá",
    "Neiva": "Huila",
    "Santa Marta": "Magdalena",
    "Aracataca": "Magdalena",
    "Pasto": "Nariño",
    "Ibagué": "Tolima",
    "Cali": "Valle del Cauca",
    "Palmira": "Valle del Cauca",
    "Manizales": "Caldas",
    "Popayán": "Cauca",
    "Bucaramanga": "Santander",
    "Floridablanca": "Santander",
    "Medellín": "Antioquia",
    "Bogotá D.C.": "Bogotá D.C.",
    "Leticia": "Amazonas",
    "Quibdó": "Chocó",
    "Manaure": "La Guajira",
    "Villavicencio": "Meta",
    "Montería": "Córdoba",
}

# ---------------------------------------------------------------------------
# Política de correos (Habeas Data)
# ---------------------------------------------------------------------------
# Solo se publican buzones institucionales genéricos. Un correo se descarta si:
#   1. su dominio es comercial o personal,
#   2. tiene formato inválido o caracteres no ASCII,
#   3. el usuario coincide con nombres de directores o enlaces (solo verificable
#      cuando la base cruda está disponible localmente),
#   4. no contiene ningún término institucional genérico ni un término propio
#      del nombre del museo (y no está en la lista de buzones revisados),
#   5. tiene forma "nombre.apellido" sin ningún término institucional.

COMMERCIAL_DOMAINS = frozenset({
    "gmail.com", "googlemail.com", "hotmail.com", "hotmail.es", "outlook.com",
    "outlook.es", "live.com", "yahoo.com", "yahoo.es", "icloud.com", "aol.com",
    "protonmail.com",
})

# Correcciones de dominio verificables (errores de digitación evidentes).
DOMAIN_FIXES = {
    "jacveriana.edu.co": "javeriana.edu.co",
    "minorte.edu.co": "uninorte.edu.co",
}

# Términos que identifican un buzón del museo o de la colección (prioridad alta).
MAILBOX_KEYWORDS_MUSEUM = (
    "museografia", "museos", "museo", "mus", "herbario", "herba", "entomo",
    "observatorio", "coleccion", "colecciones",
)

# Términos que identifican un buzón institucional genérico (prioridad media).
MAILBOX_KEYWORDS_GENERIC = (
    "vicerrectoria", "informacion", "contactenos", "contacto", "info",
    "cultura", "cultural", "patrimonio", "proyeccion", "extension", "bienestar",
    "direccion", "biblio", "archivo", "general", "rectoria", "comunica",
    "educacion", "laboratorio", "digital", "centro", "arte", "ciencia",
    "historia", "natural", "arqueolog", "antropolog", "geolog", "paleon",
    "forest", "secretaria", "divulgacion",
)

# Buzones genéricos revisados manualmente. Ninguno corresponde a una persona.
# Se aceptan aunque no contengan términos genéricos o aunque una subcadena
# coincida por azar con un nombre (p. ej. "leon" dentro de "paleon").
MAILBOX_ALLOWLIST = frozenset({
    "latitud@udistrital.edu.co",      # Museo Interactivo Geoespacial (marca "Latitud")
    "obsan_fcbog@unal.edu.co",        # Observatorio Astronómico Nacional
    "depant_bog@unal.edu.co",         # Departamento de Antropología, sede Bogotá
    "muspaleon_fcbog@unal.edu.co",    # Museo Paleontológico, Facultad de Ciencias
    "msamoga_man@unal.edu.co",        # Museo Samoga, sede Manizales
})

# Palabras que nunca se tratan como nombre de persona aunque aparezcan en los
# campos de director o enlace de la base cruda.
PERSON_STOPWORDS = frozenset({
    "museo", "museos", "universidad", "nacional", "colombia", "director",
    "directora", "coordinador", "coordinadora", "coordinacion", "docente",
    "profesor", "profesora", "curador", "curadora", "jefe", "jefa", "decano",
    "decana", "sede", "facultad", "departamento", "herbario", "laboratorio",
    "grupo", "centro", "cultura", "cultural", "patrimonio", "extension",
    "historia", "natural", "ciencias", "ciencia", "division", "oficina",
    "area", "unidad", "programa", "instituto", "escuela", "biblioteca",
    "vicerrectoria", "rectoria", "direccion", "administrativo", "administrativa",
    "encargado", "encargada", "responsable", "auxiliar", "asistente",
    "profesional", "investigador", "investigadora", "monitor", "monitora",
})

EMAIL_RE = re.compile(r"(?<![\w.%+-])([\w.%+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,})(?![\w.-])")
STRICT_EMAIL_RE = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,}$")


def fold(text):
    """Minúsculas sin tildes ni diacríticos."""
    text = unicodedata.normalize("NFKD", str(text or ""))
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def museum_tokens(nombre):
    """Términos distintivos del nombre del museo (para buzones tipo 'casagaitan@')."""
    tokens = set()
    for t in re.split(r"[^a-z0-9]+", fold(nombre)):
        if len(t) >= 4 and t not in {"museo", "universidad", "nacional", "colombia", "para", "como"}:
            tokens.add(t)
    return tokens


def load_person_tokens(csv_path=RAW_CSV):
    """
    Tokens (>= 4 letras) de los nombres de directores y enlaces en la base cruda.
    Solo se usan en memoria; nunca se escriben a disco ni se imprimen.
    Devuelve None si la base cruda no está disponible (p. ej. en CI).
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        return None
    tokens = set()
    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        person_cols = [h for h in (reader.fieldnames or [])
                       if h.startswith("Director o coordinador") or h.startswith("Nombre de la persona")]
        for row in reader:
            for col in person_cols:
                for t in re.split(r"[^a-z]+", fold(row.get(col))):
                    if len(t) >= 4 and t not in PERSON_STOPWORDS:
                        tokens.add(t)
    return tokens


def normalize_email(raw_email):
    """Minúsculas y corrección de dominios con errores evidentes."""
    email = str(raw_email or "").strip().lower()
    if "@" not in email:
        return email
    local, domain = email.rsplit("@", 1)
    domain = DOMAIN_FIXES.get(domain, domain)
    return f"{local}@{domain}"


def extract_emails(text):
    """Extrae todos los correos candidatos de un texto libre, en orden."""
    return [m.group(1) for m in EMAIL_RE.finditer(str(text or ""))]


def email_decision(email, nombre_museo, person_tokens=None):
    """
    Evalúa un correo según la política de publicación.
    Devuelve (aceptado: bool, prioridad: int, motivo: str).
    Prioridad 2 = buzón del museo; 1 = buzón institucional genérico.
    """
    email = normalize_email(email)
    if not STRICT_EMAIL_RE.match(email):
        return False, 0, "formato inválido o caracteres no ASCII"
    local, domain = email.split("@", 1)
    if domain in COMMERCIAL_DOMAINS or any(label in {"gmail", "hotmail", "yahoo", "outlook"} for label in domain.split(".")):
        return False, 0, "dominio comercial o personal"

    if email in MAILBOX_ALLOWLIST:
        return True, 2, "buzón genérico revisado"

    local_alpha = re.sub(r"[^a-z]", "", local)
    if person_tokens:
        for t in person_tokens:
            if t in local_alpha:
                return False, 0, "coincide con nombre de director o enlace"

    has_museum_kw = any(k in local for k in MAILBOX_KEYWORDS_MUSEUM)
    has_museum_token = any(t in local_alpha for t in museum_tokens(nombre_museo))
    has_generic_kw = any(k in local for k in MAILBOX_KEYWORDS_GENERIC)

    if not (has_museum_kw or has_museum_token or has_generic_kw):
        return False, 0, "sin término institucional genérico"

    # Forma "nombre.apellido": dos o más segmentos alfabéticos donde ninguno
    # aporta un término institucional.
    segments = [s for s in re.split(r"[._-]+", local) if s]
    if len(segments) >= 2:
        def institutional(seg):
            return (any(k in seg for k in MAILBOX_KEYWORDS_MUSEUM + MAILBOX_KEYWORDS_GENERIC)
                    or any(t in seg for t in museum_tokens(nombre_museo)))
        if not any(institutional(s) for s in segments):
            return False, 0, "forma nombre.apellido"

    priority = 2 if (has_museum_kw or has_museum_token) else 1
    return True, priority, "buzón institucional"


def city_dept_consistent(ciudad, departamento):
    expected = CITY_DEPT.get(ciudad)
    return expected is None or expected == departamento
