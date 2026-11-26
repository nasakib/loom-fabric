"""
Universal Multimodal File Analyzer (`loom/clothos/universal_file_analyzer.py`).

Inspects, extracts structured metadata, computes quantitative signals, and
chunks content for downstream ClothOS / Loom Fabric reasoning across ALL file types:
- Documents: PDF, DOCX, PPTX, XLSX/CSV/TSV, HTML, XML, RTF, Markdown, TXT
- Source Code & Config: Python (AST symbols), JS/TS, C/C++, Rust, JSON/JSONL, YAML, TOML, INI
- Databases: SQLite (.db, .sqlite, .sqlite3) schemas, row counts, sample rows
- Archives: ZIP, WHL, TAR, GZ, TGZ manifests
- Images: PNG, JPG, WEBP, GIF, BMP, TIFF, ICO, SVG (dimensions, EXIF, palette, edge/entropy via PIL+NumPy)
- Audio: WAV, FLAC, OGG, AIFF, MIDI, MP3 (sample rate, duration, RMS, FFT dominant harmonics)
- Video: AVI (RIFF avih/strh), MP4/MOV (ISOBMFF moov/mvhd/tkhd), MKV/WebM (EBML), animated GIF/WebP
- 3D / CAD / Scientific: STL, OBJ, STEP/STP, SCAD, CIF/mmCIF/PDB, NPY/NPZ
- Arbitrary Binaries: Magic bytes, Shannon entropy, printable strings, hex header preview
"""

from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
import math
import mimetypes
from pathlib import Path
import re
import sqlite3
import struct
import tarfile
from typing import Any, Dict, List, Optional, Tuple, Union
import wave
import zipfile

import numpy as np
from PIL import Image, ExifTags

try:
    import soundfile as sf
except Exception:
    sf = None

try:
    import yaml
except Exception:
    yaml = None

try:
    import tomllib
except Exception:
    tomllib = None


_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff", ".tif", ".ico"}
_AUDIO_EXTS = {".wav", ".flac", ".ogg", ".aiff", ".aif", ".mp3", ".m4a", ".mid", ".midi"}
_VIDEO_EXTS = {".avi", ".mp4", ".mov", ".m4v", ".mkv", ".webm"}
_DB_EXTS = {".db", ".sqlite", ".sqlite3"}
_ARCHIVE_EXTS = {".zip", ".whl", ".jar", ".tar", ".gz", ".tgz"}
_CAD_3D_EXTS = {".stl", ".obj", ".ply", ".step", ".stp", ".scad"}
_BIO_EXTS = {".cif", ".mmcif", ".pdb", ".ent"}
_DOC_EXTS = {".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls", ".csv", ".tsv", ".html", ".htm", ".xml", ".rtf", ".md", ".txt", ".log", ".rst", ".tex"}
_CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go", ".c", ".cpp", ".h", ".hpp", ".java", ".cs", ".ps1", ".bat", ".sh", ".sql", ".css", ".scss"}
_DATA_EXTS = {".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env", ".npy", ".npz"}
_NOTEBOOK_EXTS = {".ipynb"}


def _analyze_notebook(path: Path) -> Tuple[Dict[str, Any], str]:
    raw = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    cells = raw.get("cells", []) if isinstance(raw, dict) else []
    md_parts: List[str] = []
    code_parts: List[str] = []
    headings: List[str] = []
    for idx, cell in enumerate(cells):
        if not isinstance(cell, dict):
            continue
        ctype = cell.get("cell_type", "unknown")
        src_raw = cell.get("source", "")
        src = "".join(src_raw) if isinstance(src_raw, list) else str(src_raw)
        if ctype == "markdown":
            for ln in src.splitlines():
                if ln.lstrip().startswith("#"):
                    headings.append(ln.strip()[:120])
            md_parts.append(f"[Cell {idx} MD]\n{src.strip()}")
        elif ctype == "code":
            code_parts.append(f"[Cell {idx} CODE]\n{src.strip()}")

    meta = {
        "format": "Jupyter Notebook (.ipynb)",
        "nbformat": raw.get("nbformat"),
        "total_cells": len(cells),
        "markdown_cells": len(md_parts),
        "code_cells": len(code_parts),
        "headings": headings[:25],
    }
    combined = "\n\n".join(md_parts[:30] + code_parts[:30])
    return meta, f"Notebook {path.name}: {len(cells)} cells ({len(md_parts)} md, {len(code_parts)} code).\n\n{combined}"


