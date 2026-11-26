# Copyright (c) 2026 Najmos Sakib. All rights reserved.

# Proprietary and confidential. Commercial distribution prohibited.

"""

Comprehensive Unit Test Suite for ClothOS Agentic Polyglot CLI Chatbot

(`tests/test_agent_cli.py`).

Tests Polyglot Execution (Python, Node.js, Rust, SQL, PowerShell),

Dual Execution Modes (FULL_ACCESS vs SANDBOX),

Ahimsa Safety Invariants, Ephemeral File Isolation, Promotion, Diffing,

Data Science Tooling, and Autonomous Task Resolution.

"""



import os

import json

import pytest

from pathlib import Path



from loom.clothos.agent_cli import (

    ClothOSAgentEngine,

    ExecutionMode,

    PolyglotEngine,

    SandboxManager,

    ToolRegistry,

)





@pytest.fixture

def workspace_root():

    return Path(__file__).resolve().parents[1]





@pytest.fixture

def agent_engine(workspace_root):

    return ClothOSAgentEngine(workspace_root, mode=ExecutionMode.FULL_ACCESS)





@pytest.fixture

def sandbox_manager(workspace_root):

    sm = SandboxManager(workspace_root)

    sm.reset_sandbox()

    yield sm

    sm.reset_sandbox()





def test_polyglot_python_execution(workspace_root, sandbox_manager):

    poly = PolyglotEngine(workspace_root, sandbox_manager)

    code = "print(sum([x * 2 for x in range(5)]))"

    res = poly.execute_code("python", code, ExecutionMode.FULL_ACCESS)

    assert res.get("returncode") == 0

    assert "20" in res.get("stdout", "").strip()

    assert res.get("language") == "Python"

    assert res.get("duration_s", 0) >= 0





def test_polyglot_node_execution(workspace_root, sandbox_manager):

    poly = PolyglotEngine(workspace_root, sandbox_manager)

    if not poly.runtimes.get("node"):

        pytest.skip("Node.js runtime not installed on host.")

    code = "console.log(JSON.stringify({status: 'OK', val: 42 * 2}));"

    res = poly.execute_code("javascript", code, ExecutionMode.FULL_ACCESS)

    assert res.get("returncode") == 0

    data = json.loads(res.get("stdout", "").strip())

    assert data["status"] == "OK"

    assert data["val"] == 84





def test_polyglot_rust_execution(workspace_root, sandbox_manager):

    poly = PolyglotEngine(workspace_root, sandbox_manager)

    if not poly.runtimes.get("rustc"):

        pytest.skip("Rust compiler (rustc) not installed on host.")

    code = """fn main() {

    let mut sum: u64 = 0;

    for i in 1..=10 { sum += i; }

    println!("RUST_SUM={}", sum);

}"""

    res = poly.execute_code("rust", code, ExecutionMode.FULL_ACCESS)

    assert res.get("returncode") == 0

    assert "RUST_SUM=55" in res.get("stdout", "")





def test_polyglot_sql_execution(workspace_root, sandbox_manager):

    poly = PolyglotEngine(workspace_root, sandbox_manager)

    sql_script = """

    CREATE TABLE test_scores (student TEXT, score INT);

    INSERT INTO test_scores VALUES ('Alice', 95), ('Bob', 88), ('Charlie', 92);

    SELECT student, score FROM test_scores WHERE score > 90;

    """

    res = poly.execute_code("sql", sql_script, ExecutionMode.FULL_ACCESS)

    assert "tables" in res

    assert len(res["tables"]) > 0

    table_data = res["tables"][0]

    assert table_data["table"] == "test_scores"

    assert len(table_data["rows"]) == 3





def test_polyglot_powershell_execution(workspace_root, sandbox_manager):

    poly = PolyglotEngine(workspace_root, sandbox_manager)

    ps_code = 'Write-Output "CLOTHOS_PS_TEST_SUCCESS"'

    res = poly.execute_code("powershell", ps_code, ExecutionMode.FULL_ACCESS)

    assert res.get("returncode") == 0

    assert "CLOTHOS_PS_TEST_SUCCESS" in res.get("stdout", "")





def test_sandbox_file_isolation(workspace_root, sandbox_manager):

    poly = PolyglotEngine(workspace_root, sandbox_manager)

    test_fname = "isolated_experiment_test.txt"

    code = f"""with open("{test_fname}", "w") as f:

    f.write("SANDBOX_ISOLATED_DATA_12345")

print("WROTE_FILE")

"""

    res = poly.execute_code("python", code, ExecutionMode.SANDBOX)

    assert res.get("returncode") == 0

    assert "WROTE_FILE" in res.get("stdout", "")



    # Host workspace root MUST NOT contain the file

    host_file = workspace_root / test_fname

    assert not host_file.exists(), "Sandbox violation: File was written directly to host workspace!"



    # Ephemeral sandbox directory MUST contain the file

    sandbox_file = sandbox_manager.sandbox_dir / test_fname

    assert sandbox_file.exists(), "File should be created inside ephemeral sandbox chamber!"

    assert sandbox_file.read_text().strip() == "SANDBOX_ISOLATED_DATA_12345"



    # Promote file to workspace

    success, msg = sandbox_manager.promote_to_workspace(test_fname)

    assert success is True

    assert host_file.exists()

    assert host_file.read_text().strip() == "SANDBOX_ISOLATED_DATA_12345"



    # Cleanup host file

    host_file.unlink()





def test_sandbox_ahimsa_veto(sandbox_manager):

    # Destructive commands must be vetoed

    safe, reason = sandbox_manager.is_safe_command("rmdir /s /q c:\\")

    assert not safe

    assert "destructive" in reason.lower()



    safe, reason = sandbox_manager.is_safe_command("del /f /s /q c:\\windows\\system32")

    assert not safe



    safe, reason = sandbox_manager.is_safe_command("format c:")

    assert not safe



    safe, reason = sandbox_manager.is_safe_command("python script.py")

    assert safe





def test_sandbox_diff_generation(workspace_root, sandbox_manager):

    test_file = "diff_sample_test.txt"

    sbx_file = sandbox_manager.sandbox_dir / test_file

    sbx_file.write_text("line1\nline2_modified\nline3\n")



    ws_file = workspace_root / test_file

    ws_file.write_text("line1\nline2_original\nline3\n")



    diff_output = sandbox_manager.diff_file(test_file)

    assert "-line2_original" in diff_output

    assert "+line2_modified" in diff_output



    # Clean up workspace test file

    ws_file.unlink()





def test_data_science_inspect_and_ascii(workspace_root, agent_engine):

    # Create temporary test dataset

    csv_path = workspace_root / "temp_agent_test.csv"

    csv_path.write_text("id,val,category\n1,10.5,A\n2,20.2,B\n3,30.8,A\n4,40.1,B\n5,50.0,A\n")



    try:

        prof = agent_engine.tools.execute("data_inspect", file_path="temp_agent_test.csv")

        assert prof["rows"] == 5

        assert prof["columns"] == 3

        assert prof["profiles"]["val"]["is_numeric"] is True

        assert prof["profiles"]["val"]["mean"] == 30.32



        # Test ASCII Histogram

        hist = agent_engine.tools.execute("data_visualize_ascii", file_path="temp_agent_test.csv", column="val", chart_type="histogram")

        assert "chart" in hist

        assert "█" in hist["chart"]



        # Test ASCII Sparkline

        spark = agent_engine.tools.execute("data_visualize_ascii", file_path="temp_agent_test.csv", column="val", chart_type="sparkline")

        assert "chart" in spark

        assert len(spark["chart"]) > 0



        # Test SQL query on CSV

        sql_res = agent_engine.tools.execute("data_query_sql", file_path="temp_agent_test.csv", sql_query="SELECT category, COUNT(*) as cnt FROM dataset GROUP BY category")

        assert sql_res["row_count"] == 2

    finally:

        if csv_path.exists():

            csv_path.unlink()





