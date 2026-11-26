"""
Comprehensive End-to-End Verification Suite:
- Rolling Trajectory Summarization in Gonzalez Pruning (`prune_messages_gonzalez`)
- Deliberative Planning, Novelty Gate & Non-Collapsing Creation
- High-Fidelity Multimodal Synthesis (PNG/WEBP Images, Stereo WAV/FLAC/MID Music, RIFF AVI+PCM/GIF/WEBP Video)
- Universal File Analysis Across All Modalities + Dashboard APIs
- Pure Geometric Simplex Engine, Quaternary Logic, Logos Sieve, Active Inference & AES-GCM Enclave
- Llama 70B Teacher Distillation Append/Deduplication & Workspace Output Consolidation
"""

from __future__ import annotations

import io
import json
from pathlib import Path
import sqlite3
import tempfile
import zipfile

from fastapi.testclient import TestClient

from loom.unified_nexus import prune_messages_gonzalez
from loom.clothos.deliberation_engine import TrajectoryLedger, DeliberativeCreator
from loom.clothos.multimodal_synth import (
    synthesize_high_res_image,
    synthesize_expressive_music,
    synthesize_real_video,
)
from loom.clothos.universal_file_analyzer import analyze_any_file
from loom.clothos.doc_parser import parse_document
from loom.clothos.creative_art import CreativeArtEngine
from loom.clothos.art_learning_feedback import ArtLearningFeedbackEngine
from loom.si.atelier import SovereignAtelier
from loom.clothos.simplex_substrate import (
    PureGeometricSimplexEngine,
    LogosSieveVerifier,
    BayesianActiveInferenceAgent,
    ZeroTrustEnclaveCipher,
    TargetForgeHarmonizer,
)
from loom.models.distillation_trainer import LoomDistillationTrainer
from loom.clothos.work_consolidator import WorkConsolidator
from loom.fabric.dashboard_server import app


def test_rolling_trajectory_memory_prevents_context_collapse():
    msgs = [{"role": "system", "content": "You are Sovereign Author tracking chapters."}]
    for ch in range(1, 26):
        msgs.append({"role": "user", "content": f"Write chapter {ch} advancing voyage past waypoint alpha-{ch}."})
        msgs.append({"role": "assistant", "content": f"Chapter {ch}: Vessel crossed meridian sector-{ch} toward harbor-{ch * 2}."})

    pruned, meta = prune_messages_gonzalez(msgs, max_turns=6)
    assert len(pruned) == 6
    assert pruned[0]["role"] == "system"
    assert pruned[-1]["content"] == msgs[-1]["content"]
    assert meta["pruned"] is True
    assert meta["dropped_count"] == len(msgs) - 6
    assert "[ROLLING_TRAJECTORY_MEMORY]" in pruned[0]["content"]
    # Early and recent dropped turns must remain represented in rolling trajectory
    assert "T1[user]" in pruned[0]["content"] or "waypoint alpha-1" in pruned[0]["content"]

    # Second pruning pass simulating Chapter 50 retains prior rolling summary without nesting bugs
    pruned.append({"role": "user", "content": "Write chapter 26 reaching basalt archipelago."})
    pruned.append({"role": "assistant", "content": "Chapter 26: Anchored beside basalt archipelago."})
    pruned2, _ = prune_messages_gonzalez(pruned, max_turns=6)
    assert len(pruned2) == 6
    assert pruned2[0]["content"].count("[ROLLING_TRAJECTORY_MEMORY]") == 1


