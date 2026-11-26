"""
Unit and Integration Tests for STEM Art Differential Signal Engine & CAD/SVG Synthesizers
(`tests/test_art_differential.py`).
"""

import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from loom.clothos.art_differential import (
    ArtSignal,
    ArtSignalAnalyzer,
    ArtDifferentialEngine,
    StemCadEngine,
    StemSvgEngine,
    art_differential_engine,
    stem_cad_engine,
    stem_svg_engine,
)
from loom.clothos.creative_art import creative_art_engine
from loom.si.atelier import get_sovereign_atelier
from loom.fabric.dashboard_server import app


@pytest.fixture
def test_client():
    return TestClient(app)


def test_art_signal_analyzer_text():
    """Verifies physical signal extraction from mathematical poetry."""
    analyzer = ArtSignalAnalyzer()
    sample_poem = """### Canticle of the Conserved 2-Form
*Theme: FIDUCIARY_STEWARDSHIP • Fiduciary Alignment Invariant*

```latex
\\omega = \\sum_{i} dp_i \\wedge dq_i, \\quad d\\omega = 0
```

> **Dedication:** A meditation on Emmy Noether's theorem: that every continuous symmetry of nature yields an invariant truth.

**I. The Silicon Loam**
In the dark hollow of the chassis, where sixty-four amps turn current into thought.
The Kuramoto oscillators tilt, two thousand times each second.
"""
    sig = analyzer.analyze_text(
        text=sample_poem,
        title="Canticle of the Conserved 2-Form",
        medium="poetry",
        source_id="ART-POEM-TEST-1",
        formula=r"\omega = \sum dp_i \wedge dq_i",
    )
    assert sig.spectral_entropy > 0.0
    assert sig.fundamental_freq > 0.0
    assert 0.0 <= sig.symmetry_order <= 1.0
    assert sig.topology_betti[0] >= 1
    assert sig.stem_domain in analyzer.STEM_DOMAINS


def test_art_signal_analyzer_svg():
    """Verifies physical signal extraction from SVG vector art."""
    analyzer = ArtSignalAnalyzer()
    sample_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 900">
    <path d="M 100,100 L 200,200 L 300,100 Z" fill="none" stroke="#38bdf8"/>
    <circle cx="450" cy="450" r="20" fill="#10b981"/>
    <text x="40" y="835">f_CPU = 3.7 GHz | Kuramoto r = 0.950</text>
    <text x="40" y="878">Invariant: dω/dt = 0</text>