def test_natural_language_task_solving(agent_engine):

    # Test natural language mode toggle

    resp_sbx = agent_engine.process_query("switch to sandbox mode")

    assert "Switched to SANDBOX MODE" in resp_sbx

    assert agent_engine.mode == ExecutionMode.SANDBOX



    resp_full = agent_engine.process_query("switch to full access mode")

    assert "Switched to FULL ACCESS MODE" in resp_full

    assert agent_engine.mode == ExecutionMode.FULL_ACCESS



    # Test autonomous task solving

    resp_calc = agent_engine.process_query("Calculate the first 8 Fibonacci numbers in Python")

    assert "13" in resp_calc or "21" in resp_calc or "Fibonacci" in resp_calc





def test_conversational_chat_and_help(agent_engine):

    # Test conversational greeting (Gemini / AGY style)

    resp_hi = agent_engine.process_query("hello there!")

    assert any(w in resp_hi.lower() for w in ["hello", "clothos", "assistant", "greetings", "hi"])



    # Test conversational inquiry about sandbox vs full access

    resp_modes = agent_engine.process_query("What is the difference between sandbox and full access?")

    assert "sandbox" in resp_modes.lower()

    assert "full access" in resp_modes.lower()



    # Test slash commands help

    resp_help = agent_engine.process_query("/help")

    assert "Common Slash Commands" in resp_help

    assert "/mode" in resp_help





def test_file_traversal_and_riscv_tooling(agent_engine, workspace_root):

    # Test directory traversal

    trav_res = agent_engine.tools.execute("file_traverse", path="loom/clothos", max_depth=2)

    assert "error" not in trav_res

    assert trav_res["total_files"] > 0

    assert ".py" in trav_res["extension_breakdown"]



    # Test RISC-V template generation

    gen_res = agent_engine.tools.execute("riscv_generate", template="tpu_systolic", matrix_dim=16)

    assert gen_res["template"] == "tpu_systolic"

    assert "tpu_matmul_acc" in gen_res["code"]

    assert gen_res["analysis"]["has_custom_tpu_opcodes"] is True



    # Test RISC-V inspection of existing kernel

    asm_sample = "addi a0, a0, 1\nmul a1, a0, a2\ntpu_matmul_acc t1, a1, t0\nret\n"

    insp = agent_engine.tools.execute("riscv_inspect", file_path=None)

    assert "total_riscv_files_found" in insp



    # Natural language traversal and RISC-V prompt test

    resp_nl_rv = agent_engine.process_query("generate riscv assembly for systolic tpu")

    assert any(term in resp_nl_rv.lower() for term in ["tpu", "riscv", "systolic", "matmul", "assembly"])





def test_autonomous_runner_and_idle_policy(agent_engine):

    # Test idle explanation

    resp_idle = agent_engine.process_query("What should loom do when running in autonomous mode with no prompt or command?")

    assert any(w in resp_idle.lower() for w in ["idle", "autonomous", "policy", "safe"])

    assert "Task Queue Polling" in resp_idle

    assert "Zero Unprompted File Mutation" in resp_idle



    # Test task enqueue and queue listing

    enqueue_res = agent_engine.tools.execute("runner_enqueue", prompt="Calculate 10 Fibonacci numbers in Python")

    assert "task_id" in enqueue_res

    assert enqueue_res["status"] == "QUEUED"



    status_res = agent_engine.tools.execute("runner_status")

    assert "pending_tasks" in status_res

    assert status_res["idle_policy"] in ["PASSIVE_WATCHDOG_NO_FILE_MUTATION", "AUTOPOIETIC_ART_AND_SELF_TRAINING_FEEDBACK"]





def test_agentic_brain_cns_and_self_teaching(agent_engine):

    # 1. Test CNS telemetry tool

    cns_res = agent_engine.tools.execute("cns_telemetry")

    assert "cns" in cns_res

    assert "operator_fealty" in cns_res

    assert "Najmos Sakib" in cns_res["operator_fealty"]

    assert "ClothOS" in cns_res["operator_fealty"]



    # 2. Test neuromodulation tool

    neuro_res = agent_engine.tools.execute("brain_neuromodulate", dopamine=0.95, acetylcholine=0.92)

    assert neuro_res["status"] == "NEUROMODULATION_UPDATED"

    assert neuro_res["current_tone"]["dopamine_rpe"] == 0.95

    assert neuro_res["current_tone"]["acetylcholine_snr"] == 0.92



    # 3. Test self-teaching and capability diagnostics

    diag_res = agent_engine.tools.execute("self_diagnose_and_learn", run_tests=True)

    assert "self_knowledge" in diag_res

    assert diag_res["self_knowledge"]["status"] == "SELF_KNOWLEDGE_CONSOLIDATED"

    assert diag_res["self_knowledge"]["total_tools_mastered"] >= 15

    assert "diagnostic_tests" in diag_res

    assert diag_res["diagnostic_tests"]["all_healthy"] is True



    # 4. Test natural language CNS & Brain queries

    resp_cns = agent_engine.process_query("show me the central nervous system telemetry")

    assert "Central Nervous System (CNS)" in resp_cns

    assert "Financial & Macro Synapse" in resp_cns

    assert "Cluster Proprioception" in resp_cns



    resp_brain = agent_engine.process_query("what is your digital brain status and neuromodulation?")

    assert "Digital Brain & Neurobiological Framework" in resp_brain

    assert "Dopamine" in resp_brain

    assert "Prefrontal Cortex" in resp_brain



    # 5. Test autonomous ReAct execution loop

    react_res = agent_engine.tools.execute("agentic_execute_loop", goal="teach yourself and test your tools")

    assert "final_answer" in react_res

    assert react_res["steps_taken"] >= 1

    assert "Autonomous Execution Report" in react_res["final_answer"]



    # 6. Test natural language /agent routing

    resp_agent = agent_engine.process_query("agent: traverse loom/clothos directory")

    assert "Autonomous Execution Report" in resp_agent

    assert "file_traverse" in resp_agent





def test_jarvis_and_self_training_knowledge_engine(agent_engine):

    # 1. Test Jarvis Briefing

    b_res = agent_engine.tools.execute("jarvis_briefing", speak_aloud=False)

    assert "markdown_briefing" in b_res

    assert "Najmos Sakib" in b_res["markdown_briefing"]

    assert "ClothOS" in b_res["markdown_briefing"]

    assert "spoken_script" in b_res

    assert "phi" in b_res["spoken_script"].lower()



    # 2. Test Jarvis Speak and Notify

    spk_res = agent_engine.tools.execute("jarvis_speak", text="ClothOS all systems nominal.")

    assert "SPEAKING" in spk_res["status"]



    notif_res = agent_engine.tools.execute("jarvis_notify", title="ClothOS", message="All systems nominal.")

    assert "NOTIFICATION" in notif_res["status"]



    # 3. Test Self-Training Cycle

    train_res = agent_engine.tools.execute("model_train_self")

    assert "cycle_id" in train_res

    assert train_res["generation"] >= 16

    assert train_res["new_training_pairs_generated"] >= 1

    assert train_res["experiments_confirmed"] >= 1

    assert train_res["fitness_improvement"] > 0



    # 4. Test Knowledge Status

    k_res = agent_engine.tools.execute("model_knowledge_status")

    assert k_res["total_curriculum_pairs"] >= 10

    assert "sovereign_skill_weights" in k_res

    assert "Kuramoto Phase Synchronization" in k_res["sovereign_skill_weights"]



    # 5. Test Natural Language Query Routing

    resp_jarvis = agent_engine.process_query("give me an executive sitrep briefing")

    assert "J.A.R.V.I.S. Executive Situation Report" in resp_jarvis

    assert "Cluster & Hardware Proprioception" in resp_jarvis



    resp_train = agent_engine.process_query("train the model weights from empirical experiments and knowledge base")

    assert "ClothOS Autonomous Self-Training Cycle Completed" in resp_train

    assert "Hebbian Weight Delta" in resp_train