def test_deliberative_creator_novelty_and_non_resetting_counter(tmp_path: Path):
    ledger = TrajectoryLedger(tmp_path)
    n1 = ledger.allocate_dream_num()
    n2 = ledger.allocate_dream_num()
    assert n2 == n1 + 1

    text_a = "Subglacial acoustic interferometer calibrated along volcanic vent 44B with cesium timing."
    ledger.record_work(
        work_id="w1",
        title="Basalt Lattice No.1",
        medium="story",
        theme="Acoustic observatory",
        body_text=text_a,
        structural_form="story",
    )

    ok_dup, reason_dup, _ = ledger.check_novelty("lMinted Dream #1: Basalt Lattice No.1", text_a, medium="story")
    assert not ok_dup and "Title collision" in reason_dup

    ok_near, reason_near, sim = ledger.check_novelty("Different Title", text_a, medium="story")
    assert not ok_near and sim >= 0.56 and ("duplicate" in reason_near.lower() or "similar" in reason_near.lower())

    ok_fresh, _, sim_fresh = ledger.check_novelty(
        "Pelagic Compass No.2",
        "Floating mangrove phytoremediation barge balanced vanadium chelators across brackish tidal deltas.",
        medium="story",
    )
    assert ok_fresh and sim_fresh < 0.5

    # CreativeArtEngine never resets dream_num and creates distinct outputs across mediums
    eng = CreativeArtEngine(workspace_root=tmp_path)
    r_img = eng.generate_art(medium="image", use_llm=False)
    r_mus = eng.generate_art(medium="music", use_llm=False)
    r_vid = eng.generate_art(medium="animated_video", use_llm=False)
    r_sto = eng.generate_art(medium="story", use_llm=False)
    assert r_img["dream_num"] < r_mus["dream_num"] < r_vid["dream_num"] < r_sto["dream_num"]
    assert Path(tmp_path / r_img["png_file"]).exists()
    assert Path(tmp_path / r_mus["wav_file"]).exists()
    assert Path(tmp_path / r_vid["avi_file"]).exists()

    # SovereignAtelier only seeds once when empty
    at_dir = tmp_path / "gallery"
    a1 = SovereignAtelier(gallery_dir=at_dir)
    count_after_first = len(list(at_dir.glob("*")))
    a2 = SovereignAtelier(gallery_dir=at_dir)
    count_after_second = len(list(at_dir.glob("*")))
    assert count_after_first == count_after_second

    # ArtLearningFeedbackEngine generates unique works tracked in ledger
    fb = ArtLearningFeedbackEngine(workspace_root=tmp_path)
    p1 = fb.create_artwork("VISUAL_GEOMETRY")
    p2 = fb.create_artwork("SONIC_HARMONIC")
    assert p1.title != p2.title
    assert Path(p1.file_path).exists() and Path(p2.file_path).exists()


def test_multimodal_synth_and_universal_file_analyzer(tmp_path: Path):
    # 1. Image (Gray-Scott + ST-GNN Geometric Fingerprint)
    img_res = synthesize_high_res_image(
        tmp_path / "img",
        "test_stgnn",
        "ST-GNN 200x200 Topology",
        algorithm="geometric_fingerprint_stgnn",
        width=256,
        height=256,
    )
    png_p = Path(img_res["png_file"])
    webp_p = Path(img_res["webp_file"])
    assert png_p.exists() and webp_p.exists()

    # 2. Music (Stereo WAV + FLAC + MIDI)
    mus_res = synthesize_expressive_music(tmp_path / "mus", "test_mus", "Lydian Tide", duration_s=2.5, seed=7)
    wav_p = Path(mus_res["wav_file"])
    mid_p = Path(mus_res["midi_file"])
    assert wav_p.exists() and mid_p.exists()

    # 3. Video (Real RIFF AVI + GIF + WEBP)
    vid_res = synthesize_real_video(tmp_path / "vid", "test_vid", "Lorenz Flow", duration_s=1.0, fps=12, width=128, height=128)
    avi_p = Path(vid_res["avi_file"])
    gif_p = Path(vid_res["gif_file"])
    assert avi_p.exists() and gif_p.exists()

    # 4. SQLite DB, Archive ZIP, Jupyter Notebook, Python, Binary
    db_p = tmp_path / "sample.db"
    conn = sqlite3.connect(db_p)
    conn.execute("CREATE TABLE metrics(id INTEGER, val REAL)")
    conn.execute("INSERT INTO metrics VALUES (1, 0.98)")
    conn.commit()
    conn.close()

    zip_p = tmp_path / "bundle.zip"
    with zipfile.ZipFile(zip_p, "w") as zf:
        zf.writestr("hello.txt", "world")

    nb_p = tmp_path / "experiment.ipynb"
    nb_p.write_text(json.dumps({
        "nbformat": 4,
        "cells": [
            {"cell_type": "markdown", "source": ["# Biomarker Forge\n", "Test note."]},
            {"cell_type": "code", "source": ["x = 42\n"]},
        ],
    }), encoding="utf-8")

    bin_p = tmp_path / "opaque.bin"
    bin_p.write_bytes(b"\x00\x01\x02CLOTHOS_MAGIC\x00\xff\xfe\xfd" * 8)

    for fp, expected_cat in [
        (png_p, "image"),
        (wav_p, "audio"),
        (mid_p, "audio"),
        (avi_p, "video"),
        (db_p, "database"),
        (zip_p, "archive"),
        (nb_p, "notebook"),
        (bin_p, "binary"),
    ]:
        ua = analyze_any_file(fp)
        assert ua["status"] == "SUCCESS", fp
        assert ua["category"] == expected_cat, f"{fp} expected {expected_cat}, got {ua['category']}"
        dp = parse_document(fp)
        assert dp["success"] is True

    # Spot check rich extracted signals
    assert analyze_any_file(png_p)["metadata"]["width"] == 256
    assert analyze_any_file(wav_p)["metadata"]["channels"] == 2
    assert analyze_any_file(avi_p)["metadata"]["container"] == "RIFF AVI"
    assert analyze_any_file(nb_p)["metadata"]["total_cells"] == 2