def _chunk_text(text: str, chunk_size: int = 1500) -> List[str]:
    clean = (text or "").strip()
    if not clean:
        return []
    return [clean[i : i + chunk_size] for i in range(0, len(clean), chunk_size)]


def _shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    total = float(len(data))
    return round(-sum((c / total) * math.log2(c / total) for c in counts.values()), 4)


def _detect_magic(header: bytes) -> str:
    if header.startswith(b"%PDF-"):
        return "PDF document"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG image"
    if header.startswith(b"\xff\xd8\xff"):
        return "JPEG image"
    if header.startswith((b"GIF87a", b"GIF89a")):
        return "GIF image/animation"
    if header.startswith(b"RIFF") and len(header) >= 12:
        sub = header[8:12].decode("ascii", errors="replace")
        return f"RIFF ({sub})"
    if header.startswith(b"fLaC"):
        return "FLAC audio"
    if header.startswith(b"OggS"):
        return "Ogg container"
    if header.startswith(b"MThd"):
        return "Standard MIDI"
    if header.startswith(b"SQLite format 3"):
        return "SQLite 3 database"
    if header.startswith(b"PK\x03\x04"):
        return "ZIP/OOXML archive"
    if header.startswith(b"\x1f\x8b"):
        return "GZIP stream"
    if header.startswith(b"\x1a\x45\xdf\xa3"):
        return "EBML (MKV/WebM video)"
    if len(header) >= 12 and header[4:8] == b"ftyp":
        brand = header[8:12].decode("ascii", errors="replace")
        return f"ISOBMFF (MP4/MOV brand={brand})"
    if header.startswith(b"ID3") or (len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0):
        return "MP3 / MPEG audio"
    if header.startswith(b"MZ"):
        return "Windows PE/COFF executable/DLL"
    if header.startswith(b"\x7fELF"):
        return "ELF executable/library"
    if header.lstrip().startswith((b"<svg", b"<?xml", b"<!DOCTYPE html", b"<html")):
        return "XML/HTML/SVG markup"
    if header.lstrip().startswith(b"ISO-10303-21"):
        return "STEP AP214/AP203 CAD"
    return "Generic / Text or Raw Binary"


def _analyze_image(path: Path) -> Tuple[Dict[str, Any], str]:
    with Image.open(path) as img:
        n_frames = int(getattr(img, "n_frames", 1))
        meta: Dict[str, Any] = {
            "format": img.format,
            "mode": img.mode,
            "width": img.width,
            "height": img.height,
            "aspect_ratio": round(img.width / max(1, img.height), 4),
            "n_frames": n_frames,
            "is_animated": n_frames > 1,
        }
        exif_dict: Dict[str, str] = {}
        try:
            raw_exif = img.getexif()
            if raw_exif:
                for tag_id, val in list(raw_exif.items())[:16]:
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    exif_dict[str(tag_name)] = str(val)[:120]
        except Exception:
            pass
        if exif_dict:
            meta["exif"] = exif_dict

        rgb = img.convert("RGB")
        # Downsample cleanly for fast palette + edge energy analytics
        thumb = rgb.resize((min(128, max(16, img.width)), min(128, max(16, img.height))))
        arr = np.asarray(thumb, dtype=np.float32)
        mean_rgb = [round(float(x), 1) for x in arr.mean(axis=(0, 1))]
        gray = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
        gx = np.abs(np.diff(gray, axis=1)).mean() if gray.shape[1] > 1 else 0.0
        gy = np.abs(np.diff(gray, axis=0)).mean() if gray.shape[0] > 1 else 0.0

        # Top quantized hex colors
        quant = thumb.quantize(colors=5).convert("RGB")
        q_colors = quant.getcolors(maxcolors=256) or []
        q_colors.sort(key=lambda x: x[0], reverse=True)
        palette = [f"#{r:02x}{g:02x}{b:02x}" for _, (r, g, b) in q_colors[:5]]

        motion_delta = None
        if n_frames > 1:
            try:
                f0 = np.asarray(rgb.resize((64, 64)), dtype=np.float32)
                img.seek(min(1, n_frames - 1))
                f1 = np.asarray(img.convert("RGB").resize((64, 64)), dtype=np.float32)
                motion_delta = round(float(np.mean(np.abs(f1 - f0))), 2)
            except Exception:
                pass

        meta.update({
            "mean_rgb": mean_rgb,
            "brightness_mean": round(float(gray.mean()), 2),
            "contrast_std": round(float(gray.std()), 2),
            "edge_energy": round(float(gx + gy), 2),
            "dominant_palette": palette,
        })
        if motion_delta is not None:
            meta["frame_motion_delta"] = motion_delta

    summary = (
        f"Image {path.name}: {meta['format']} {meta['width']}x{meta['height']} ({meta['mode']}), "
        f"frames={meta['n_frames']}, brightness={meta['brightness_mean']}, contrast={meta['contrast_std']}, "
        f"edge_energy={meta['edge_energy']}, palette={meta['dominant_palette']}."
    )
    return meta, summary