def test_idle_art_and_closed_loop_learning_feedback(agent_engine):

    # 1. Test Art Creation tool

    art_res = agent_engine.tools.execute("art_create", modality="VISUAL_GEOMETRY")

    assert "art_id" in art_res

    assert art_res["modality"] == "VISUAL_GEOMETRY"

    assert "svg" in art_res["file_path"].lower()

    assert "phi_ratio" in art_res["latent_ratios"]

    assert "epistemic_hypothesis" in art_res

    assert "investigation_target" in art_res



    # 2. Test Idle Art Closed-Loop Learning Feedback

    cycle_res = agent_engine.tools.execute("art_idle_cycle", modality="SONIC_HARMONIC")

    assert cycle_res["cycle_status"] == "SUCCESS_CLOSED_LOOP"

    assert "art_piece" in cycle_res

    assert cycle_res["art_piece"]["modality"] == "SONIC_HARMONIC"

    assert "432" in cycle_res["art_piece"]["investigation_target"]



    # 3. Test Gallery Summary

    gal_res = agent_engine.tools.execute("art_gallery")

    assert gal_res["total_artworks"] >= 1

    assert "recent_hypotheses" in gal_res



    # 4. Test Natural Language & Query Routing

    resp_art = agent_engine.process_query("make art using sacred geometry and svg")

    assert "ClothOS Sovereign Art Generated & Learning Feedback Engaged" in resp_art

    assert "Derived Epistemic Hypothesis" in resp_art



    resp_gal = agent_engine.process_query("show recent art gallery and curiosities")

    assert "ClothOS Sovereign Art & Curiosity Gallery" in resp_gal





def test_autonomous_task_delegator(agent_engine):

    # 1. Test Task Delegation tool

    goal = "Synthesize new RISC-V matrix kernel, verify Kuramoto synchrony, and conduct empirical self-training"

    del_res = agent_engine.tools.execute("task_delegate", goal=goal)

    assert "plan_id" in del_res

    assert del_res["overall_status"] == "COMPLETED"

    assert len(del_res["subtasks"]) >= 2

    assert "synthesis" in del_res



    # 2. Test natural language /delegate routing

    resp = agent_engine.process_query("delegate: query CNS telemetry and create 432Hz harmonic art")

    assert "ClothOS Autonomous Task Delegation Plan Completed" in resp

    assert "Sub-Task Allocations & Execution Receipts" in resp

    assert "ART_CURIO_ENGINE" in resp or "CNS_SENSORY_ENGINE" in resp













def test_multimodal_music_generation(agent_engine):

    # Test polyphonic ambient generative music synthesis (.wav + .html)

    res = agent_engine.tools.execute("generate_music", prompt="Deep space Lydian pad", duration_s=2.5, key="Dm9")

    assert res["status"] == "SUCCESS"

    assert res["medium"] == "music"

    assert res["duration_s"] == 2.5

    assert res["sample_rate"] == 44100

    wav_path = Path(res["audio_file"])

    html_path = Path(res["player_html"])

    assert wav_path.exists()

    assert wav_path.stat().st_size > 1000

    assert html_path.exists()





def test_multimodal_video_generation(agent_engine):

    # Test animated video generation (.gif + interactive canvas HTML)

    res = agent_engine.tools.execute("generate_video", prompt="Clifford strange attractor loop", duration_s=2.0, fps=20)

    assert res["status"] == "SUCCESS"

    assert res["medium"] == "animated_video"

    assert res["fps"] == 20

    assert res["total_frames"] == 40

    gif_path = Path(res["video_gif"])

    canvas_path = Path(res["video_canvas_html"])

    assert gif_path.exists()

    assert gif_path.stat().st_size > 1000

    assert canvas_path.exists()





def test_multimodal_visual_art_generation(agent_engine):

    # Test high-resolution SVG and PNG visual art generation

    res = agent_engine.tools.execute("generate_visual_art", prompt="Symplectic manifold sacred geometry", art_type="sacred_geometry")

    assert res["status"] == "SUCCESS"

    assert res["medium"] == "visual_art"

    svg_path = Path(res["svg_file"])

    png_path = Path(res["png_file"])

    assert svg_path.exists()

    assert "<svg" in svg_path.read_text(encoding="utf-8")

    assert png_path.exists()

    assert png_path.stat().st_size > 500





def test_realtime_stream_of_consciousness():

    from loom.clothos.agent_cli import ThinkingStream

    ThinkingStream.enable()

    assert ThinkingStream.is_enabled() is True



    # Test stream lifecycle

    ThinkingStream.start_stream("Unit-Test-Head")

    assert ThinkingStream._streaming_active is True

    assert ThinkingStream._streaming_in_thought is True



    ThinkingStream.stream_chunk("Thought: Deliberating over manifold curvature...")

    ThinkingStream.stream_chunk("Action: run_shell")

    assert ThinkingStream._streaming_in_thought is False



    ThinkingStream.end_stream()

    assert ThinkingStream._streaming_active is False





def test_art_piece_companion_explainers(agent_engine):

    # 1. Test music generation with companion explainer

    res_music = agent_engine.tools.execute("generate_music", prompt="Pythagorean 432Hz ambient pad", duration_s=2.0, key="432Hz")

    assert "explainer" in res_music

    assert "explainer_file" in res_music

    expl_music = Path(res_music["explainer_file"])

    assert expl_music.exists()

    assert "Kuramoto" in res_music["explainer"] or "432" in res_music["explainer"]



    # 2. Test video generation with companion explainer

    res_video = agent_engine.tools.execute("generate_video", prompt="Clifford strange attractor", duration_s=1.5, fps=20)

    assert "explainer" in res_video

    assert "explainer_file" in res_video

    expl_video = Path(res_video["explainer_file"])

    assert expl_video.exists()

    assert "Dynamical Systems" in res_video["explainer"] or "Attractor" in res_video["explainer"]



    # 3. Test standalone explainer tool

    expl_res = agent_engine.tools.execute("art_generate_explainer", file_path=res_music["audio_file"], modality="music")

    assert expl_res["status"] == "SUCCESS"

    assert Path(expl_res["explainer_path"]).exists()



    # 4. Test natural language art explainer routing

    nl_expl = agent_engine.process_query("every art piece should come with an explainer")

    assert "Art Explainer Protocol Active" in nl_expl

    assert "Mathematical & Scientific Foundation" in nl_expl





def test_work_review_and_100mb_consolidation(agent_engine):

    # Test work review and long-form opus consolidation exceeding 100MB+

    # We test with min_size_mb=101.0

    res = agent_engine.tools.execute("consolidate_artifacts_and_review", mode="codebase_compendium", min_size_mb=101.0)

    assert res["status"] == "SUCCESS"

    assert res["exceeds_100mb"] is True

    assert res["size_mb"] >= 100.0

    assert "work_review_audit" in res

    assert res["work_review_audit"]["status"] == "REVIEW_AUDIT_COMPLETED"

    assert "storage_allocation" in res

    archive_file = Path(res["archive_file"])

    assert archive_file.exists()

    assert archive_file.stat().st_size > 100 * 1024 * 1024



    # Test natural language review and consolidation routing

    nl_resp = agent_engine.process_query("review work and consolidate deliverables into longer works exceeding 100mb")

    assert "ClothOS Work Review & Master Long-Form Opus Consolidated" in nl_resp

    assert "Exceeds 100MB+: `True`" in nl_resp