</svg>"""
    sig = analyzer.analyze_svg(
        svg_content=sample_svg,
        title="Resonant Test SVG",
        source_id="ART-SVG-TEST-1",
    )
    assert sig.fundamental_freq == 3700.0  # 3.7 GHz mapped to MHz
    assert sig.symmetry_order == 0.950
    assert sig.topology_betti[1] >= 1  # Closed loop Z


def test_differential_signal_engine():
    """Verifies Delta S calculation and deterministic generative seed synthesis."""
    engine = ArtDifferentialEngine()
    analyzer = ArtSignalAnalyzer()

    sig1 = analyzer.analyze_text("First Artwork Entropy Ground", "Poem 1", "poetry", "ART-001")
    sig2 = analyzer.analyze_text("Second Artwork Expanded Complex Phase Trajectory", "Poem 2", "poetry", "ART-002")

    diff = engine.compute_differential(sig1, sig2)
    assert diff.prior_id == "ART-001"
    assert diff.current_id == "ART-002"
    assert diff.seed_hash is not None
    assert diff.seed_int > 0
    assert diff.next_suggested_medium in engine.MEDIUM_CYCLE
    assert diff.next_stem_domain in engine.STEM_CYCLE
    assert diff.next_target_freq > 0.0


def test_stem_cad_engine_synthesis():
    """Verifies parametric 3D CAD solid generation, FreeCAD export, and files on disk."""
    engine = StemCadEngine()
    cad = engine.generate_cad_model(archetype="MICROWAVE_CAVITY_FILTER", title="Test Cavity Filter")

    assert cad["id"].startswith("CAD_")
    assert cad["medium"] == "cad_model"
    assert cad["stem_domain"] == "Electromagnetics"
    assert cad["volume_mm3"] > 0.0

    step_path = Path(cad["step_file"])
    stl_path = Path(cad["stl_file"])
    py_path = Path(cad["py_file"])
    svg_path = Path(cad["svg_file"])

    assert step_path.exists()
    assert stl_path.exists()
    assert py_path.exists()
    assert svg_path.exists()
    assert step_path.stat().st_size > 0
    assert stl_path.stat().st_size > 0


def test_stem_svg_engine_synthesis():
    """Verifies 2D precision STEM technical SVG schematic generation."""
    engine = StemSvgEngine()
    svg_res = engine.generate_stem_svg(archetype="SMITH_CHART_RF", title="Test Smith Chart")

    assert svg_res["id"].startswith("SVG_STEM_")
    assert svg_res["medium"] == "svg_stem"
    assert "SMITH CHART" in svg_res["svg_preview"]
    assert Path(svg_res["svg_file"]).exists()


def test_closed_loop_evolutionary_transmutation():
    """Verifies that creative_art_engine uses the differential seed across successive creations."""
    art1 = creative_art_engine.generate_art()
    assert "id" in art1
    assert art1["medium"] in creative_art_engine.MEDIUMS

    # Second generation should be seeded by art1's differential
    art2 = creative_art_engine.generate_art()
    assert "id" in art2
    assert "differential_seed" in art2 or art2.get("genesis") is not None


def test_sovereign_atelier_cad_and_svg_integration():
    """Verifies that SovereignAtelier can compose CAD and STEM SVG artifacts."""
    atelier = get_sovereign_atelier()
    cad_art = atelier.compose_stem_cad(title="Sovereign Resonant Chamber")
    assert cad_art.art_form == "STEM_CAD_MODEL"
    assert cad_art.theme in ArtSignalAnalyzer.STEM_DOMAINS

    svg_art = atelier.compose_stem_svg(title="Sovereign Poincare Section")
    assert svg_art.art_form == "STEM_SVG_DRAWING"
    assert svg_art.theme in ArtSignalAnalyzer.STEM_DOMAINS


def test_dashboard_differential_endpoints(test_client):
    """Verifies REST endpoints for differential history and STEM composition."""
    res_latest = test_client.get("/api/art/differential/latest")
    assert res_latest.status_code == 200

    res_hist = test_client.get("/api/art/differential/history")
    assert res_hist.status_code == 200
    assert isinstance(res_hist.json(), list)

    res_cad = test_client.post("/api/art/compose/cad", json={"title": "API Test Solid"})
    assert res_cad.status_code == 200
    assert res_cad.json()["success"] is True

    res_svg = test_client.post("/api/art/compose/svg_stem", json={"title": "API Test SVG"})
    assert res_svg.status_code == 200
    assert res_svg.json()["success"] is True


def test_parametric_cad_kernel_and_viewer_apis(test_client):
    """Verifies real multi-facet 3D CAD generation across all 5 STEM archetypes,
    AP214 BREP STEP + binary STL roundtrip parsing, and interactive viewer endpoints."""
    from loom.clothos.cad_kernel import load_stl_as_mesh

    engine = StemCadEngine()
    for arch in StemCadEngine.ARCHETYPES:
        cad = engine.generate_cad_model(archetype=arch, title=f"Parametric {arch}", scale_mm=1.1, resolution=14)
        stl_path = engine.workspace_root / cad["stl_file"]
        step_path = engine.workspace_root / cad["step_file"]
        parsed = load_stl_as_mesh(stl_path)

        assert parsed["triangle_count"] >= 100
        assert parsed["volume_mm3"] > 0.0
        assert parsed["surface_area_mm2"] > 0.0
        assert len(parsed["normals"]) == parsed["triangle_count"]

        step_text = step_path.read_text(encoding="utf-8")
        assert "ISO-10303-21;" in step_text
        assert "CLOSED_SHELL" in step_text
        assert "CARTESIAN_POINT" in step_text

    # Test REST CAD endpoints
    for mtype in ["flexure", "cavity", "rotor", "gyroid", "microfluidic"]:
        r = test_client.get(f"/api/cad/mesh/{mtype}?scale_mm=1.0&resolution=12")
        assert r.status_code == 200
        data = r.json()
        assert data["triangle_count"] >= 100
        assert len(data["normals"]) == data["triangle_count"]
        assert data["volume_mm3"] > 0.0

    r_synth = test_client.post(
        "/api/cad/synthesize",
        json={"archetype": "GYROID_TPMS_HEAT_EXCHANGER", "scale_mm": 1.0, "resolution": 12},
    )
    assert r_synth.status_code == 200
    s_data = r_synth.json()
    assert s_data["success"] is True
    assert s_data["triangle_count"] >= 500
    assert s_data["artifact"]["stl_url"].startswith("/artifacts/art/")
    stl_name = Path(s_data["artifact"]["stl_url"]).name

    r_list = test_client.get("/api/cad/stl/list")
    assert r_list.status_code == 200
    assert any(f["filename"] == stl_name for f in r_list.json()["files"])

    r_load = test_client.get(f"/api/cad/stl/load?filename={stl_name}")
    assert r_load.status_code == 200
    assert r_load.json()["triangle_count"] == s_data["triangle_count"]
