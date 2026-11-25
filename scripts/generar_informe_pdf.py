#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera la versión imprimible del informe ejecutivo de la RNMU.

Entrada : docs/informe_reunion_inicial_rnmu.md
Salidas : docs/informe_reunion_inicial_rnmu.html (HTML con estilos de impresión)
          docs/Informe_Inicial_Arquitectura_y_Datos_RNMU.pdf (vía Microsoft Edge headless)

Uso:
    python scripts/generar_informe_pdf.py

Requisitos: Python 3 con el paquete `markdown` y Microsoft Edge (o Google Chrome).
El Markdown es la fuente única: para cambiar el informe, edite el .md y vuelva a ejecutar.
"""

import html
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "docs" / "informe_reunion_inicial_rnmu.md"
HTML_PATH = ROOT / "docs" / "informe_reunion_inicial_rnmu.html"
PDF_PATH = ROOT / "docs" / "Informe_Inicial_Arquitectura_y_Datos_RNMU.pdf"

TITULO = "Red Nacional de Museos Universitarios de Colombia (RNMU)"
SUBTITULO = "Informe Inicial de Arquitectura Tecnológica, Seguridad de Datos y Gestión del Catálogo"
FECHA = "Noviembre 2026"
VERSION = "1.0"

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

CSS = """
@page {
  size: Letter;
  margin: 22mm 18mm 20mm 18mm;
  @top-left { content: "RNMU · Informe Inicial de Arquitectura y Datos"; font: 600 7.5pt 'Segoe UI', Arial, sans-serif; color: #852230; }
  @top-right { content: "Versión 1.0 · Noviembre 2026"; font: 7.5pt 'Segoe UI', Arial, sans-serif; color: #6b7280; }
  @bottom-left { content: "Uso interno del Comité de la Red · No contiene datos personales"; font: 7.5pt 'Segoe UI', Arial, sans-serif; color: #6b7280; }
  @bottom-right { content: "Página " counter(page) " de " counter(pages); font: 600 7.5pt 'Segoe UI', Arial, sans-serif; color: #71212d; }
}
@page cover {
  margin: 0;
  @top-left { content: none; } @top-right { content: none; }
  @bottom-left { content: none; } @bottom-right { content: none; }
}

* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  margin: 0;
  font-family: 'Segoe UI', Arial, Helvetica, sans-serif, 'Segoe UI Emoji';
  font-size: 10pt;
  line-height: 1.5;
  color: #1f2937;
}

/* ---------- Portada ---------- */
.cover {
  page: cover;
  width: 215.9mm;
  height: 278mm;
  position: relative;
  overflow: hidden;
  break-after: page;
  background: #faf9f6;
}
.cover-band {
  background: linear-gradient(135deg, #3f0c13 0%, #71212d 55%, #852230 100%);
  color: #fff;
  padding: 30mm 22mm 18mm 22mm;
  position: relative;
}
.cover-band::after {
  content: "";
  position: absolute; left: 0; right: 0; bottom: 0;
  height: 3mm;
  background: linear-gradient(90deg, #c59b27, #e1cb73, #c59b27);
}
.cover-eyebrow {
  font-size: 9pt; letter-spacing: 0.22em; text-transform: uppercase;
  color: #e1cb73; font-weight: 700; margin: 0 0 6mm 0;
}
.cover h1 {
  font-size: 27pt; line-height: 1.15; margin: 0 0 7mm 0; font-weight: 800; color: #fff;
}
.cover .subtitle {
  font-size: 14pt; line-height: 1.35; font-weight: 400; color: #fbe6e8; margin: 0; max-width: 150mm;
}
.cover-body { padding: 14mm 22mm 0 22mm; }
.cover-meta { width: 100%; border-collapse: collapse; font-size: 10pt; margin: 0; }
.cover-meta td { padding: 2.8mm 0; border: none; border-bottom: 0.5pt solid #e5dccb; vertical-align: top; background: transparent !important; }
.cover-meta td:first-child { width: 52mm; color: #852230; font-weight: 700; text-transform: uppercase; font-size: 8pt; letter-spacing: 0.08em; padding-top: 3.3mm; }
.cover-notes { display: flex; gap: 6mm; margin-top: 10mm; }
.cover-note {
  flex: 1; border: 0.75pt solid #e5dccb; border-top: 2.5pt solid #c59b27;
  background: #fff; padding: 5mm 5mm 4mm 5mm; border-radius: 1.5mm; font-size: 9pt; line-height: 1.45;
}
.cover-note strong { display: block; color: #71212d; font-size: 9.5pt; margin-bottom: 1.5mm; }
.cover-footer {
  position: absolute; left: 22mm; right: 22mm; bottom: 16mm;
  font-size: 8pt; color: #6b7280; border-top: 0.5pt solid #e5dccb; padding-top: 4mm;
  display: flex; justify-content: space-between;
}

/* ---------- Contenido ---------- */
.toc { break-after: page; }
.toc h2 { border-bottom: 2pt solid #c59b27; }
.toc ol { list-style: none; padding: 0; margin: 6mm 0 0 0; counter-reset: none; }
.toc li {
  display: flex; align-items: baseline; gap: 4mm;
  padding: 3.5mm 0; border-bottom: 0.5pt solid #eee6d6; font-size: 11pt;
}
.toc .num {
  flex: 0 0 9mm; height: 9mm; border-radius: 50%; background: #fdf3f4; color: #71212d;
  font-weight: 800; display: inline-flex; align-items: center; justify-content: center; font-size: 10pt;
}
.toc .anexo { margin-top: 8mm; font-size: 9pt; color: #6b7280; }

h2 {
  color: #71212d; font-size: 17pt; line-height: 1.25; font-weight: 800;
  margin: 0 0 5mm 0; padding-bottom: 2.5mm; border-bottom: 1.5pt solid #c59b27;
  break-after: avoid; page-break-after: avoid;
}
section.chapter { break-before: page; page-break-before: always; }
h3 {
  color: #852230; font-size: 12pt; font-weight: 700; margin: 6mm 0 2.5mm 0;
  break-after: avoid; page-break-after: avoid;
}
p { margin: 0 0 3mm 0; }
ul, ol { margin: 0 0 3.5mm 0; padding-left: 6mm; }
li { margin: 0 0 1.2mm 0; }
li::marker { color: #c59b27; }
strong { color: #111827; }
code {
  font-family: Consolas, 'Courier New', monospace; font-size: 8.8pt;
  background: #f4f2ec; color: #71212d; padding: 0.3mm 1.2mm; border-radius: 1mm;
}
hr { display: none; }

.keep, table, blockquote, .flow, .cover-note { break-inside: avoid; page-break-inside: avoid; }

/* ---------- Tablas ---------- */
table { width: 100%; border-collapse: collapse; margin: 2mm 0 5mm 0; font-size: 9pt; line-height: 1.4; }
thead th {
  background: #71212d; color: #fff; font-weight: 700; text-align: left;
  padding: 2.4mm 2.6mm; border: 0.5pt solid #71212d; vertical-align: bottom;
}
thead th strong, thead th a { color: inherit; }
thead { display: table-header-group; }
tbody td { padding: 2.2mm 2.6mm; border: 0.5pt solid #e5dccb; vertical-align: top; }
tbody tr:nth-child(even) td { background: #faf6ee; }
tbody tr { break-inside: avoid; page-break-inside: avoid; }
table.no-head tbody tr:first-child td { border-top: 1.5pt solid #c59b27; }
table.datos12 td { text-align: center; font-weight: 600; color: #71212d; background: #fdf9f3; }
table.datos12 tbody tr:nth-child(even) td { background: #fdf9f3; }
table.comparativa { font-size: 8pt; line-height: 1.32; margin-bottom: 3mm; }
table.comparativa thead th { padding: 2mm 2.2mm; }
table.comparativa tbody td { padding: 1.6mm 2.2mm; }
table.comparativa td:last-child strong { color: #71212d; }
/* Capítulo 5: lista y aviso compactos para que quepan con la tabla */
section.compact h3 { margin-top: 4mm; }
section.compact ul { margin-bottom: 2.5mm; }
section.compact li { margin-bottom: 0.8mm; }
section.compact blockquote { margin-top: 2mm; }
table.comparativa td:first-child { font-weight: 700; color: #71212d; background: #fbf9ed; width: 18%; }
table.comparativa th:last-child { background: #3f0c13; border-color: #3f0c13; }
table.comparativa td:last-child { background: #fdf3f4 !important; }

/* ---------- Avisos ---------- */
blockquote {
  margin: 3mm 0 5mm 0; padding: 3.5mm 4.5mm; background: #fbf9ed;
  border-left: 3pt solid #c59b27; border-radius: 0 1.5mm 1.5mm 0; font-size: 9.2pt;
}
blockquote p { margin: 0; }
blockquote.warning { background: #fdf3f4; border-left-color: #852230; }

/* ---------- Diagrama del filtro ---------- */
.flow { display: flex; align-items: stretch; gap: 0; margin: 3mm 0 6mm 0; font-size: 8.6pt; line-height: 1.35; }
.flow .step { flex: 1; border-radius: 2mm; padding: 3.5mm; border: 0.75pt solid #e5dccb; background: #fff; }
.flow .step.wide { flex: 1.6; }
.flow .step h4 { margin: 0 0 1.5mm 0; font-size: 9.2pt; color: #71212d; }
.flow .step ul { margin: 0; padding-left: 4mm; }
.flow .step p { margin: 0; }
.flow .arrow { flex: 0 0 7mm; display: flex; align-items: center; justify-content: center; color: #c59b27; font-size: 14pt; font-weight: 700; }
.flow .private { background: #f4f2ec; }
.flow .filter { background: #fdf3f4; border-color: #f0abb3; }
.flow .check { background: #fbf9ed; border-color: #e1cb73; }
.flow .public { background: #f0f5fa; border-color: #c3dbed; }
.flow .public h4 { color: #254a6d; }

.closing { margin-top: 8mm; padding-top: 4mm; border-top: 0.5pt solid #e5dccb; font-size: 8.8pt; color: #6b7280; }
"""

FLOW_HTML = """
<div class="flow" role="img" aria-label="Flujo del filtro de privacidad">
  <div class="step private"><h4>🔒 Matriz interna</h4><p>Archivo local y privado de la coordinación. Nunca se sube a internet.</p></div>
  <div class="arrow">→</div>
  <div class="step filter wide"><h4>🛡️ Filtro de privacidad y limpieza</h4>
    <ul>
      <li>Conserva solo 12 datos institucionales</li>
      <li>Retira teléfonos, nombres de personas, datos financieros y comentarios</li>
      <li>Descarta correos personales o comerciales (Gmail, Hotmail…)</li>
      <li>Corrige y unifica nombres, ciudades y universidades</li>
    </ul></div>
  <div class="arrow">→</div>
  <div class="step check"><h4>✅ Verificación automática</h4><p>Si algo no cumple, <strong>no se publica</strong>.</p></div>
  <div class="arrow">→</div>
  <div class="step public"><h4>🌐 Portal público</h4><p>Solo información institucional autorizada.</p></div>
</div>
"""


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).strip()


def parse_cover_meta(head_md):
    """Filas '| **Clave** | Valor |' de la tabla de metadatos inicial."""
    meta = []
    for line in head_md.splitlines():
        m = re.match(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|$", line.strip())
        if m:
            meta.append((m.group(1), m.group(2)))
    return meta


def normalize_lists(md_text):
    """python-markdown exige una línea en blanco antes de una lista; GitHub no."""
    lines, out = md_text.splitlines(), []
    for i, line in enumerate(lines):
        prev = out[-1] if out else ""
        is_item = re.match(r"^\s*([-*]|\d+\.)\s+", line)
        prev_is_item_or_blank = (not prev.strip()) or re.match(r"^\s*([-*]|\d+\.)\s+", prev) or prev.startswith("  ")
        if is_item and not prev_is_item_or_blank and not prev.lstrip().startswith("|"):
            out.append("")
        out.append(line)
    return "\n".join(out)


def render_body(body_md):
    out = markdown.markdown(normalize_lists(body_md), extensions=["tables", "fenced_code", "sane_lists"])

    # Diagrama ASCII -> diagrama HTML
    out = re.sub(r"<pre><code>Matriz interna[\s\S]*?</code></pre>", FLOW_HTML, out)

    # Clases por tabla: sin encabezado (p. ej. los 12 datos) y comparativa
    def classify_table(m):
        table = m.group(0)
        thead = re.search(r"<thead>[\s\S]*?</thead>", table)
        classes = []
        if thead and not strip_tags(thead.group(0)):
            table = table.replace(thead.group(0), "")
            classes.append("no-head")
            if "Identificador" in table:
                classes.append("datos12")
        elif thead and "Solución implementada" in thead.group(0):
            classes.append("comparativa")
        if classes:
            table = table.replace("<table>", f'<table class="{" ".join(classes)}">', 1)
        return table
    out = re.sub(r"<table>[\s\S]*?</table>", classify_table, out)

    # Avisos: advertencia en tono borgoña
    out = re.sub(r"<blockquote>\s*<p>⚠️", '<blockquote class="warning">\n<p>⚠️', out)

    # Mantener cada h3 junto al bloque que lo sigue
    out = re.sub(
        r"(<h3>[\s\S]*?</h3>\s*<(table|p|ul|ol|blockquote)\b[\s\S]*?</\2>)",
        r'<div class="keep">\1</div>', out)

    # Capítulos: cada h2 abre una sección en página nueva
    parts = re.split(r"(?=<h2>)", out)
    chapters, toc = [], []
    for part in parts:
        if not part.strip():
            continue
        h2 = re.match(r"<h2>([\s\S]*?)</h2>", part)
        if h2:
            title = strip_tags(h2.group(1))
            anchor = f"cap-{len(toc) + 1}"
            toc.append(title)
            part = part.replace("<h2>", f'<h2 id="{anchor}">', 1)
            cls = "chapter compact" if 'class="comparativa"' in part else "chapter"
            chapters.append(f'<section class="{cls}">{part}</section>')
        else:
            chapters.append(part)
    return "\n".join(chapters), toc


def build_html():
    text = MD_PATH.read_text(encoding="utf-8")
    m = re.search(r"^## \d+\.", text, flags=re.M)
    if not m:
        raise SystemExit("No se encontró el primer capítulo ('## 1.') en el informe.")
    head_md, body_md = text[:m.start()], text[m.start():]

    # La línea final de anexo se muestra como cierre
    anexo = ""
    am = re.search(r"\n\*\*Anexo:\*\*(.+)$", body_md.strip(), flags=re.S)
    if am:
        anexo = markdown.markdown("**Anexo:** " + am.group(1).strip())
        body_md = body_md.strip()[:am.start()]

    meta = parse_cover_meta(head_md)
    body_html, toc = render_body(body_md)

    # Fecha y versión van primero; se omite la fecha repetida del Markdown
    meta_rows = [("Fecha", FECHA), ("Versión", VERSION)] + [
        (k, v) for k, v in meta if k.lower() not in ("fecha", "versión", "version")]
    meta_html = "\n".join(
        f"<tr><td>{html.escape(k)}</td><td>{markdown.markdown(v)[3:-4]}</td></tr>" for k, v in meta_rows)

    toc_items = []
    for i, t in enumerate(toc, start=1):
        label = re.sub(r"^\d+\.\s*", "", t)
        toc_items.append(f'<li><span class="num">{i}</span><a href="#cap-{i}" style="color:inherit;text-decoration:none">{html.escape(label)}</a></li>')

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{html.escape(SUBTITULO)} · RNMU</title>
<meta name="author" content="Red Nacional de Museos Universitarios (RNMU)">
<meta name="description" content="{html.escape(SUBTITULO)}">
<style>{CSS}</style>
</head>
<body>
<div class="cover">
  <div class="cover-band">
    <p class="cover-eyebrow">Informe ejecutivo · Reunión inicial del proyecto</p>
    <h1>{html.escape(TITULO)}</h1>
    <p class="subtitle">{html.escape(SUBTITULO)}</p>
  </div>
  <div class="cover-body">
    <table class="cover-meta"><tbody>{meta_html}</tbody></table>
    <div class="cover-notes">
      <div class="cover-note"><strong>🔒 Nota de confidencialidad</strong>
        Documento de uso interno del Comité de la Red y de las autoridades académicas convocadas. No contiene datos personales: las cifras provienen únicamente de los datos institucionales publicados en el portal.</div>
      <div class="cover-note"><strong>💰 Costo de infraestructura: $0</strong>
        El portal opera sin pago de servidores, bases de datos ni licencias, sobre GitHub Pages, bajo las condiciones actuales del servicio para proyectos públicos y no comerciales.</div>
    </div>
  </div>
  <div class="cover-footer"><span>Coordinación: Museo de Trajes · Universidad de América</span><span>Versión {VERSION} · {FECHA}</span></div>
</div>

<div class="toc">
  <h2>Contenido</h2>
  <ol>{''.join(toc_items)}</ol>
  <p class="anexo">Anexo: detalle de duplicados, URLs no oficiales y registros sin correo en <code>docs/analisis_duplicados_y_urls.md</code>.</p>
</div>

{body_html}

<div class="closing">{anexo}</div>
</body>
</html>
"""


def find_browser():
    for p in BROWSERS:
        if Path(p).exists():
            return p
    for name in ("msedge", "chrome", "google-chrome", "chromium"):
        found = shutil.which(name)
        if found:
            return found
    return None


def print_pdf(browser):
    if PDF_PATH.exists():
        PDF_PATH.unlink()
    with tempfile.TemporaryDirectory(prefix="rnmu-edge-", ignore_cleanup_errors=True) as profile:
        cmd = [
            browser,
            "--headless",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={profile}",   # perfil aislado: no interfiere con un Edge abierto
            "--run-all-compositor-stages-before-draw",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            f"--print-to-pdf={PDF_PATH}",
            HTML_PATH.resolve().as_uri(),
        ]
        subprocess.run(cmd, check=False, timeout=180,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # En Windows el ejecutable puede devolver el control antes de terminar de escribir.
        for _ in range(60):
            if PDF_PATH.exists() and PDF_PATH.stat().st_size > 0:
                size = PDF_PATH.stat().st_size
                time.sleep(1)
                if PDF_PATH.stat().st_size == size:
                    break
            time.sleep(1)


def main():
    HTML_PATH.write_text(build_html(), encoding="utf-8")
    print(f"[INFORME] HTML generado: {HTML_PATH}")

    browser = find_browser()
    if not browser:
        print("[INFORME ERROR] No se encontró Microsoft Edge ni Google Chrome.")
        return 1
    print_pdf(browser)

    if not PDF_PATH.exists() or PDF_PATH.stat().st_size < 10_000:
        print("[INFORME ERROR] El PDF no se generó o está vacío.")
        return 1
    print(f"[INFORME] PDF generado: {PDF_PATH} ({PDF_PATH.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