def test_storage_hierarchy_and_strategic_tiering(agent_engine):

    # 1. Test storage matrix status

    status = agent_engine.tools.execute("storage_matrix_status")

    assert "total_cluster_storage_gb" in status

    assert status["device_count"] >= 1

    assert len(status["tiers_configured"]) == 5



    # 2. Test strategic placement recommendation for 150MB opus

    rec_heavy = agent_engine.tools.execute("storage_recommend_target", file_size_mb=150.0, purpose="opus_archive")

    assert "tier" in rec_heavy

    assert "drive" in rec_heavy



    # 3. Test natural language storage query

    nl_storage = agent_engine.process_query("show storage devices and strategic hierarchy")

    assert "Strategic Multi-Tier Storage Hierarchy" in nl_storage

    assert "Tier 0" in nl_storage

    assert "Tier 1" in nl_storage





def test_entire_codebase_deep_ast_analysis(agent_engine):

    # 1. Test entire codebase analysis

    audit = agent_engine.tools.execute("codebase_analyze_entire", target_dir=".", deep_ast=True)

    assert audit["status"] == "SUCCESS"

    assert audit["total_files"] > 10

    assert audit["total_lines"] > 1000

    assert audit["ast_symbols"]["total_classes"] > 0

    assert audit["ast_symbols"]["total_functions"] > 0

    assert "ClothOSAgentEngine" in str(audit["ast_symbols"]["classes"])

    assert "ahimsa_security_checks" in audit



    # 2. Test natural language codebase analysis routing

    nl_audit = agent_engine.process_query("analyze entire codebase")

    assert "Entire Codebase Architectural & AST Analysis Report" in nl_audit

    assert "Scale & Polyglot Composition" in nl_audit

    assert "Ahimsa & Security Boundaries" in nl_audit





def test_heterogeneous_hardware_and_all_gpus(agent_engine):

    # 1. Test hardware discovery across all GPUs and CPU threads

    hw = agent_engine.tools.execute("hardware_accelerate_status")

    assert hw["total_gpus_detected"] >= 2

    gpu_names = [g["name"] for g in hw["gpus"]]

    assert any("RTX 3060" in n or "3060" in n for n in gpu_names)

    assert any("RX 580" in n or "580" in n or "Radeon" in n for n in gpu_names)

    assert hw["cpu_topology"]["total_cluster_compute_threads"] >= 16



    # 2. Test compute affinity dispatching

    disp_llm = agent_engine.tools.execute("hardware_dispatch_task", task_type="LLM_INFERENCE")

    assert "3060" in disp_llm["assigned_device"] or "CUDA" in disp_llm["backend"]



    disp_dsp = agent_engine.tools.execute("hardware_dispatch_task", task_type="AUDIO_DSP_SYNTHESIS")

    assert "Ryzen" in disp_dsp["assigned_device"] or "AVX2" in disp_dsp["backend"]



    # 3. Test natural language GPU telemetry

    nl_gpu = agent_engine.process_query("show all hardware components and all gpus")

    assert "Heterogeneous Silicon & Multi-GPU Compute Matrix" in nl_gpu

    assert "RTX 3060" in nl_gpu

    assert "RX 580" in nl_gpu or "Radeon" in nl_gpu



    # 4. Test GPU 1 (RX 580) Diagnosis and Engagement

    nl_rx580 = agent_engine.process_query("why isn't gpu1 being used? the rx580")

    assert "GPU 1 (AMD Radeon RX 580" in nl_rx580

    assert "Ollama" in nl_rx580

    assert "CUDA" in nl_rx580



    engage_res = agent_engine.tools.execute("hardware_engage_rx580", workload="kuramoto_sweep")

    assert engage_res["status"] == "SUCCESS"

    assert engage_res["compute_units_engaged"] == 36

    assert engage_res["active_oscillators"] == 65536





def test_terminal_task_execution(agent_engine, workspace_root):

    """Verify full-spectrum terminal and shell task execution capabilities."""

    # 1. Verify Terminal Tool Registrations

    assert "terminal_execute" in agent_engine.tools.tools

    assert "terminal_interactive_session" in agent_engine.tools.tools

    assert "terminal_remote_exec" in agent_engine.tools.tools

    assert "terminal_sysinfo" in agent_engine.tools.tools

    assert "terminal_ps" in agent_engine.tools.tools

    assert "terminal_bench" in agent_engine.tools.tools

    assert "terminal_monitors" in agent_engine.tools.tools



    # 2. Test Local Terminal Command Execution

    exec_res = agent_engine.tools.execute("terminal_execute", cmd="echo 'ClothOS Sovereign Terminal Active'")

    assert exec_res["returncode"] == 0

    assert "ClothOS Sovereign Terminal Active" in exec_res["stdout"]

    assert exec_res["duration_s"] >= 0.0



    # 3. Test Stateful Navigation (cd)

    sub_dir = workspace_root / "test_term_sub"

    sub_dir.mkdir(exist_ok=True)

    cd_res = agent_engine.tools.execute("terminal_execute", cmd="cd test_term_sub")

    assert cd_res["returncode"] == 0

    assert "Directory changed" in cd_res["stdout"] or "test_term_sub" in cd_res["cwd"]



    cd_back = agent_engine.tools.execute("terminal_execute", cmd="cd -")

    assert cd_back["returncode"] == 0



    # 4. Test Terminal Utilities (sysinfo, ps, bench, monitors)

    sys_res = agent_engine.tools.execute("terminal_sysinfo")

    assert sys_res["returncode"] == 0

    assert "sysinfo" in sys_res

    assert "host" in sys_res["sysinfo"]

    assert "cluster_mesh" in sys_res["sysinfo"]



    ps_res = agent_engine.tools.execute("terminal_ps")

    assert ps_res["returncode"] == 0

    assert "processes" in ps_res

    assert ps_res["process_count"] >= 1



    bench_res = agent_engine.tools.execute("terminal_bench", cmd="echo 1")

    assert bench_res["returncode"] == 0

    assert bench_res["duration_ms"] >= 0.0



    mon_res = agent_engine.tools.execute("terminal_monitors")

    assert mon_res["returncode"] == 0

    assert "cluster_monitors" in mon_res



    # 5. Test Remote Terminal Execution fallback

    rem_res = agent_engine.tools.execute("terminal_remote_exec", target_node="node2", cmd="echo 'Local Node2 Echo'")

    assert rem_res["returncode"] == 0

    assert "Local Node2 Echo" in rem_res["stdout"]



    # 6. Test Natural Language Terminal Routing in process_query

    nl_cap = agent_engine.process_query("can you do terminal tasks as well?")

    assert "ClothOS Terminal Task Execution Engine" in nl_cap

    assert "Stateful Session Execution" in nl_cap



    nl_cmd = agent_engine.process_query("run terminal command: echo HelloFromClothOSTerminal")

    assert "Terminal Task Execution" in nl_cmd

    assert "HelloFromClothOSTerminal" in nl_cmd



    nl_ps = agent_engine.process_query("show processes in terminal")

    assert "ClothOS Terminal Process Inspector" in nl_ps

    assert "PID" in nl_ps



    nl_sys = agent_engine.process_query("system info in terminal")

    assert "ClothOS Terminal System Architecture" in nl_sys

    assert "Host" in nl_sys