def test_simplex_substrate_logos_sieve_and_enclave():
    engine = PureGeometricSimplexEngine(block_size=8)
    block = engine.encode_scalar_array([0.0, 1.0, -1.0, 0.35] * 16, sequence_id=9)
    dma = block.pack_base16_dma()
    verdict = LogosSieveVerifier.verify_phase1_base16_block(block, packet=dma)
    assert verdict.passed is True
    assert verdict.checks["destructive_cancellation_axiom"] is True

    ai = BayesianActiveInferenceAgent()
    collapsed_txt = " ".join(["irs oort cloud 19 submission"] * 12)
    bad = LogosSieveVerifier.audit_text_truthfulness(collapsed_txt)
    assert bad.passed is False
    st = ai.update(bad)
    assert st["free_energy"] > 0.0

    enclave = ZeroTrustEnclaveCipher("test-passphrase")
    sealed = enclave.seal("Sovereign verified trajectory context")
    assert enclave.unseal(sealed) == "Sovereign verified trajectory context"

    harmonized = TargetForgeHarmonizer().harmonize_multimodal_batch(
        "Empirical synthesis measured at 0.033 Hz across 200 cortical nodes with r=0.985 coherence.",
        visual_seed=19,
    )
    assert len(harmonized["wdm_lanes"]["lane_2_spatial_200x200"]["top_features"]) == 10