def _analyze_audio(path: Path) -> Tuple[Dict[str, Any], str]:
    ext = path.suffix.lower()
    if ext in (".mid", ".midi"):
        raw = path.read_bytes()
        if raw.startswith(b"MThd") and len(raw) >= 14:
            hdr_len, fmt, n_tracks, tpqn = struct.unpack(">IHHH", raw[4:14])
            note_on_est = raw.count(b"\x90")
            meta = {"format": "MIDI", "midi_format": fmt, "tracks": n_tracks, "ticks_per_quarter": tpqn, "approx_note_events": note_on_est, "header_len": hdr_len}
            return meta, f"MIDI {path.name}: format={fmt}, tracks={n_tracks}, TPQN={tpqn}, ~{note_on_est} note-on bytes."

    sr, channels, frames, subtype = 0, 0, 0, ""
    samples = None
    if sf is not None:
        try:
            info = sf.info(str(path))
            sr, channels, frames, subtype = int(info.samplerate), int(info.channels), int(info.frames), str(info.subtype)
            max_read = min(frames, max(sr * 15, 44100)) if sr else 441000
            data, sr_r = sf.read(str(path), frames=max_read, dtype="float32", always_2d=True)
            sr = sr or int(sr_r)
            samples = data.mean(axis=1)
        except Exception:
            samples = None

    if samples is None and ext == ".wav":
        with wave.open(str(path), "rb") as wf:
            sr = wf.getframerate()
            channels = wf.getnchannels()
            frames = wf.getnframes()
            sw = wf.getsampwidth()
            subtype = f"PCM_{sw * 8}"
            raw_b = wf.readframes(min(frames, max(sr * 15, 44100)))
            if sw == 2:
                arr = np.frombuffer(raw_b, dtype=np.int16).astype(np.float32) / 32768.0
                if channels > 1:
                    arr = arr.reshape(-1, channels).mean(axis=1)
                samples = arr

    if samples is not None and samples.size > 64 and sr > 0:
        rms = float(np.sqrt(np.mean(samples ** 2)))
        peak = float(np.max(np.abs(samples)))
        win = min(len(samples), 65536)
        spec = np.abs(np.fft.rfft(samples[:win] * np.hanning(win)))
        freqs = np.fft.rfftfreq(win, d=1.0 / sr)
        spec_sum = float(np.sum(spec)) + 1e-12
        centroid = float(np.sum(freqs * spec) / spec_sum)
        top_idx = np.argsort(spec)[-5:][::-1]
        top_freqs = [round(float(freqs[i]), 1) for i in top_idx if freqs[i] > 10.0]
        duration_s = round(frames / max(1, sr), 3)
        meta = {
            "sample_rate": sr,
            "channels": channels,
            "total_frames": frames,
            "duration_s": duration_s,
            "subtype": subtype,
            "rms": round(rms, 5),
            "peak": round(peak, 5),
            "peak_dbfs": round(20.0 * math.log10(max(1e-7, peak)), 2),
            "spectral_centroid_hz": round(centroid, 1),
            "dominant_frequencies_hz": top_freqs,
        }
        return meta, (
            f"Audio {path.name}: {duration_s}s @ {sr}Hz ({channels}ch, {subtype}), "
            f"RMS={meta['rms']}, Peak={meta['peak_dbfs']}dBFS, Centroid={meta['spectral_centroid_hz']}Hz, Peaks={top_freqs}."
        )

    meta = {"format": ext.lstrip(".").upper(), "size_bytes": path.stat().st_size}
    return meta, f"Audio {path.name}: compressed/container audio ({meta['size_bytes']} bytes)."