def test_task_abort_and_cancellation(agent_engine):

    """Verify task quitting, abort protocols, and live Currently Doing telemetry."""

    from loom.clothos.activity_tracker import CurrentlyDoing

    from loom.clothos.agent_cli import ClothOSAgentREPL



    # 1. Test Activity Tracking

    CurrentlyDoing.set("Executing AST Codebase Audit", phase="ANALYSIS")

    assert CurrentlyDoing.get() == "Executing AST Codebase Audit"

    assert CurrentlyDoing.get_phase() == "ANALYSIS"

    assert CurrentlyDoing.get_elapsed_s() >= 0.0



    st = CurrentlyDoing.get_status_dict()

    assert st["phase"] == "ANALYSIS"

    assert "AST Codebase Audit" in st["current_task"]



    # 2. Test Abort Signal

    assert CurrentlyDoing.is_abort_requested() is False

    CurrentlyDoing.request_abort()

    assert CurrentlyDoing.is_abort_requested() is True



    CurrentlyDoing.reset()

    assert CurrentlyDoing.is_abort_requested() is False

    assert CurrentlyDoing.get_phase() == "IDLE"



    # 3. Test Render Panel

    panel = CurrentlyDoing.render_panel()

    assert panel is not None



    # 4. Test Natural Language Query: How to Quit Task

    nl_quit = agent_engine.process_query("how do i get it to quit a task?")

    assert "How to Quit or Abort a Task in ClothOS" in nl_quit

    assert "Ctrl+C" in nl_quit

    assert "/abort" in nl_quit



    # 5. Test Natural Language Query: Currently Doing

    nl_doing = agent_engine.process_query("what are you currently doing?")

    assert "Currently Doing Telemetry" in nl_doing

    assert "Active Task" in nl_doing



    # 6. Test REPL Slash Commands for /abort and /doing

    repl = ClothOSAgentREPL(agent_engine.workspace_root)

    assert repl.handle_slash_command("/abort") is False

    assert repl.handle_slash_command("/doing") is False





def test_ui_banner_and_forest_purple_theme(agent_engine, workspace_root):
    """Verify production industrial slate theme, preserved forest theme, and scientific theme."""
    from loom.clothos.terminal import format_powerline_prompt, make_bottom_toolbar
    from loom.clothos.agent_cli import ClothOSAgentREPL
    from loom.clothos.theme import ThemeManager

    # 1. Verify default active theme is production
    assert ThemeManager.get_active().name in ("production", "forest")
    prod = ThemeManager.get_theme("production")
    assert prod.brand_primary == "#38bdf8"
    assert prod.border_primary == "#334155"

    # 2. Verify ThemeManager preserves copies of forest and 8-bit scientific themes
    forest_copy = ThemeManager.get_theme("forest")
    assert forest_copy is not None
    assert forest_copy.brand_primary == "#22c55e"

    sci_copy = ThemeManager.get_theme("scientific")
    assert sci_copy is not None
    assert sci_copy.brand_primary == "#00ff66"
    assert sci_copy.brand_secondary == "#00f0ff"

    # 3. Verify Powerline Prompt styling in production theme
    prompt_html = format_powerline_prompt(
        workspace_root=workspace_root,
        active_head="loom-sovereign",
        last_returncode=0,
        is_full_access=True
    )
    val = prompt_html.value
    assert "CLOTHOS" in val
    assert "#38bdf8" in val or "#22c55e" in val

    # 4. Verify Bottom Toolbar with [CURRENT] indicator
    tb = make_bottom_toolbar()
    tb_val = tb.value
    assert "[CURRENT]:" in tb_val

    # 5. Verify Display Banner executes cleanly without animation flicker
    repl = ClothOSAgentREPL(workspace_root)
    repl.display_banner()
    assert repl.handle_slash_command("/theme") is False
    assert repl.handle_slash_command("/theme list") is False
    assert repl.handle_slash_command("/theme forest") is False
    assert ThemeManager.get_active().name == "forest"
    assert repl.handle_slash_command("/theme production") is False
    assert ThemeManager.get_active().name == "production"





def test_agent_steering_controller_and_protocols(agent_engine):

    """Verify real-time operator steering capabilities and dynamic context modulation."""

    from loom.clothos.steering_controller import SteeringController

    from loom.clothos.agent_cli import ClothOSAgentREPL



    # 1. Test Steering Tool Execution

    steer_res = agent_engine.tools.execute(

        "agent_steer",

        directive="Prioritize OpenCL 2.0 Kuramoto sweeps on AMD RX 580",

        category="silicon",

        priority="CRITICAL"

    )

    assert steer_res["status"] == "SUCCESS"

    assert "directive_id" in steer_res

    assert SteeringController.has_directives() is True



    # 2. Test Steering Status Tool

    status_res = agent_engine.tools.execute("agent_steering_status")

    assert status_res["has_directives"] is True

    assert status_res["count"] >= 1

    directives = status_res["directives"]

    assert any("RX 580" in d["directive"] for d in directives)



    # 3. Test Context Block Generation

    ctx_block = SteeringController.get_steering_context_block()

    assert "OPERATOR STEERING VECTORS" in ctx_block

    assert "RX 580" in ctx_block



    # 4. Test Natural Language Steering Explanation

    nl_expl = agent_engine.process_query("allow for steering as well")

    assert "ClothOS Real-Time Agent Steering Engine" in nl_expl

    assert "Immediate Natural Language Steering" in nl_expl

    assert "RX 580" in nl_expl



    # 5. Test Natural Language Direct Steer Injection

    nl_inject = agent_engine.process_query("steer: ensure all audio synthesis uses 432Hz Pythagorean tuning")

    assert "Operator Steering Vector Injected & Active" in nl_inject

    assert "432Hz" in nl_inject



    # 6. Test REPL Slash Commands

    repl = ClothOSAgentREPL(agent_engine.workspace_root)

    assert repl.handle_slash_command("/steer status") is False

    assert repl.handle_slash_command("/steer clear") is False



    # 7. Test Steering Clear Tool

    clear_res = agent_engine.tools.execute("agent_steering_clear")

    assert clear_res["status"] == "SUCCESS"

    assert SteeringController.has_directives() is False





def test_session_management_and_active_steering(agent_engine, workspace_root):

    """Verify fresh session on startup, session persistence, resumption, and active mid-flight steering."""

    from loom.clothos.session_manager import SessionManager

    from loom.clothos.steering_controller import SteeringController

    from loom.clothos.agent_cli import ClothOSAgentREPL



    # 1. Test SessionManager creation and auto-saving

    sm = SessionManager(workspace_root)

    sid = sm.current_session_id

    assert sid.startswith("session_")



    sm.save_session([

        {"user": "Synthesize a 432Hz ambient track", "agent": "Generated 432Hz track successfully."}

    ])

    sessions = sm.list_sessions()

    assert any(s["session_id"] == sid for s in sessions)



    # 2. Test REPL defaults to fresh session on startup

    repl_fresh = ClothOSAgentREPL(workspace_root)

    assert repl_fresh.engine.history == []

    assert repl_fresh.session_id != sid



    # 3. Test REPL loading previous session

    repl_resumed = ClothOSAgentREPL(workspace_root, session_id=sid)

    assert len(repl_resumed.engine.history) == 1

    assert repl_resumed.session_id == sid



    # 4. Test REPL slash commands for session management

    assert repl_fresh.handle_slash_command("/sessions") is False

    assert repl_fresh.handle_slash_command(f"/session open {sid}") is False

    assert len(repl_fresh.engine.history) == 1

    assert repl_fresh.handle_slash_command("/session new") is False

    assert repl_fresh.engine.history == []



    # 5. Test Natural Language Query: List Sessions

    nl_sess = agent_engine.process_query("list sessions")

    assert "ClothOS Historical Sessions" in nl_sess

    assert "/session open" in nl_sess



    # 6. Test Active Mid-Flight Steering while working

    SteeringController.inject_mid_flight("Live mid-flight directive: prioritize AVX2 SIMD")

    pending = SteeringController.poll_mid_flight_guidance()

    assert "Live mid-flight directive: prioritize AVX2 SIMD" in pending



    # Test External Queue persistence

    SteeringController.enqueue_external_steering("External queue test directive")

    pending_ext = SteeringController.poll_mid_flight_guidance()

    assert "External queue test directive" in pending_ext







