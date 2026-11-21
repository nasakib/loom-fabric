"""
Multi-Format Document Parsing & Extraction Engine (`loom/clothos/doc_parser.py`).

Adapted from Qwen-Agent's simple_doc_parser & doc_parser architectures:
- Extracts structured content from PDF, DOCX, PPTX, XLSX, CSV, HTML, and Markdown/TXT.
- Native fallback parsers using Python standard library (zipfile XML parsing) when 
  third-party packages (docx, pptx, pypdf) are not installed.
- Generates structured token-friendly chunks with page numbers and markdown tables.
"""

from __future__ import annotations

import csv
import html
import io
import json
import os
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


def clean_text(text: str) -> str:
    """Sanitizes text by removing continuous whitespace and unprintable control chars."""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def parse_pdf(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Extracts text per page from PDF using available PDF libraries or text fallback."""
    path = Path(file_path).resolve()
    pages = []
    
    # 1. Try pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(str(path))
        for idx, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            pages.append({"page": idx + 1, "text": clean_text(txt)})
        if pages:
            return pages
    except Exception:
        pass

    # 2. Try fitz (PyMuPDF)
    try:
        import fitz
        doc = fitz.open(str(path))
        for idx, page in enumerate(doc):
            pages.append({"page": idx + 1, "text": clean_text(page.get_text())})
        if pages:
            return pages
    except Exception:
        pass

    # 3. Fallback: Raw stream extraction
    try:
        data = path.read_bytes()
        streams = re.findall(rb'stream[\r\n]+(.*?)[\r\n]+endstream', data, re.DOTALL)
        extracted = []
        for s in streams:
            try:
                import zlib
                decomp = zlib.decompress(s)
                words = re.findall(rb'\((.*?)\)', decomp)
                if words:
                    extracted.append(b' '.join(words).decode('latin1', errors='ignore'))
            except Exception:
                pass
        full_text = "\n".join(extracted)
        return [{"page": 1, "text": clean_text(full_text)}]
    except Exception as exc:
        return [{"page": 1, "error": f"Failed to parse PDF: {exc}"}]


def parse_docx(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Extracts paragraphs and tables from DOCX using python-docx or native zipfile XML."""
    path = Path(file_path).resolve()
    
    # 1. Try python-docx
    try:
        import docx
        doc = docx.Document(str(path))
        content = []
        for p in doc.paragraphs:
            if p.text.strip():
                content.append(clean_text(p.text))
        for table in doc.tables:
            tbl_rows = []
            for row in table.rows:
                cells = [clean_text(cell.text) for cell in row.cells]
                tbl_rows.append("| " + " | ".join(cells) + " |")
            if tbl_rows:
                content.append("\n" + "\n".join(tbl_rows) + "\n")
        return [{"page": 1, "text": "\n\n".join(content)}]
    except Exception:
        pass

    # 2. Zero-dependency fallback: extract word/document.xml from docx zip
    try:
        with zipfile.ZipFile(str(path), 'r') as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            # Find all text nodes <w:t>
            texts = []
            for elem in tree.iter():
                if elem.tag.endswith('}t') and elem.text:
                    texts.append(elem.text)
                elif elem.tag.endswith('}p'):
                    texts.append('\n')
            full = ''.join(texts)
            return [{"page": 1, "text": clean_text(full)}]
    except Exception as exc:
        return [{"page": 1, "error": f"Failed to parse DOCX: {exc}"}]


def parse_pptx(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Extracts text per slide from PPTX using python-pptx or native zipfile XML."""
    path = Path(file_path).resolve()
    
    # 1. Try python-pptx
    try:
        import pptx
        prs = pptx.Presentation(str(path))
        slides = []
        for idx, slide in enumerate(prs.slides):
            slide_texts = []
            for shape in slide.shapes:
                if shape.has_text_frame:
                    slide_texts.append(shape.text_frame.text)
            slides.append({"slide": idx + 1, "text": clean_text("\n".join(slide_texts))})
        return slides
    except Exception:
        pass

    # 2. Zero-dependency fallback: extract slide XMLs
    try:
        slides = []
        with zipfile.ZipFile(str(path), 'r') as z:
            slide_files = sorted([f for f in z.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')])
            for idx, sf in enumerate(slide_files):
                tree = ET.fromstring(z.read(sf))
                texts = [elem.text for elem in tree.iter() if elem.tag.endswith('}t') and elem.text]
                slides.append({"slide": idx + 1, "text": clean_text(" ".join(texts))})
        return slides if slides else [{"slide": 1, "text": ""}]
    except Exception as exc:
        return [{"slide": 1, "error": f"Failed to parse PPTX: {exc}"}]


def parse_tabular(file_path: Union[str, Path], max_rows: int = 100) -> List[Dict[str, Any]]:
    """Parses CSV, TSV, or Excel spreadsheets into formatted Markdown tables."""
    path = Path(file_path).resolve()
    suffix = path.suffix.lower()

    if suffix in ('.csv', '.tsv'):
        delimiter = '\t' if suffix == '.tsv' else ','
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)
            if not rows:
                return [{"table": "", "row_count": 0}]
            headers = rows[0]
            data_rows = rows[1:max_rows + 1]
            md_lines = [
                "| " + " | ".join(headers) + " |",
                "| " + " | ".join(["---"] * len(headers)) + " |",
            ]
            for r in data_rows:
                # pad or truncate to header length
                cells = [str(r[i]) if i < len(r) else "" for i in range(len(headers))]
                md_lines.append("| " + " | ".join(cells) + " |")
            return [{
                "table": "\n".join(md_lines),
                "total_rows": len(rows) - 1,
                "displayed_rows": len(data_rows),
            }]
        except Exception as exc:
            return [{"error": f"Failed to parse CSV/TSV: {exc}"}]

    elif suffix in ('.xlsx', '.xls'):
        try:
            import pandas as pd
            xls = pd.ExcelFile(str(path))
            sheets = []
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name, nrows=max_rows)
                sheets.append({
                    "sheet": sheet_name,
                    "table": df.to_markdown(index=False),
                    "shape": f"{len(df)} rows x {len(df.columns)} cols",
                })
            return sheets
        except Exception as exc:
            return [{"error": f"Failed to parse Excel: {exc}"}]

    return [{"error": f"Unsupported tabular format: {suffix}"}]


def parse_document(file_path: Union[str, Path], chunk_size: int = 1500) -> Dict[str, Any]:
    """Unified document parser dispatcher returning structured chunks and metadata."""
    path = Path(file_path).resolve()
    if not path.exists():
        return {"success": False, "error": f"File not found: {path}"}

    suffix = path.suffix.lower()
    file_type = suffix.lstrip('.')
    metadata = {
        "file_name": path.name,
        "file_path": str(path),
        "file_size_bytes": path.stat().st_size,
        "extension": suffix,
    }

    if suffix == '.pdf':
        pages = parse_pdf(path)
        full_text = "\n\n".join([f"--- Page {p.get('page', 1)} ---\n{p.get('text', '')}" for p in pages])
    elif suffix in ('.docx', '.doc'):
        pages = parse_docx(path)
        full_text = pages[0].get('text', '') if pages else ''
    elif suffix in ('.pptx', '.ppt'):
        slides = parse_pptx(path)
        full_text = "\n\n".join([f"--- Slide {s.get('slide', 1)} ---\n{s.get('text', '')}" for s in slides])
    elif suffix in ('.csv', '.tsv', '.xlsx', '.xls'):
        tables = parse_tabular(path)
        full_text = json.dumps(tables, indent=2)
    elif suffix in ('.html', '.htm'):
        raw = path.read_text(encoding='utf-8', errors='replace')
        # strip tags
        text = re.sub(r'<[^>]+>', ' ', raw)
        full_text = clean_text(html.unescape(text))
    else:
        # Standard text, markdown, code
        full_text = clean_text(path.read_text(encoding='utf-8', errors='replace'))

    # Break into token-friendly chunks
    chunks = []
    paragraphs = full_text.split('\n\n')
    current_chunk = []
    current_len = 0
    for p in paragraphs:
        p_len = len(p)
        if current_len + p_len > chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [p]
            current_len = p_len
        else:
            current_chunk.append(p)
            current_len += p_len
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return {
        "success": True,
        "metadata": metadata,
        "total_characters": len(full_text),
        "total_chunks": len(chunks),
        "chunks": chunks,
        "full_text_preview": full_text[:2000] + ("..." if len(full_text) > 2000 else ""),
    }
