#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de los datos públicos de la RNMU (src/data/*.json).

Sale con código 1 si encuentra cualquier incumplimiento:
  - claves distintas a las 12 de la lista blanca en museos.json,
  - correos con dominio comercial, malformados, con forma de nombre de
    persona o, si la base cruda está disponible localmente, que coincidan con
    nombres de directores o enlaces,
  - valores fuera de catálogo en naturaleza, estadoAtencion o registroSimco,
  - URLs de paginaWeb que no empiecen por http:// o https://,
  - stats.json que no cuadre con museos.json,
  - faq.json sin las 12 preguntas o con categorías distintas a las acordadas,
  - otros controles de calidad: ids duplicados, separadores '|', saltos de
    línea literales, prefijos numéricos y ciudad incoherente con departamento.

En CI la base cruda no existe; en ese caso la verificación de correos usa solo
las reglas heurísticas de rnmu_rules.email_decision (sin nombres reales).

Uso:
    python scripts/validar_json.py
"""

import sys

sys.dont_write_bytecode = True

import json
import re
from collections import Counter

import rnmu_rules as R


def _check_museos(museos, person_tokens):
    errors = []
    if not isinstance(museos, list) or not museos:
        return ["museos.json debe ser una lista no vacía."]

    ids = Counter(m.get("id") for m in museos if isinstance(m, dict))
    for dup, n in ids.items():
        if n > 1:
            errors.append(f"id {dup} aparece {n} veces.")

    for m in museos:
        if not isinstance(m, dict):
            errors.append("museos.json contiene un elemento que no es un objeto.")
            continue
        mid = m.get("id")
        keys = set(m.keys())
        if keys != R.WHITELIST_FIELDS:
            extra = sorted(keys - R.WHITELIST_FIELDS)
            missing = sorted(R.WHITELIST_FIELDS - keys)
            errors.append(f"id {mid}: claves no permitidas {extra} / faltantes {missing}.")
            continue

        if not isinstance(mid, int):
            errors.append(f"id {mid!r}: el id debe ser entero.")
        for field in ("nombre", "universidad", "departamento", "ciudad"):
            if not isinstance(m[field], str) or not m[field].strip():
                errors.append(f"id {mid}: '{field}' debe ser texto no vacío.")
        for field in ("direccion", "tipologia", "paginaWeb", "correoInstitucional"):
            if m[field] is not None and (not isinstance(m[field], str) or not m[field].strip()):
                errors.append(f"id {mid}: '{field}' debe ser texto no vacío o null.")

        if m["naturaleza"] not in R.NATURALEZA_VALUES:
            errors.append(f"id {mid}: naturaleza fuera de catálogo: {m['naturaleza']!r}.")
        if m["estadoAtencion"] not in R.ESTADO_VALUES:
            errors.append(f"id {mid}: estadoAtencion fuera de catálogo: {m['estadoAtencion']!r}.")
        if m["registroSimco"] not in R.SIMCO_VALUES:
            errors.append(f"id {mid}: registroSimco fuera de catálogo: {m['registroSimco']!r}.")

        url = m["paginaWeb"]
        if url is not None and (not url.startswith(("http://", "https://")) or " " in url):
            errors.append(f"id {mid}: paginaWeb no es una URL http(s) válida: {url!r}.")

        email = m["correoInstitucional"]
        if email is not None:
            ok, _, motivo = R.email_decision(email, m["nombre"], person_tokens)
            if not ok:
                # No se imprime el correo: puede contener datos personales.
                errors.append(f"id {mid}: correoInstitucional no permitido ({motivo}).")

        for field, value in m.items():
            if isinstance(value, str):
                if "|" in value:
                    errors.append(f"id {mid}: '{field}' contiene el separador '|'.")
                if "\\n" in value or "\n" in value or "\r" in value:
                    errors.append(f"id {mid}: '{field}' contiene saltos de línea.")
        if re.match(r"^\d", m["departamento"]):
            errors.append(f"id {mid}: departamento con prefijo numérico: {m['departamento']!r}.")
        if not R.city_dept_consistent(m["ciudad"], m["departamento"]):
            errors.append(f"id {mid}: la ciudad {m['ciudad']!r} no pertenece a {m['departamento']!r}.")
    return errors


def _expected_stats(museos):
    dept = Counter(m["departamento"] for m in museos)
    univ = {m["universidad"] for m in museos}
    nat = Counter(m["naturaleza"] for m in museos)
    est = Counter(m["estadoAtencion"] for m in museos)
    sim = Counter(m["registroSimco"] for m in museos)
    return {
        "totalMuseos": len(museos),
        "totalUniversidades": len(univ - R.NON_IES),
        "totalEntidadesAliadas": len(univ & R.NON_IES),
        "totalDepartamentos": len(dept),
        "distribucionPorDepartamento": dict(dept),
        "porNaturaleza": {v: nat.get(v, 0) for v in R.NATURALEZA_VALUES},
        "porEstadoAtencion": {v: est.get(v, 0) for v in R.ESTADO_VALUES},
        "porSimco": {v: sim.get(v, 0) for v in R.SIMCO_VALUES},
    }


def _check_stats(museos, stats):
    if not isinstance(stats, dict):
        return ["stats.json debe ser un objeto."]
    errors = []
    if set(stats.keys()) != R.STATS_KEYS:
        errors.append(f"stats.json: claves esperadas {sorted(R.STATS_KEYS)}, encontradas {sorted(stats.keys())}.")
        return errors
    expected = _expected_stats(museos)
    for key, value in expected.items():
        if stats[key] != value:
            errors.append(f"stats.json: '{key}' no cuadra con museos.json (esperado {value}, encontrado {stats[key]}).")
    return errors


def _check_faq(faq):
    if faq is None:
        return ["faq.json no existe."]
    errors = []
    if not isinstance(faq, list) or len(faq) != 12:
        return [f"faq.json debe contener exactamente 12 preguntas (tiene {len(faq) if isinstance(faq, list) else 'formato inválido'})."]
    expected_cat = {i: cat for cat, ids in R.FAQ_CATEGORIES.items() for i in ids}
    seen = set()
    for item in faq:
        fid = item.get("id")
        seen.add(fid)
        if set(item.keys()) != {"id", "categoria", "pregunta", "respuesta"}:
            errors.append(f"faq id {fid}: claves esperadas id, categoria, pregunta, respuesta.")
            continue
        if item["categoria"] != expected_cat.get(fid):
            errors.append(f"faq id {fid}: categoría {item['categoria']!r}, esperada {expected_cat.get(fid)!r}.")
        for field in ("pregunta", "respuesta"):
            if not isinstance(item[field], str) or not item[field].strip():
                errors.append(f"faq id {fid}: '{field}' vacío.")
    if seen != set(range(1, 13)):
        errors.append(f"faq.json: ids esperados 1 a 12, encontrados {sorted(seen, key=str)}.")
    return errors


def validate(museos, stats, faq, person_tokens=None):
    """Devuelve la lista de errores encontrados (vacía si todo es válido)."""
    errors = _check_museos(museos, person_tokens)
    if not errors:
        errors += _check_stats(museos, stats)
    errors += _check_faq(faq)
    return errors


def _load(name):
    path = R.DATA_DIR / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    museos, stats, faq = _load("museos.json"), _load("stats.json"), _load("faq.json")
    if museos is None or stats is None:
        print("[VALIDACIÓN ERROR] Faltan src/data/museos.json o src/data/stats.json.")
        return 1

    person_tokens = R.load_person_tokens()
    modo = ("con nombres de la base cruda local" if person_tokens is not None
            else "sin base cruda (modo CI: reglas heurísticas)")
    errors = validate(museos, stats, faq, person_tokens)

    if errors:
        print(f"[VALIDACIÓN ERROR] {len(errors)} incumplimiento(s) ({modo}):")
        for e in errors:
            print(f"  - {e}")
        return 1

    con_correo = sum(1 for m in museos if m["correoInstitucional"])
    print(f"[VALIDACIÓN OK] {len(museos)} museos, {con_correo} correos genéricos, "
          f"stats.json y faq.json conformes ({modo}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