def test_ui_progress_bars_and_usability_features(agent_engine, workspace_root):

    """Verify progress bars, multi-stage execution, hardware HUD, clipboard, exporter, and palette."""

    from loom.clothos.ui_progress import (

        ClothOSProgress,

        ClusterTelemetryHUD,

        ClipboardManager,

        SessionExporter,

        CommandPalette

    )

    from loom.clothos.agent_cli import ClothOSAgentREPL



    # 1. Test ClothOSProgress bar creation and step rendering

    prog = ClothOSProgress.create_progress(transient=True)

    assert prog is not None



    step_bar = ClothOSProgress.render_step_bar(3, 10, "polyglot_exec")

    assert "[Step 3/10]" in step_bar

    assert "30%" in step_bar

    assert "polyglot_exec" in step_bar



    # Test iterable tracking

    items = [1, 2, 3, 4]

    tracked = list(ClothOSProgress.track_iterable(items, description="Test Loop"))

    assert tracked == [1, 2, 3, 4]



    # Test multi-stage execution

    stage_results = ClothOSProgress.execute_multi_stage([

        ("Stage A: Init", lambda: "init_ok"),

        ("Stage B: Compute", lambda: 42)

    ], title="Unit Test Multi-Stage")

    assert stage_results == ["init_ok", 42]



    # 2. Test ClusterTelemetryHUD rendering

    hud = ClusterTelemetryHUD.render_hardware_dashboard()

    assert hud is not None

    assert "CLOTHOS CLUSTER HARDWARE" in str(hud.title)



    # 3. Test CommandPalette rendering

    palette = CommandPalette.render()

    assert palette is not None

    assert "COMMAND PALETTE" in str(palette.title)



    # 4. Test ClipboardManager

    copy_res = ClipboardManager.copy_text("ClothOS High-Performance Clipboard Test")

    assert copy_res.get("success") is True

    assert copy_res.get("chars") == len("ClothOS High-Performance Clipboard Test")



    md_sample = "Here is some code:\n```python\nprint('hello')\n```\nAnd more:\n```bash\ngit status\n```"

    code_blocks = ClipboardManager.extract_code_blocks(md_sample)

    assert len(code_blocks) == 2

    assert code_blocks[0] == "print('hello')"

    assert code_blocks[1] == "git status"



    # 5. Test SessionExporter

    test_hist = [

        {"user": "What is the Kuramoto coupling factor?", "agent": "The coupling factor $K$ determines phase locking:\n```python\nK = 1.42\n```"}

    ]

    exported_file = SessionExporter.export_to_markdown(

        history=test_hist,

        workspace_root=workspace_root,

        session_id="session_test_123",

        active_head="loom-sovereign"

    )

    assert exported_file.exists()

    content = exported_file.read_text(encoding="utf-8")

    assert "ClothOS Session Transcript" in content

    assert "Kuramoto coupling factor" in content

    assert "K = 1.42" in content



    # 6. Test REPL slash commands for usability

    repl = ClothOSAgentREPL(workspace_root)

    repl.engine.history = test_hist



    assert repl.handle_slash_command("/palette") is False

    assert repl.handle_slash_command("/cheatsheet") is False

    assert repl.handle_slash_command("/gpu") is False

    assert repl.handle_slash_command("/telemetry") is False

    assert repl.handle_slash_command("/copy") is False

    assert repl.handle_slash_command("/copy code") is False

    assert repl.handle_slash_command("/export") is False

    assert repl.handle_slash_command("/ls") is False

    assert repl.handle_slash_command("/consolidate Test Opus") is False







def test_selected_drillbit_needed_unbounded_timeout(workspace_root):

    """Verify that when a selected drillbit is needed, its timeout is unbounded (no timeout)."""

    from loom.clothos.agent_cli import ModelHead, ModelRouter



    # 1. Mount a sovereign head

    head = ModelHead.mount("loom-sovereign-70b")

    assert head.unbounded_timeout is True



    # 2. Spy on _dispatch to verify that effective_timeout is None when needed

    captured_timeout = []

    def mock_dispatch(messages, timeout=None):

        captured_timeout.append(timeout)

        return "Thought: Deep theory.\nFinal Answer: Kuramoto phase locked."



    orig_dispatch = head._dispatch

    head._dispatch = mock_dispatch

    try:

        # Call with an explicit timeout=10.0, but needed=True

        res = head.query([{"role": "user", "content": "Explain Kuramoto synchronization"}], timeout=10.0, needed=True)

        assert res is not None

        assert captured_timeout[0] is None, f"Expected None (unbounded), got {captured_timeout[0]}"



        # Test ModelRouter resolution and dispatch

        captured_timeout.clear()

        router_res = ModelRouter.dispatch_query(

            [{"role": "user", "content": "Explain Kuramoto synchronization using 70b"}],

            prompt_hint="70b",

            timeout=15.0

        )

        assert router_res is not None

        assert captured_timeout[-1] is None, f"ModelRouter expected None (unbounded), got {captured_timeout[-1]}"

        # Ensure head was NOT placed into cooldown

        assert head.label not in ModelRouter._cooldowns or ModelRouter._cooldowns[head.label] == 0

    finally:

        head._dispatch = orig_dispatch







def test_glowing_aura_and_activity_details_tracking(workspace_root):

    """Verify sovereign glowing aura, waveform shimmer, and rich activity details tracking."""

    from loom.clothos.activity_tracker import CurrentlyDoing, GlowActivityIndicator

    from loom.clothos.agent_cli import ClothOSAgentREPL



    # 1. Test Glow Wave and Glyph generation

    wave = GlowActivityIndicator.get_glow_wave(width=16)

    assert len(wave) > 0

    assert any(c in wave for c in ["▂", "▃", "▄", "▅", "▆", "▇", "█"])



    glyph = GlowActivityIndicator.get_pulse_glyph()

    assert any(g in glyph for g in ["■", "▲", "◆", "►", "◈", "●", "✦", "█"])



    # 2. Test CurrentlyDoing with granular operational details

    CurrentlyDoing.set(

        task_desc="Synthesize 100MB+ Audio Opus",

        phase="SYNTHESIS",

        drillbit="loom-sovereign",

        sub_goal="Step 2/4: PCM Waveform Concatenation",

        target="artifacts/symphony_opus.wav",

        hardware="Node 1 (skyTech) ➔ RTX 3060 CUDA (12GB)",

        storage_tier="Tier 0 (RAM Scratchpad) ➔ Tier 2 (USB E:/)",

        metrics="Buffer: 64.2 MB / 100MB+ • 48kHz Float",

        steering="Prioritize AVX2 SIMD vectorization"

    )



    details = CurrentlyDoing.get_details()

    assert details["sub_goal"] == "Step 2/4: PCM Waveform Concatenation"

    assert details["target"] == "artifacts/symphony_opus.wav"

    assert "RTX 3060" in details["hardware"]

    assert "Tier 2" in details["storage_tier"]

    assert "64.2 MB" in details["metrics"]



    # 3. Test dynamic real-time detail updates

    CurrentlyDoing.update_details(metrics="Buffer: 104.5 MB / 100MB+ • Complete")

    assert "104.5 MB" in CurrentlyDoing.get_details()["metrics"]



    # 4. Test Glowing Panel rendering

    glow_panel = CurrentlyDoing.render_glow_panel()

    assert glow_panel is not None

    assert "CLOTHOS" in str(glow_panel.title) and "COGNITIVE" in str(glow_panel.title)



    # 5. Test inline glow badge for toolbars

    badge = CurrentlyDoing.get_glow_badge()

    assert "CURRENT" in badge

    assert "Synthesize 100MB+ Audio Opus" in badge



    # 6. Test REPL slash commands for glowing HUD

    repl = ClothOSAgentREPL(workspace_root)

    assert repl.handle_slash_command("/glow") is False

    assert repl.handle_slash_command("/aura") is False

    assert repl.handle_slash_command("/hud") is False