def _analyze_video(path: Path) -> Tuple[Dict[str, Any], str]:
    raw = path.read_bytes()
    ext = path.suffix.lower()
    meta: Dict[str, Any] = {"container": ext.lstrip(".").upper(), "size_bytes": len(raw)}

    if raw.startswith(b"RIFF") and len(raw) >= 12 and raw[8:12] == b"AVI ":
        avih_idx = raw.find(b"avih")
        if avih_idx != -1 and avih_idx + 64 <= len(raw):
            vals = struct.unpack("<14I", raw[avih_idx + 8 : avih_idx + 64])
            us_per_frame, _, _, _, total_frames, _, num_streams, _, width, height = vals[:10]
            fps = round(1_000_000.0 / max(1, us_per_frame), 2)
            dur = round(total_frames / max(0.01, fps), 2)
            codecs = re.findall(rb"strh.{4}([a-zA-Z0-9_ ]{4})([a-zA-Z0-9_ ]{4})", raw[:16384], re.DOTALL)
            meta.update({
                "container": "RIFF AVI",
                "width": width,
                "height": height,
                "fps": fps,
                "total_frames": total_frames,
                "duration_s": dur,
                "streams": num_streams,
                "codecs": [{"type": t.decode("ascii", "replace"), "fourcc": f.decode("ascii", "replace")} for t, f in codecs[:4]],
            })
            return meta, (
                f"Video AVI {path.name}: {width}x{height} @ {fps} FPS, {total_frames} frames ({dur}s), streams={num_streams}."
            )

    if len(raw) >= 16 and raw[4:8] == b"ftyp":
        brand = raw[8:12].decode("ascii", errors="replace")
        meta["container"] = f"ISOBMFF ({brand})"
        mvhd_pos = raw.find(b"mvhd")
        if mvhd_pos != -1 and mvhd_pos + 24 <= len(raw):
            ver = raw[mvhd_pos + 4]
            if ver == 0 and mvhd_pos + 24 <= len(raw):
                timescale, dur_u = struct.unpack(">II", raw[mvhd_pos + 16 : mvhd_pos + 24])
                if timescale > 0:
                    meta["duration_s"] = round(dur_u / timescale, 2)
        tkhd_pos = raw.find(b"tkhd")
        if tkhd_pos != -1 and tkhd_pos + 88 <= len(raw):
            w_fp, h_fp = struct.unpack(">II", raw[tkhd_pos + 80 : tkhd_pos + 88])
            if w_fp > 0 and h_fp > 0:
                meta["width"] = round(w_fp / 65536.0)
                meta["height"] = round(h_fp / 65536.0)
        return meta, f"Video MP4/MOV {path.name}: brand={brand}, duration={meta.get('duration_s', '?')}s, size={len(raw)} bytes."

    return meta, f"Video container {path.name}: {meta['container']} ({len(raw)} bytes)."


def _analyze_database(path: Path) -> Tuple[Dict[str, Any], str]:
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        table_info: Dict[str, Any] = {}
        samples_txt: List[str] = []
        for tbl in tables[:20]:
            safe_tbl = tbl.replace('"', '""')
            cnt = cur.execute(f'SELECT COUNT(*) FROM "{safe_tbl}"').fetchone()[0]
            cols = [r[1] for r in cur.execute(f'PRAGMA table_info("{safe_tbl}")').fetchall()]
            rows = cur.execute(f'SELECT * FROM "{safe_tbl}" LIMIT 5').fetchall()
            table_info[tbl] = {"rows": cnt, "columns": cols}
            samples_txt.append(f"## Table `{tbl}` ({cnt} rows)\nColumns: {cols}\nSample rows:\n" + "\n".join(str(r) for r in rows))
        meta = {"table_count": len(tables), "tables": table_info}
        return meta, f"SQLite DB {path.name}: {len(tables)} tables.\n\n" + "\n\n".join(samples_txt)
    finally:
        conn.close()


