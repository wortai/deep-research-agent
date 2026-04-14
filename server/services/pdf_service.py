import os
import sys
import glob
import tempfile
import uuid
import logging

logger = logging.getLogger(__name__)

_BREW_LIB_DIRS = [
    p for p in ("/opt/homebrew/lib", "/usr/local/lib") if os.path.isdir(p)
]

if _BREW_LIB_DIRS and sys.platform == "darwin":
    try:
        import cffi as _cffi_mod

        _orig_dlopen = _cffi_mod.FFI.dlopen

        def _patched_dlopen(self, name, flags=0):
            try:
                return _orig_dlopen(self, name, flags)
            except OSError:
                basename = os.path.basename(name)
                for libdir in _BREW_LIB_DIRS:
                    full = os.path.join(libdir, basename)
                    for candidate in (full, full + ".dylib", full + ".0.dylib"):
                        if os.path.exists(candidate):
                            try:
                                return _orig_dlopen(self, candidate, flags)
                            except OSError:
                                continue
                    for match in sorted(
                        glob.glob(os.path.join(libdir, basename + "*"))
                    ):
                        if match.endswith(".dylib"):
                            try:
                                return _orig_dlopen(self, match, flags)
                            except OSError:
                                continue
                raise

        _cffi_mod.FFI.dlopen = _patched_dlopen
    except ImportError:
        pass

_weasyprint_error = None
try:
    from weasyprint import HTML
except (OSError, ImportError, Exception) as e:
    HTML = None
    _weasyprint_error = f"{type(e).__name__}: {e}"

_xhtml2pdf_available = False
try:
    from xhtml2pdf import pisa

    _xhtml2pdf_available = True
except ImportError:
    pisa = None

if HTML is not None:
    logger.info("[PDF] WeasyPrint loaded")
elif _xhtml2pdf_available:
    logger.warning(
        f"[PDF] WeasyPrint unavailable ({_weasyprint_error}), using xhtml2pdf fallback"
    )
else:
    logger.error(f"[PDF] No PDF engine available. WeasyPrint: {_weasyprint_error}")

from server.api.schemas import ReportData


_PDF_CSS = """\
    @page {{
        size: A4;
        margin: 20mm 15mm;
    }}
    *, *::before, *::after {{ box-sizing: border-box; }}
    html, body {{
        margin: 0;
        padding: 0;
        background: white;
        font-family: 'General Sans', 'Inter', sans-serif;
        font-size: 14px;
        line-height: 1.7;
        color: #2d3748;
        overflow-wrap: break-word;
    }}
    .report-page {{
        width: 100%;
        page-break-after: always;
    }}
    .report-page:last-child {{
        page-break-after: auto;
    }}
    .report-chapter {{
        margin: 0;
    }}
    .report-page > div,
    .report-page > section,
    .report-page > figure,
    .report-page > aside,
    .report-page > blockquote {{
        break-inside: avoid;
        page-break-inside: avoid;
    }}
    p {{ orphans: 3; widows: 3; }}
    img, svg, video, canvas {{ max-width: 100% !important; height: auto; }}
    pre, code {{ white-space: pre-wrap !important; word-break: break-all; }}
    pre {{ overflow-x: hidden; max-width: 100%; }}
    table {{
        table-layout: fixed;
        width: 100%;
        border-collapse: collapse;
        break-inside: avoid;
        page-break-inside: avoid;
    }}
    tr {{ break-inside: avoid; page-break-inside: avoid; }}
    td, th {{ word-wrap: break-word; overflow-wrap: break-word; }}
    svg, pre {{ break-inside: avoid; page-break-inside: avoid; }}
    a {{ color: #2c5282; text-decoration: none; }}
"""


def _assemble_pdf_html(report: ReportData) -> str:
    """Builds the HTML document matching the frontend iframe with print-optimised CSS."""
    toc_raw = report.table_of_contents or ""
    toc_page = f'<div class="report-page">{toc_raw}</div>' if toc_raw else ""

    body_html = "\n".join(
        s.section_content
        for s in sorted(report.body_sections, key=lambda s: s.section_order)
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Research Report</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=General+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/charts.css/dist/charts.min.css">
    <style>
{_PDF_CSS}
    </style>
</head>
<body>
{toc_page}
{body_html}
</body>
</html>"""


def generate_pdf_from_report(report: ReportData) -> str:
    """Generates a PDF matching the on-screen report viewer. Tries WeasyPrint first."""
    html_content = _assemble_pdf_html(report)
    temp_dir = tempfile.gettempdir()
    task_id = uuid.uuid4().hex
    out_path = os.path.join(temp_dir, f"{task_id}_report.pdf")

    if HTML is not None:
        try:
            HTML(string=html_content).write_pdf(out_path)
            return out_path
        except Exception as e:
            logger.warning(
                f"[PDF] WeasyPrint render failed: {e}, trying xhtml2pdf fallback"
            )

    if _xhtml2pdf_available and pisa is not None:
        try:
            from io import BytesIO

            result = BytesIO()
            pisa.CreatePDF(
                BytesIO(html_content.encode("utf-8")),
                result,
                encoding="utf-8",
            )
            with open(out_path, "wb") as f:
                f.write(result.getvalue())
            return out_path
        except Exception as e:
            logger.error(f"[PDF] xhtml2pdf fallback failed: {e}")

    raise RuntimeError(
        "No PDF engine available. Install WeasyPrint system deps "
        "(brew install pango cairo gdk-pixbuf libffi) or pip install xhtml2pdf."
    )