def test_live_shimmer_hud_and_bicameral_fast_heavy_routing(workspace_root):

    """Verify active live shimmer HUD 12fps animation and bicameral fast-pilot + heavy-flagship execution."""

    import time

    from loom.clothos.activity_tracker import CurrentlyDoing, LiveShimmerHUD

    from loom.clothos.agent_cli import ModelRouter, ModelHead, ClothOSAgentREPL



    # 1. Test LiveShimmerHUD animation context manager

    CurrentlyDoing.set("Testing Live Shimmer 12 FPS", phase="COGNITION", sub_goal="Shimmer Verification")

    with CurrentlyDoing.live_shimmer(fps=15) as hud:

        assert hud._thread is not None

        assert hud._thread.is_alive()

        time.sleep(0.15)

        # Test pause & resume

        hud.pause()

        assert hud._paused is True

        hud.resume()

        assert hud._paused is False

    # Verify stopped cleanly

    assert not hud._thread.is_alive()



    # 2. Test ModelRouter Bicameral Speculative Mode

    ModelRouter.set_mode(ModelRouter.MODE_BICAMERAL)

    assert ModelRouter.get_mode() == ModelRouter.MODE_BICAMERAL

    assert ModelRouter._fast_pilot_label == "loom-sovereign-fast"

    assert ModelRouter._heavy_flagship_label == "loom-sovereign"



    # Mock heads to test bicameral pipeline

    pilot = ModelHead.mount("loom-sovereign-fast")

    flagship = ModelHead.mount("loom-sovereign")

    cortex_70b = ModelHead.mount("loom-sovereign-70b")



    orig_pilot_dispatch = pilot._dispatch

    orig_flagship_dispatch = flagship._dispatch

    orig_70b_dispatch = cortex_70b._dispatch



    pilot_called = []

    flagship_called = []



    mock_pilot = lambda msgs, timeout=None, **kw: pilot_called.append(True) or "Fast tactical triage: build distributed router"

    mock_flagship = lambda msgs, timeout=None, **kw: flagship_called.append(True) or "Flagship deep deliverable: complete code"



    pilot._dispatch = mock_pilot

    flagship._dispatch = mock_flagship

    cortex_70b._dispatch = mock_flagship



    try:

        reply = ModelRouter.dispatch_query(

            [{"role": "user", "content": "Build distributed API router"}],

            prompt_hint="Build distributed API router"

        )

        assert len(pilot_called) > 0, "Fast pilot was not invoked"

        assert len(flagship_called) > 0, "Heavy flagship was not invoked"

        assert "complete code" in reply

    finally:

        pilot._dispatch = orig_pilot_dispatch

        flagship._dispatch = orig_flagship_dispatch

        cortex_70b._dispatch = orig_70b_dispatch

        ModelRouter.set_mode(ModelRouter.MODE_AUTO)



    # 3. Test /bicameral slash commands

    repl = ClothOSAgentREPL(workspace_root)

    assert repl.handle_slash_command("/bicameral on") is False

    assert ModelRouter.get_mode() == ModelRouter.MODE_BICAMERAL

    assert repl.handle_slash_command("/bicameral status") is False

    assert repl.handle_slash_command("/bicameral off") is False

    assert ModelRouter.get_mode() == ModelRouter.MODE_AUTO





def test_sovereign_terminal_usability_and_antigravity_clearing(workspace_root):

    """Verify real-time token throughput counter, command shorthands, and complete antigravity removal."""

    import io

    import sys

    import os

    import re

    from loom.clothos.agent_cli import ClothOSAgentREPL, ThinkingStream, ModelRouter

    from loom.clothos.terminal import make_bottom_toolbar, format_powerline_prompt



    # 1. Test ThinkingStream real-time token throughput meter

    ThinkingStream.enable()

    assert ThinkingStream.is_enabled()

    ThinkingStream.start_stream(label="Neural Throughput Test")

    ThinkingStream.stream_chunk("Synthesizing ")

    ThinkingStream.stream_chunk("harmonic ")

    ThinkingStream.stream_chunk("polynomials ")

    ThinkingStream.stream_chunk("in R^4")

    assert ThinkingStream._stream_token_count >= 4

    assert ThinkingStream._stream_char_count > 0

    ThinkingStream.end_stream()

    assert not ThinkingStream._streaming_active



    # 2. Test command shorthands in ClothOSAgentREPL

    repl = ClothOSAgentREPL(workspace_root)



    # Shorthand '?' or '/h' for help

    assert repl.handle_slash_command("?") is False

    assert repl.handle_slash_command("/h") is False



    # Shorthand '/b' for bicameral

    assert repl.handle_slash_command("/b") is False

    assert repl.handle_slash_command("/b on") is False

    assert ModelRouter.get_mode() == ModelRouter.MODE_BICAMERAL

    assert repl.handle_slash_command("/b off") is False

    assert ModelRouter.get_mode() == ModelRouter.MODE_AUTO



    # Shorthand '/g' for gpu telemetry

    assert repl.handle_slash_command("/g") is False



    # Shorthand '/s' for steer

    assert repl.handle_slash_command("/s") is False



    # Shorthand '/a' for abort

    assert repl.handle_slash_command("/a") is False



    # Shorthand '/d' for doing / live HUD

    assert repl.handle_slash_command("/d") is False



    # Shorthand '/c' for clear

    repl.engine.history.append({"user": "test", "agent": "reply"})

    assert len(repl.engine.history) == 1

    assert repl.handle_slash_command("/c") is False

    assert len(repl.engine.history) == 0



    # Shorthand '/q' for quit

    assert repl.handle_slash_command("/q") is True



    # 3. Test bottom toolbar and powerline prompt

    toolbar = make_bottom_toolbar()

    toolbar_str = str(toolbar)

    assert "CURRENT" in toolbar_str

    assert "2-Node" in toolbar_str



    prompt = format_powerline_prompt(workspace_root=workspace_root, active_head="loom-sovereign")

    assert "CLOTHOS" in str(prompt)



    # 4. Rigorous verification: Zero occurrences of 'antigravity' in loom/clothos

    clothos_dir = Path(r"C:\Users\natsa\Documents\loom-fabric\loom\clothos")

    ag_pattern = re.compile(r"antigravity", re.IGNORECASE)

    matches = []

    for f in clothos_dir.glob("*.py"):

        content = f.read_text(encoding="utf-8", errors="ignore")

        for line_no, line in enumerate(content.splitlines(), 1):

            if ag_pattern.search(line):

                matches.append(f"{f.name}:{line_no}: {line.strip()}")



    assert len(matches) == 0, f"Found unexpected antigravity references: {matches}"