def _analyze_archive(path: Path) -> Tuple[Dict[str, Any], str]:
    members: List[Dict[str, Any]] = []
    if path.suffix.lower() in (".zip", ".whl", ".jar") or zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, "r") as zf:
            for info in zf.infolist()[:300]:
                members.append({"name": info.filename, "size": info.file_size, "compressed": info.compress_size})
        total_entries = len(members)
        text = f"ZIP Archive {path.name} ({total_entries} listed entries):\n" + "\n".join(
            f"- {m['name']} ({m['size']} bytes)" for m in members[:80]
        )
        return {"archive_type": "zip", "entries_sampled": total_entries, "members": members[:50]}, text
    elif path.suffix.lower() in (".tar", ".tgz", ".gz"):
        try:
            with tarfile.open(path, "r:*") as tf:
                for m in tf.getmembers()[:200]:
                    members.append({"name": m.name, "size": m.size, "is_file": m.isfile()})
            text = f"TAR Archive {path.name} ({len(members)} entries):\n" + "\n".join(
                f"- {m['name']} ({m['size']} bytes)" for m in members[:80]
            )
            return {"archive_type": "tar", "entries_sampled": len(members), "members": members[:50]}, text
        except Exception:
            pass
    return {"archive_type": "compressed_blob"}, f"Compressed archive {path.name} ({path.stat().st_size} bytes)."


def _analyze_3d_or_bio(path: Path) -> Tuple[Dict[str, Any], str]:
    ext = path.suffix.lower()
    raw = path.read_bytes()
    if ext == ".stl":
        if not raw.lstrip().startswith(b"solid") and len(raw) >= 84:
            tri_count = struct.unpack("<I", raw[80:84])[0]
            header_txt = raw[:80].decode("ascii", errors="ignore").strip("\x00 ")
            meta = {"format": "Binary STL", "triangles": tri_count, "header": header_txt}
            return meta, f"3D Binary STL {path.name}: {tri_count} triangles, header='{header_txt}'."
        txt = raw.decode("utf-8", errors="replace")
        facets = txt.count("facet normal")
        return {"format": "ASCII STL", "triangles": facets}, f"3D ASCII STL {path.name}: {facets} facets.\n\n{txt[:2500]}"

    txt = raw.decode("utf-8", errors="replace")
    if ext in _BIO_EXTS:
        atoms = [ln for ln in txt.splitlines() if ln.startswith(("ATOM", "HETATM"))]
        return {"format": ext.lstrip(".").upper(), "atom_records": len(atoms)}, f"Biomolecular Structure {path.name}: {len(atoms)} atom records.\n\n{txt[:3000]}"

    lines = txt.splitlines()
    return {"format": ext.lstrip(".").upper(), "line_count": len(lines)}, f"CAD/3D {path.name}: {len(lines)} lines.\n\n{txt[:3000]}"