def test_distillation_appends_without_overwrite_and_consolidator_deduplicates(tmp_path: Path):
    trainer = LoomDistillationTrainer(output_dir=tmp_path / "train")
    r1 = trainer.run_distillation_cycle(iterations_per_task=1, allow_live_teacher=False)
    r2 = trainer.run_distillation_cycle(iterations_per_task=1, allow_live_teacher=False)
    assert r1["total_distillation_pairs"] >= 7
    # Second run skips exact duplicates without wiping existing JSONL lines
    assert r2["total_distillation_pairs"] >= r1["total_distillation_pairs"]
    assert (tmp_path / "train" / "loom_sovereign_distilled_lessons.md").exists()

    # Consolidator collapses identical deliverable & story templates into clean archives
    deliv_dir = tmp_path / "deliverables"
    art_deliv = deliv_dir / "art"
    deliv_dir.mkdir(parents=True, exist_ok=True)
    art_deliv.mkdir(parents=True, exist_ok=True)
    (deliv_dir / "LATEST_24X7_REPORT.md").write_text("# Latest\nActive", encoding="utf-8")
    for idx in range(12):
        (deliv_dir / f"DELIVERABLE_20261126_0000{idx:02d}.md").write_text(
            f"# Empirical Deliverable\nGenerated at 2026-11-26 00:00:{idx:02d}\nIdentical template body.",
            encoding="utf-8",
        )
    for idx in range(8):
        (art_deliv / f"LMINT_DREAM_{idx}_STORY_100{idx}.md").write_text(
            "# Story\nSonnet of the Dual Cores identical body",
            encoding="utf-8",
        )

    wc = WorkConsolidator(workspace_root=tmp_path)
    cat = wc.consolidate_workspace_outputs(dry_run=False, keep_recent_per_category=3)
    assert cat["total_scanned"] == 20
    assert cat["categories"]["deliverables_reports"]["duplicates_collapsed"] == 11
    assert (deliv_dir / "LATEST_24X7_REPORT.md").exists()
    assert (deliv_dir / "archives" / "consolidated" / "CONSOLIDATED_CATALOG.json").exists()
    assert (deliv_dir / "archives" / "consolidated" / "CONSOLIDATED_SYNTHESIS.md").exists()


def test_dashboard_universal_analyze_and_simplex_endpoints(tmp_path: Path):
    client = TestClient(app)

    r_simp = client.get("/api/simplex/status")
    assert r_simp.status_code == 200
    assert r_simp.json()["status"] == "RATIFIED"

    sample_json = tmp_path / "probe.json"
    sample_json.write_text(json.dumps({"node": "ryzen", "rad": 16}), encoding="utf-8")
    r_path = client.post("/api/files/analyze", json={"file_path": str(sample_json)})
    assert r_path.status_code == 200
    assert r_path.json()["category"] == "data"

    # Multipart upload test (binary / image bytes)
    buf = io.BytesIO()
    from PIL import Image
    Image.new("RGB", (32, 32), color=(40, 80, 160)).save(buf, format="PNG")
    buf.seek(0)
    r_up = client.post(
        "/api/files/analyze",
        files={"file": ("uploaded_probe.png", buf, "image/png")},
    )
    assert r_up.status_code == 200
    assert r_up.json()["category"] == "image"
    assert r_up.json()["metadata"]["width"] == 32


def test_prompt_multimedia_inference_cli_and_api(tmp_path: Path):
    from loom.clothos.agent_cli import ClothOSAgentEngine, ClothOSAgentREPL, ExecutionMode

    eng = CreativeArtEngine(workspace_root=tmp_path)
    assert eng.infer_medium_from_prompt("generate a glowing fractal image") == ["image"]
    assert eng.infer_medium_from_prompt("compose an ambient synth music track") == ["music"]
    assert eng.infer_medium_from_prompt("make a swirling particle video animation") == ["animated_video"]
    assert eng.infer_medium_from_prompt("create a multimedia bundle of this concept") == ["image", "music", "animated_video", "story"]

    res = eng.prompt_multimedia("create a coral reaction-diffusion image", medium="auto", use_llm=False)
    assert res["medium"] == "image"
    assert Path(tmp_path / res["png_file"]).exists()

    # Dashboard auto-inferring prompt API
    client = TestClient(app)
    api_res = client.post("/api/media/generate", json={"medium": "auto", "prompt": "compose a short 432Hz melody"})
    assert api_res.status_code == 200
    body = api_res.json()
    assert body["success"] is True
    assert body["artifact"]["medium"] == "music"

    # CLI NL routing and /image slash command
    cli_eng = ClothOSAgentEngine(workspace_root=tmp_path, mode=ExecutionMode.FULL_ACCESS)
    nl_out = cli_eng.process_query("create an image of a Chladni standing wave")
    assert "ClothOS Deliberated Multimedia Output" in nl_out
    repl = ClothOSAgentREPL(tmp_path)
    repl.engine = cli_eng
    assert repl.handle_slash_command("/image basalt nebula mandala") is False