def test_bfcl_function_calling_and_schema_coercion(workspace_root):

    """Verify Berkeley Function Calling Leaderboard (BFCL) multi-tool parsing, schema coercion, and abstention."""

    from loom.clothos.bfcl_engine import BFCLEngine

    from loom.clothos.bfcl_eval import BFCLBenchmarkRunner

    from loom.clothos.agent_cli import ClothOSAgentREPL, ClothOSAgentEngine



    # 1. Test argument coercion engine

    schema = {

        "limit": "integer (optional)",

        "ratio": "float",

        "enabled": "boolean",

        "tags": "list of strings",

        "metadata": "dict"

    }

    raw = {

        "limit": "42",

        "ratio": "0.85",

        "enabled": "true",

        "tags": '["ai", "sovereign", "clothos"]',

        "metadata": '{"cluster": "node1"}'

    }

    coerced = BFCLEngine.coerce_arguments("test_tool", raw, schema)

    assert coerced["limit"] == 42

    assert coerced["ratio"] == 0.85

    assert coerced["enabled"] is True

    assert coerced["tags"] == ["ai", "sovereign", "clothos"]

    assert coerced["metadata"] == {"cluster": "node1"}



    # 2. Test Parallel Function Calling extraction

    parallel_reply = """Thought: Need to read both files concurrently.

[

  {"name": "dev_view_file", "arguments": {"path": "a.py"}},

  {"name": "dev_view_file", "arguments": {"path": "b.py"}}

]"""

    calls = BFCLEngine.parse_all_tool_calls(parallel_reply)

    assert len(calls) == 2

    assert calls[0][0] == "dev_view_file" and calls[0][1]["path"] == "a.py"

    assert calls[1][0] == "dev_view_file" and calls[1][1]["path"] == "b.py"



    # 3. Test Multi-tag XML extraction

    xml_reply = """<tool_call>{"name": "cns_telemetry", "arguments": {}}</tool_call>

<tool_call>{"name": "gpu_telemetry", "arguments": {"gpu_index": "0"}}</tool_call>"""

    xml_calls = BFCLEngine.parse_all_tool_calls(xml_reply)

    assert len(xml_calls) == 2

    assert xml_calls[0][0] == "cns_telemetry"

    assert xml_calls[1][0] == "gpu_telemetry"



    # 4. Test Irrelevance Abstention (Zero Tool Calls)

    abstain_reply = "Thought: 2+2 is 4. No tool required.\nAction: No tool needed.\nFinal Answer: 4"

    assert len(BFCLEngine.parse_all_tool_calls(abstain_reply)) == 0



    # 5. Test full BFCL Benchmark Runner suite (8/8 cases pass)

    bench_data = BFCLBenchmarkRunner.run_benchmark()

    assert bench_data["total_tests"] == 8

    assert bench_data["passed_tests"] == 8

    assert bench_data["pass_rate_pct"] == 100.0



    # 6. Test /bfcl slash command in ClothOSAgentREPL

    repl = ClothOSAgentREPL(workspace_root)

    assert repl.handle_slash_command("/bfcl") is False





def test_directory_context_auto_reconnaissance(workspace_root):

    """Verify zero-config directory auto-context scan, 8-bit retro panel, and /context slash command."""

    from loom.clothos.directory_context import DirectoryContextEngine

    from loom.clothos.agent_cli import ClothOSAgentREPL



    # 1. Scan directory

    info = DirectoryContextEngine.scan_directory(workspace_root)

    assert info is not None

    assert "workspace_name" in info

    assert "project_type" in info

    assert info["total_files"] >= 0

    assert "recommendations" in info

    assert len(info["recommendations"]) > 0



    # 2. Render 8-bit retro-scientific panel

    panel = DirectoryContextEngine.render_context_panel(workspace_root)

    assert panel is not None

    assert "AUTO-RECONNAISSANCE" in str(panel.title)



    # 3. Test slash commands

    repl = ClothOSAgentREPL(workspace_root)

    assert repl.handle_slash_command("/context") is False

    assert repl.handle_slash_command("/recs") is False

    assert repl.handle_slash_command("/recon") is False



def test_computer_wisdom_windows_cmd_and_hardware_curriculum(workspace_root):
    """Verify computer wisdom engine, Windows CMD translation, hardware prober, and /teach commands."""
    from loom.clothos.computer_wisdom import (
        ComputerWisdomEngine,
        HardwareProber,
        WindowsCommandTranslator,
        FOUNDATIONAL_COMPUTER_WISDOM
    )
    from loom.clothos.agent_cli import ClothOSAgentREPL, ToolRegistry
    from loom.clothos.wisdom_engine import wisdom_engine
    from loom.clothos.self_training_knowledge_engine import SelfTrainingKnowledgeEngine

    # 1. Test ComputerWisdomEngine initialization
    ComputerWisdomEngine.initialize()
    assert len(ComputerWisdomEngine._axioms) >= len(FOUNDATIONAL_COMPUTER_WISDOM)
    assert "AXIOM_WIN_CMD_BUILTINS" in ComputerWisdomEngine._axioms
    assert "AXIOM_HW_DUAL_GPU_TOPOLOGY" in ComputerWisdomEngine._axioms
    assert "AXIOM_DEV_PYTHON_WINDOWS" in ComputerWisdomEngine._axioms

    # 2. Test HardwareProber
    hw = HardwareProber.probe_all()
    assert hw["os_name"] in ("Windows", "win32") or len(hw["os_name"]) > 0
    assert hw["cpu_logical_cores"] >= 1
    assert "RTX 3060" in hw["gpu_nvidia"]
    assert "RX 580" in hw["gpu_amd"]

    # 3. Test WindowsCommandTranslator
    assert WindowsCommandTranslator.translate_posix_to_cmd("ls -la") == "dir -la"
    assert WindowsCommandTranslator.translate_posix_to_cmd("cat README.md") == "type README.md"
    assert WindowsCommandTranslator.translate_posix_to_cmd("grep error log.txt") == "findstr error log.txt"
    assert WindowsCommandTranslator.translate_posix_to_cmd("which python") == "where.exe python"
    assert WindowsCommandTranslator.translate_posix_to_cmd("rm -rf old_build") == "rmdir /s /q old_build"
    assert WindowsCommandTranslator.translate_posix_to_cmd("touch new.txt") == "type nul > new.txt"

    # 4. Test teaching new wisdom dynamically
    ratified = ComputerWisdomEngine.teach(
        domain="WINDOWS",
        title="PowerShell Process Filtering",
        principle="Use Get-Process | Where-Object WorkingSet64 -gt 100MB for memory audits."
    )
    assert ratified["axiom_id"] in ComputerWisdomEngine._axioms
    assert ratified["domain"] == "WINDOWS"

    # 5. Test ToolRegistry integration with new tools
    tools = ToolRegistry(workspace_root)
    assert "hardware_probe" in tools.tools
    assert "wisdom_teach" in tools.tools
    assert "windows_cmd_exec" in tools.tools

    hw_tool_res = tools.execute("hardware_probe")
    assert "cpu_logical_cores" in hw_tool_res

    teach_res = tools.execute(
        "wisdom_teach",
        domain="HARDWARE",
        title="AVX2 SIMD Alignment",
        principle="Always align 256-bit AVX2 vectors to 32-byte boundaries."
    )
    assert "axiom_id" in teach_res

    cmd_res = tools.execute("windows_cmd_exec", cmd="ver")
    assert cmd_res.get("returncode") == 0
    assert "Windows" in cmd_res.get("stdout", "")

    # 6. Test REPL slash commands (/teach, /wisdom, /curriculum)
    repl = ClothOSAgentREPL(workspace_root)
    assert repl.handle_slash_command("/teach") is False
    assert repl.handle_slash_command("/teach windows") is False
    assert repl.handle_slash_command("/teach hw") is False
    assert repl.handle_slash_command('/teach add WINDOWS "Robocopy Mirroring" "Use robocopy /mir /mt:8"') is False
    assert repl.handle_slash_command("/t") is False
    assert repl.handle_slash_command("/w") is False

    # 7. Test integration with wisdom_engine & self_training
    assert any("CMD" in k or "GPU" in k or "WIN" in k for k in wisdom_engine.axioms.keys())
    trainer = SelfTrainingKnowledgeEngine(workspace_root)
    k_items = trainer.ingest_truthful_knowledge()
    assert any(item.source_type == "COMPUTER_WISDOM" for item in k_items)