def analyze_any_file(file_path: Union[str, Path], chunk_size: int = 1500) -> Dict[str, Any]:
    """
    Universal entry point analyzing ANY file type safely and returning structured
    metadata, natural-language summary, and paginated text chunks.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return {"status": "ERROR", "error": f"File not found: {path}"}

    ext = path.suffix.lower()
    stat = path.stat()
    raw_head = path.read_bytes()[:4096]
    sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    magic = _detect_magic(raw_head)
    mime_guess, _ = mimetypes.guess_type(str(path))
    mime_type = mime_guess or ("application/octet-stream" if b"\x00" in raw_head[:512] else "text/plain")
    entropy = _shannon_entropy(raw_head)

    meta: Dict[str, Any] = {}
    body_text = ""
    category = "binary"

    try:
        if ext in _IMAGE_EXTS or (magic.startswith(("PNG", "JPEG", "GIF")) and ext != ".avi"):
            category = "image"
            meta, body_text = _analyze_image(path)
        elif ext in _AUDIO_EXTS or magic.startswith(("RIFF (WAVE)", "FLAC", "Ogg", "Standard MIDI", "MP3")):
            category = "audio"
            meta, body_text = _analyze_audio(path)
        elif ext in _VIDEO_EXTS or magic.startswith(("RIFF (AVI", "EBML", "ISOBMFF")):
            category = "video"
            meta, body_text = _analyze_video(path)
        elif ext in _DB_EXTS or magic.startswith("SQLite"):
            category = "database"
            meta, body_text = _analyze_database(path)
        elif ext in _ARCHIVE_EXTS or (magic.startswith("ZIP") and ext not in (".docx", ".pptx", ".xlsx")):
            category = "archive"
            meta, body_text = _analyze_archive(path)
        elif ext in _CAD_3D_EXTS:
            category = "cad_3d"
            meta, body_text = _analyze_3d_or_bio(path)
        elif ext in _BIO_EXTS:
            category = "biomolecular"
            meta, body_text = _analyze_3d_or_bio(path)
        elif ext in (".npy", ".npz"):
            category = "data"
            loaded = np.load(str(path), allow_pickle=False)
            if isinstance(loaded, np.lib.npyio.NpzFile):
                shapes = {k: {"shape": list(loaded[k].shape), "dtype": str(loaded[k].dtype)} for k in loaded.files[:20]}
                meta = {"format": "NPZ", "arrays": shapes}
                body_text = f"NumPy NPZ archive {path.name}: keys={list(shapes.keys())}, details={json.dumps(shapes)}"
            else:
                meta = {"format": "NPY", "shape": list(loaded.shape), "dtype": str(loaded.dtype), "min": float(np.min(loaded)), "max": float(np.max(loaded)), "mean": float(np.mean(loaded))}
                body_text = f"NumPy NPY tensor {path.name}: {json.dumps(meta)}"
        elif ext == ".svg":
            category = "image"
            txt = path.read_text(encoding="utf-8", errors="replace")
            meta = {"format": "SVG", "paths": txt.count("<path"), "circles": txt.count("<circle"), "polygons": txt.count("<polygon")}
            body_text = f"Vector SVG {path.name} ({meta}):\n{txt[:4000]}"
        elif ext in _NOTEBOOK_EXTS:
            category = "notebook"
            meta, body_text = _analyze_notebook(path)
        elif ext in _DOC_EXTS or magic.startswith("PDF"):
            category = "document"
            from loom.clothos.doc_parser import parse_document_text_only
            doc_res = parse_document_text_only(path, chunk_size=chunk_size)
            meta = {k: v for k, v in doc_res.items() if k not in ("chunks", "full_text", "raw_text")}
            body_text = "\n".join(doc_res.get("chunks", [])) or str(doc_res)
        elif ext in _DATA_EXTS:
            category = "data"
            txt = path.read_text(encoding="utf-8", errors="replace")
            if ext == ".json":
                obj = json.loads(txt)
                meta = {"format": "JSON", "root_type": type(obj).__name__, "top_keys": list(obj.keys())[:25] if isinstance(obj, dict) else len(obj)}
            elif ext == ".jsonl":
                lines = [ln for ln in txt.splitlines() if ln.strip()]
                meta = {"format": "JSONL", "record_count": len(lines)}
            elif ext in (".yaml", ".yml") and yaml is not None:
                obj = yaml.safe_load(txt)
                meta = {"format": "YAML", "root_type": type(obj).__name__}
            elif ext == ".toml" and tomllib is not None:
                obj = tomllib.loads(txt)
                meta = {"format": "TOML", "top_keys": list(obj.keys())[:25]}
            body_text = txt
        elif ext in _CODE_EXTS or b"\x00" not in raw_head[:512]:
            category = "code" if ext in _CODE_EXTS else "text"
            txt = path.read_text(encoding="utf-8", errors="replace")
            if ext == ".py":
                tree = ast.parse(txt)
                classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                funcs = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                meta = {"language": "Python", "lines": txt.count("\n") + 1, "classes": classes[:40], "functions": funcs[:60]}
            else:
                meta = {"lines": txt.count("\n") + 1, "language": ext.lstrip(".") or "text"}
            body_text = txt
        else:
            category = "binary"
            all_bytes = path.read_bytes()
            strings = re.findall(rb"[ -~]{5,80}", all_bytes[:262144])
            decoded_strings = [s.decode("ascii", errors="ignore") for s in strings[:40]]
            hex_preview = " ".join(f"{b:02x}" for b in raw_head[:96])
            meta = {"entropy_bits_per_byte": entropy, "printable_strings_count": len(strings), "hex_preview": hex_preview}
            body_text = f"Binary file {path.name} ({magic}, {stat.st_size} bytes, entropy={entropy}):\nHex[0:96]: {hex_preview}\nSample strings:\n" + "\n".join(decoded_strings)
    except Exception as exc:
        meta["analysis_note"] = str(exc)
        if not body_text:
            body_text = f"File {path.name} ({magic}, {stat.st_size} bytes). Inspection note: {exc}"

    chunks = _chunk_text(body_text, chunk_size=max(200, int(chunk_size)))
    return {
        "status": "SUCCESS",
        "file_path": str(path),
        "file_name": path.name,
        "extension": ext,
        "category": category,
        "mime_type": mime_type,
        "magic_signature": magic,
        "size_bytes": stat.st_size,
        "sha256": sha256,
        "entropy": entropy,
        "metadata": meta,
        "summary": chunks[0][:600] if chunks else f"{category}: {path.name}",
        "chunks": chunks,
        "total_chunks": len(chunks),
    }
