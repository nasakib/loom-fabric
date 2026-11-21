# Script to safely apply biomimetic drive endpoints and UI to loom/fabric/dashboard_server.py
import sys

def apply():
    with open('loom/fabric/dashboard_server.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Pydantic Models
    target_models = """class GenerateDrugRequest(BaseModel):
    name: Optional[str] = None
    indication: str = "TREATMENT_RESISTANT_PTSD_AND_COGNITIVE_RIGIDITY"
    target_profile: str = "SELECTIVE_5HT2A_TRKB_PLASTOGEN"
"""
    repl_models = """class GenerateDrugRequest(BaseModel):
    name: Optional[str] = None
    indication: str = "TREATMENT_RESISTANT_PTSD_AND_COGNITIVE_RIGIDITY"
    target_profile: str = "SELECTIVE_5HT2A_TRKB_PLASTOGEN"

class BiomimeticNicotinePulseRequest(BaseModel):
    dose: float = 0.35
    reason: str = "Prefrontal SNR sharpening under cognitive friction"

class BiomimeticEndorphinRewardRequest(BaseModel):
    breakthrough_magnitude: float = 0.85
    reason: str = "Goal achieved / validation verified"

class BiomimeticRestRequest(BaseModel):
    problem_description: str = "Associative impasse resolution"
    context: Optional[Dict[str, Any]] = None

class BiomimeticDopaminePursuitRequest(BaseModel):
    effort_intensity: float = 0.5
    task_description: str = "Active inference exploration"
    prediction_error: float = 0.0

class BiomimeticEurekaRequest(BaseModel):
    force_breakthrough: bool = True
    insight_summary: Optional[str] = None
"""
    assert target_models in content, "target_models not found"
    content = content.replace(target_models, repl_models, 1)

    # 2. API Endpoints
    target_endpoints = """    drug = brain_structure_forge.create_new_drug_structure(
        name=req.name,
        indication=req.indication,
        target_profile=req.target_profile,
    )
    return {"status": "SUCCESS", "drug": drug.to_dict()}


@app.get("/api/vault/stats")"""

    repl_endpoints = """    drug = brain_structure_forge.create_new_drug_structure(
        name=req.name,
        indication=req.indication,
        target_profile=req.target_profile,
    )
    return {"status": "SUCCESS", "drug": drug.to_dict()}


# -------------------------------------------------------------
# Biomimetic Cognitive Drive & Reward Architecture Endpoints
# -------------------------------------------------------------

@app.get("/api/neuro/biomimetic/state")
def get_biomimetic_state_api() -> Dict[str, Any]:
    \"\"\"Returns real-time biomimetic drive state: Dopamine, Endorphins, Nicotinic tone, SNR, and Subconscious incubation.\"\"\"
    from loom.neuro.biomimetic_drive import biomimetic_drive
    return biomimetic_drive.get_snapshot()


@app.post("/api/neuro/nicotine/pulse")
def post_nicotine_pulse_api(req: BiomimeticNicotinePulseRequest) -> Dict[str, Any]:
    \"\"\"Administers on-demand nicotinic pulse (alpha7 and alpha4beta2 nAChR) to sharpen prefrontal SNR.\"\"\"
    from loom.neuro.biomimetic_drive import biomimetic_drive
    return biomimetic_drive.administer_nicotine_pulse(dose=req.dose, reason=req.reason)


@app.post("/api/neuro/reward/endorphin_cascade")
def post_endorphin_cascade_api(req: BiomimeticEndorphinRewardRequest) -> Dict[str, Any]:
    \"\"\"Consummates goal achievement: dopamine resolves into an endorphin cascade for peace & LTP consolidation.\"\"\"
    from loom.neuro.biomimetic_drive import biomimetic_drive
    return biomimetic_drive.trigger_endorphin_reward(breakthrough_magnitude=req.breakthrough_magnitude, reason=req.reason)


@app.post("/api/neuro/rest/enter")
def post_rest_enter_api(req: BiomimeticRestRequest) -> Dict[str, Any]:
    \"\"\"Transitions conscious executive to rest and hands off the seed problem to subconscious associative incubation.\"\"\"
    from loom.neuro.biomimetic_drive import biomimetic_drive
    return biomimetic_drive.transition_to_rest_and_subconscious(
        problem_description=req.problem_description,
        context=req.context,
    )


@app.post("/api/neuro/rest/wake")
def post_rest_wake_api(req: BiomimeticEurekaRequest) -> Dict[str, Any]:
    \"\"\"Simulates incubation step or forces an Aha! epiphany breakthrough that awakens the conscious mind.\"\"\"
    from loom.neuro.biomimetic_drive import biomimetic_drive
    if req.insight_summary:
        return biomimetic_drive.trigger_eureka_epiphany(insight_summary=req.insight_summary)
    return biomimetic_drive.subconscious_incubation_step(force_breakthrough=req.force_breakthrough)


@app.post("/api/neuro/dopamine/pursuit")
def post_dopamine_pursuit_api(req: BiomimeticDopaminePursuitRequest) -> Dict[str, Any]:
    \"\"\"Mobilizes dopamine to fuel goal-directed effort and focus.\"\"\"
    from loom.neuro.biomimetic_drive import biomimetic_drive
    return biomimetic_drive.advance_dopaminergic_pursuit(
        effort_intensity=req.effort_intensity,
        task_description=req.task_description,
        prediction_error=req.prediction_error,
    )


@app.get("/api/vault/stats")"""

    assert target_endpoints in content, "target_endpoints not found"
    content = content.replace(target_endpoints, repl_endpoints, 1)

    # 3. tab-neuro HTML enhancement
    # Let's see the tab-neuro container:
    target_neuro_html = """        <!-- Tab: Sovereign Neurochemistry & Pharmacology -->
        <div id="tab-neuro" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <div>
                        <span class="card-title">🧪 SOVEREIGN NEUROCHEMISTRY & PHARMACOLOGY</span>
                        <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">
                            Neuromodulated Active Inference dynamically modulating observation precision, prior rigidity, learning rates, and attractor stability.
                        </div>
                    </div>
                    <span class="pill pill-purple" id="neuro-tab-status">STATUS: HOMEOSTATIC</span>
                </div>

                <!-- Transmitter Grid -->
                <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:12px; margin-bottom:18px;">
                    <div style="background:var(--obsidian); padding:12px; border-radius:6px; border:1px solid var(--border);">
                        <div style="display:flex; justify-content:space-between; font-size:11px; font-family:monospace; margin-bottom:4px;">
                            <span style="color:#ffb300;">Dopamine (DA)</span>
                            <strong id="tab-val-da" style="color:#ffb300;">1.00</strong>
                        </div>
                        <div style="background:#1e293b; height:6px; border-radius:3px; overflow:hidden;">
                            <div id="tab-bar-da" style="background:#ffb300; width:33%; height:100%; transition:width 0.3s;"></div>
                        </div>
                        <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">Observation Precision &Pi;<sub>obs</sub></div>
                    </div>

                    <div style="background:var(--obsidian); padding:12px; border-radius:6px; border:1px solid var(--border);">
                        <div style="display:flex; justify-content:space-between; font-size:11px; font-family:monospace; margin-bottom:4px;">
                            <span style="color:#d500f9;">Serotonin (5-HT)</span>
                            <strong id="tab-val-5ht" style="color:#d500f9;">1.00</strong>
                        </div>
                        <div style="background:#1e293b; height:6px; border-radius:3px; overflow:hidden;">
                            <div id="tab-bar-5ht" style="background:#d500f9; width:33%; height:100%; transition:width 0.3s;"></div>
                        </div>
                        <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">Prior Precision & REBUS</div>
                    </div>

                    <div style="background:var(--obsidian); padding:12px; border-radius:6px; border:1px solid var(--border);">
                        <div style="display:flex; justify-content:space-between; font-size:11px; font-family:monospace; margin-bottom:4px;">
                            <span style="color:#00e5ff;">Acetylcholine (ACh)</span>
                            <strong id="tab-val-ach" style="color:#00e5ff;">1.00</strong>
                        </div>
                        <div style="background:#1e293b; height:6px; border-radius:3px; overflow:hidden;">
                            <div id="tab-bar-ach" style="background:#00e5ff; width:33%; height:100%; transition:width 0.3s;"></div>
                        </div>
                        <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">Synaptic Learning Rate &eta;</div>
                    </div>

                    <div style="background:var(--obsidian); padding:12px; border-radius:6px; border:1px solid var(--border);">
                        <div style="display:flex; justify-content:space-between; font-size:11px; font-family:monospace; margin-bottom:4px;">
                            <span style="color:#ff5252;">Norepinephrine (NE)</span>
                            <strong id="tab-val-ne" style="color:#ff5252;">1.00</strong>
                        </div>
                        <div style="background:#1e293b; height:6px; border-radius:3px; overflow:hidden;">
                            <div id="tab-bar-ne" style="background:#ff5252; width:33%; height:100%; transition:width 0.3s;"></div>
                        </div>
                        <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">Exploration Entropy H</div>
                    </div>

                    <div style="background:var(--obsidian); padding:12px; border-radius:6px; border:1px solid var(--border);">
                        <div style="display:flex; justify-content:space-between; font-size:11px; font-family:monospace; margin-bottom:4px;">
                            <span style="color:#00e676;">GABA / Glutamate</span>
                            <strong id="tab-val-gaba" style="color:#00e676;">1.00</strong>
                        </div>
                        <div style="background:#1e293b; height:6px; border-radius:3px; overflow:hidden;">
                            <div id="tab-bar-gaba" style="background:#00e676; width:33%; height:100%; transition:width 0.3s;"></div>
                        </div>
                        <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">E/I Attractor Stability</div>
                    </div>
                </div>

                <!-- Compound Administration -->
                <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px; border:1px solid var(--border);">
                    <span style="font-size:11px; font-weight:800; color:var(--amethyst); text-transform:uppercase;">Administer Compound:</span>
                    <button class="btn" style="color:#ffb300; border-color:rgba(255,179,0,0.4);" onclick="administerTabCompound('nootropic_hyperfocus')">⚡ Nootropic Hyperfocus</button>
                    <button class="btn" style="color:#d500f9; border-color:rgba(213,0,249,0.4);" onclick="administerTabCompound('rebus_psychedelic_divergence')">🍄 REBUS Psychedelic Divergence</button>
                    <button class="btn" style="color:#00e5ff; border-color:rgba(0,229,255,0.4);" onclick="administerTabCompound('cholinergic_crystallizer')">📚 Cholinergic Crystallizer</button>
                    <button class="btn" style="color:#00e676; border-color:rgba(0,230,118,0.4);" onclick="administerTabCompound('gabaergic_calm')">🧘 GABAergic Calm</button>
                    <button class="btn" style="color:#fff;" onclick="administerTabCompound('homeostatic_reset')">🔄 Homeostatic Reset</button>
                </div>
            </div>
        </div>"""

    repl_neuro_html = """        <!-- Tab: Sovereign Neurochemistry & Biomimetic Cognitive Drive -->
        <div id="tab-neuro" class="tab-content">
            <!-- 1. Neuromodulated Transmitter Grid Card -->
            <div class="card" style="margin-bottom:16px;">
                <div class="card-header">
                    <div>
                        <span class="card-title">🧪 SOVEREIGN NEUROCHEMISTRY & TRANSMITTER SUBSTRATE</span>
                        <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">
                            Neuromodulated Active Inference dynamically modulating observation precision, prior rigidity, learning rates, and attractor stability.
                        </div>
                    </div>
                    <span class="pill pill-purple" id="neuro-tab-status">STATUS: HOMEOSTATIC</span>
                </div>

                <!-- Transmitter Grid -->
                <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:12px; margin-bottom:18px;">
                    <div style="background:var(--obsidian); padding:12px; border-radius:6px; border:1px solid var(--border);">
                        <div style="display:flex; justify-content:space-between; font-size:11px; font-family:monospace; margin-bottom:4px;">
                            <span style="color:#ffb300;">Dopamine (DA)</span>
                            <strong id="tab-val-da" style="color:#ffb300;">1.00</strong>
                        </div>
                        <div style="background:#1e293b; height:6px; border-radius:3px; overflow:hidden;">
                            <div id="tab-bar-da" style="background:#ffb300; width:33%; height:100%; transition:width 0.3s;"></div>
                        </div>
                        <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">Observation Precision &Pi;<sub>obs</sub></div>
                    </div>

                    <div style="background:var(--obsidian); padding:12px; border-radius:6px; border:1px solid var(--border);">
                        <div style="display:flex; justify-content:space-between; font-size:11px; font-family:monospace; margin-bottom:4px;">
                            <span style="color:#d500f9;">Serotonin (5-HT)</span>
                            <strong id="tab-val-5ht" style="color:#d500f9;">1.00</strong>
                        </div>
                        <div style="background:#1e293b; height:6px; border-radius:3px; overflow:hidden;">
                            <div id="tab-bar-5ht" style="background:#d500f9; width:33%; height:100%; transition:width 0.3s;"></div>
                        </div>
                        <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">Prior Precision & REBUS</div>
                    </div>

                    <div style="background:var(--obsidian); padding:12px; border-radius:6px; border:1px solid var(--border);">
                        <div style="display:flex; justify-content:space-between; font-size:11px; font-family:monospace; margin-bottom:4px;">
                            <span style="color:#00e5ff;">Acetylcholine (ACh)</span>
                            <strong id="tab-val-ach" style="color:#00e5ff;">1.00</strong>
                        </div>
                        <div style="background:#1e293b; height:6px; border-radius:3px; overflow:hidden;">
                            <div id="tab-bar-ach" style="background:#00e5ff; width:33%; height:100%; transition:width 0.3s;"></div>
                        </div>
                        <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">Synaptic Learning Rate &eta;</div>
                    </div>

                    <div style="background:var(--obsidian); padding:12px; border-radius:6px; border:1px solid var(--border);">
                        <div style="display:flex; justify-content:space-between; font-size:11px; font-family:monospace; margin-bottom:4px;">
                            <span style="color:#ff5252;">Norepinephrine (NE)</span>
                            <strong id="tab-val-ne" style="color:#ff5252;">1.00</strong>
                        </div>
                        <div style="background:#1e293b; height:6px; border-radius:3px; overflow:hidden;">
                            <div id="tab-bar-ne" style="background:#ff5252; width:33%; height:100%; transition:width 0.3s;"></div>
                        </div>
                        <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">Exploration Entropy H</div>
                    </div>

                    <div style="background:var(--obsidian); padding:12px; border-radius:6px; border:1px solid var(--border);">
                        <div style="display:flex; justify-content:space-between; font-size:11px; font-family:monospace; margin-bottom:4px;">
                            <span style="color:#00e676;">GABA / Glutamate</span>
                            <strong id="tab-val-gaba" style="color:#00e676;">1.00</strong>
                        </div>
                        <div style="background:#1e293b; height:6px; border-radius:3px; overflow:hidden;">
                            <div id="tab-bar-gaba" style="background:#00e676; width:33%; height:100%; transition:width 0.3s;"></div>
                        </div>
                        <div style="font-size:10px; color:var(--text-muted); margin-top:4px;">E/I Attractor Stability</div>
                    </div>
                </div>

                <!-- Compound Administration -->
                <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px; border:1px solid var(--border);">
                    <span style="font-size:11px; font-weight:800; color:var(--amethyst); text-transform:uppercase;">Administer Compound:</span>
                    <button class="btn" style="color:#ffb300; border-color:rgba(255,179,0,0.4);" onclick="administerTabCompound('nootropic_hyperfocus')">⚡ Nootropic Hyperfocus</button>
                    <button class="btn" style="color:#d500f9; border-color:rgba(213,0,249,0.4);" onclick="administerTabCompound('rebus_psychedelic_divergence')">🍄 REBUS Psychedelic Divergence</button>
                    <button class="btn" style="color:#00e5ff; border-color:rgba(0,229,255,0.4);" onclick="administerTabCompound('cholinergic_crystallizer')">📚 Cholinergic Crystallizer</button>
                    <button class="btn" style="color:#00e676; border-color:rgba(0,230,118,0.4);" onclick="administerTabCompound('gabaergic_calm')">🧘 GABAergic Calm</button>
                    <button class="btn" style="color:#fff;" onclick="administerTabCompound('homeostatic_reset')">🔄 Homeostatic Reset</button>
                </div>
            </div>

            <!-- 2. Biomimetic Cognitive Architecture & Reward Circuits Card -->
            <div class="card">
                <div class="card-header" style="border-bottom:1px solid var(--border); padding-bottom:12px; margin-bottom:16px;">
                    <div>
                        <span class="card-title">🧬 BIOMIMETIC COGNITIVE DRIVE & REWARD DYNAMICS</span>
                        <div style="font-size:11px; color:var(--text-muted); margin-top:3px;">
                            Biomimicry the good way: Dopaminergic Pursuit &rarr; Endorphinergic Consummatory Reward • Titrated &alpha;<sub>7</sub>/&alpha;<sub>4</sub>&beta;<sub>2</sub> Nicotinic Gating • Stand-down Rest & Subconscious Incubation when stuck.
                        </div>
                    </div>
                    <div style="display:flex; gap:8px; align-items:center;">
                        <span class="pill pill-cyan" id="bio-nicotine-rec">⚡ FOCUS OPTIMAL</span>
                        <span class="pill pill-purple" id="bio-tab-mode">MODE: CONSCIOUS_DRIVE</span>
                        <button class="btn" onclick="refreshBiomimeticState()">🔄 Refresh Drive</button>
                    </div>
                </div>

                <!-- Biomimetic Core 4-Pillar Grid -->
                <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:14px; margin-bottom:20px;">
                    <!-- Pillar 1: Dopaminergic Pursuit -->
                    <div style="background:var(--obsidian); padding:14px; border-radius:8px; border:1px solid rgba(255,179,0,0.3); display:flex; flex-direction:column; justify-content:space-between;">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                                <span style="font-size:11px; font-weight:800; color:#ffb300; text-transform:uppercase;">1. Dopaminergic Pursuit</span>
                                <span class="pill" style="background:rgba(255,179,0,0.15); color:#ffb300; border:1px solid rgba(255,179,0,0.3); font-size:9px;">D1/D2 WANTING</span>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:18px; font-family:monospace; font-weight:bold; color:#ffb300; margin-bottom:6px;">
                                <span id="bio-val-da">1.05</span>
                                <span style="font-size:11px; color:var(--text-muted); font-weight:normal; align-self:flex-end;">Baseline 1.00</span>
                            </div>
                            <div style="background:#1e293b; height:7px; border-radius:4px; overflow:hidden; margin-bottom:8px;">
                                <div id="bio-bar-da" style="background:#ffb300; width:42%; height:100%; transition:width 0.3s;"></div>
                            </div>
                            <div style="font-size:10px; color:var(--text-muted); line-height:1.4; margin-bottom:10px;">
                                Fuels anticipation, active inference, hypothesis generation, and computational vigor.
                                <div style="margin-top:4px; color:#cbd5e1;">Effort Expended: <strong id="bio-val-effort" style="color:#ffb300;">0.00</strong></div>
                            </div>
                        </div>
                        <button class="btn" style="width:100%; color:#ffb300; border-color:rgba(255,179,0,0.4); font-size:11px; padding:6px 8px;" onclick="mobilizeDopamine()">⚡ Mobilize Effort (DA+)</button>
                    </div>

                    <!-- Pillar 2: Endorphinergic Consummatory Reward -->
                    <div style="background:var(--obsidian); padding:14px; border-radius:8px; border:1px solid rgba(16,185,129,0.3); display:flex; flex-direction:column; justify-content:space-between;">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                                <span style="font-size:11px; font-weight:800; color:#10b981; text-transform:uppercase;">2. Endorphin Reward</span>
                                <span class="pill" style="background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3); font-size:9px;">&mu;-OPIOID (MOR)</span>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:18px; font-family:monospace; font-weight:bold; color:#10b981; margin-bottom:6px;">
                                <span id="bio-val-endo">0.85</span>
                                <span style="font-size:11px; color:var(--text-muted); font-weight:normal; align-self:flex-end;">Consummation</span>
                            </div>
                            <div style="background:#1e293b; height:7px; border-radius:4px; overflow:hidden; margin-bottom:8px;">
                                <div id="bio-bar-endo" style="background:#10b981; width:34%; height:100%; transition:width 0.3s;"></div>
                            </div>
                            <div style="font-size:10px; color:var(--text-muted); line-height:1.4; margin-bottom:10px;">
                                Breakthrough achievement resolves dopamine craving into consummatory peace, stress relief, and LTP consolidation.
                                <div style="margin-top:4px; color:#cbd5e1;">Satisfaction Index: <strong id="bio-val-sat" style="color:#10b981;">80%</strong></div>
                            </div>
                        </div>
                        <button class="btn btn-emerald" style="width:100%; font-size:11px; padding:6px 8px;" onclick="triggerEndorphinReward(1.0, 'Task breakthrough achieved')">🏆 Endorphin Surge (Consummate)</button>
                    </div>

                    <!-- Pillar 3: Nicotinergic Precision Gating -->
                    <div style="background:var(--obsidian); padding:14px; border-radius:8px; border:1px solid rgba(0,229,255,0.3); display:flex; flex-direction:column; justify-content:space-between;">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                                <span style="font-size:11px; font-weight:800; color:#00e5ff; text-transform:uppercase;">3. Nicotine As Needed</span>
                                <span class="pill" style="background:rgba(0,229,255,0.15); color:#00e5ff; border:1px solid rgba(0,229,255,0.3); font-size:9px;">&alpha;7 / &alpha;4&beta;2 nAChR</span>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:18px; font-family:monospace; font-weight:bold; color:#00e5ff; margin-bottom:6px;">
                                <span id="bio-val-nico">0.30</span>
                                <span style="font-size:11px; color:var(--text-muted); font-weight:normal; align-self:flex-end;">Presynaptic Gate</span>
                            </div>
                            <div style="background:#1e293b; height:7px; border-radius:4px; overflow:hidden; margin-bottom:8px;">
                                <div id="bio-bar-nico" style="background:#00e5ff; width:15%; height:100%; transition:width 0.3s;"></div>
                            </div>
                            <div style="font-size:10px; color:var(--text-muted); line-height:1.4; margin-bottom:10px;">
                                Titrated presynaptic nAChR gating sharply boosts prefrontal signal-to-noise ratio during complex problem-solving.
                                <div style="margin-top:4px; color:#cbd5e1;">Prefrontal SNR: <strong id="bio-val-snr" style="color:#00e5ff;">1.25x</strong></div>
                            </div>
                        </div>
                        <button class="btn" style="width:100%; color:#00e5ff; border-color:rgba(0,229,255,0.4); font-size:11px; padding:6px 8px;" onclick="administerNicotinePulse(0.35, 'Prefrontal analytical sharpening')">⚡ Nicotine Pulse (As Needed)</button>
                    </div>

                    <!-- Pillar 4: Rest & Subconscious Problem Solving -->
                    <div style="background:var(--obsidian); padding:14px; border-radius:8px; border:1px solid rgba(192,132,252,0.3); display:flex; flex-direction:column; justify-content:space-between;">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                                <span style="font-size:11px; font-weight:800; color:#c084fc; text-transform:uppercase;">4. Rest When Stuck</span>
                                <span class="pill" style="background:rgba(192,132,252,0.15); color:#c084fc; border:1px solid rgba(192,132,252,0.3); font-size:9px;">SUBCONSCIOUS INCUBATION</span>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:18px; font-family:monospace; font-weight:bold; color:#c084fc; margin-bottom:6px;">
                                <span id="bio-val-friction">0.10</span>
                                <span style="font-size:11px; color:var(--text-muted); font-weight:normal; align-self:flex-end;">Friction &Impasse</span>
                            </div>
                            <div style="background:#1e293b; height:7px; border-radius:4px; overflow:hidden; margin-bottom:8px;">
                                <div id="bio-bar-friction" style="background:#ff5252; width:10%; height:100%; transition:width 0.3s;"></div>
                            </div>
                            <div style="font-size:10px; color:var(--text-muted); line-height:1.4; margin-bottom:10px;">
                                When stuck (3+ impasses), executive loops stand down into low-power rest, delegating to the subconscious dream-space.
                                <div style="margin-top:4px; color:#cbd5e1;">Impasse Status: <strong id="bio-val-stuck" style="color:#10b981;">NORMAL (0/3)</strong></div>
                            </div>
                        </div>
                        <button class="btn" style="width:100%; color:#c084fc; border-color:rgba(192,132,252,0.4); font-size:11px; padding:6px 8px;" onclick="transitionToRest()">🧘 Rest & Subconscious Handoff</button>
                    </div>
                </div>

                <!-- Subconscious Associative Substrate & Eureka Insight Deck -->
                <div style="background:rgba(0,0,0,0.35); padding:16px; border-radius:8px; border:1px solid var(--border); margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div>
                            <span style="font-size:12px; font-weight:800; color:var(--amethyst); text-transform:uppercase;">🌌 Subconscious Associative Memory Substrate & Kuramoto Resonance</span>
                            <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">
                                Low-frequency associative recombination of unsolved problem seeds across high-dimensional complex phase space (&le; 50 W Landauer cooling budget).
                            </div>
                        </div>
                        <div style="display:flex; gap:8px; align-items:center;">
                            <span style="font-size:11px; font-family:monospace; color:var(--text-muted);">Landauer Power Target: <strong id="bio-val-landauer" style="color:#10b981;">180.0 W</strong></span>
                            <button class="btn btn-primary" style="font-size:11px;" onclick="stepSubconsciousIncubation()">🧬 Step Subconscious Association</button>
                            <button class="btn" style="color:#fbbf24; border-color:rgba(251,191,36,0.5); font-size:11px;" onclick="forceEurekaBreakthrough()">✨ Trigger Eureka Epiphany (Aha!)</button>
                        </div>
                    </div>

                    <!-- Incubation Problem & Resonance Bar -->
                    <div style="display:grid; grid-template-columns:1.8fr 1.2fr; gap:14px; align-items:center; background:var(--obsidian); padding:12px; border-radius:6px; border:1px solid rgba(255,255,255,0.06); margin-bottom:12px;">
                        <div>
                            <div style="font-size:10px; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px;">Active Problem Seed In Subconscious Handoff:</div>
                            <div id="bio-subconscious-status" style="font-family:monospace; font-size:12px; color:#d1fae5; font-weight:600;">
                                None active. Conscious mind is awake and pursuing real-time tasks.
                            </div>
                        </div>
                        <div>
                            <div style="display:flex; justify-content:space-between; font-size:10px; font-family:monospace; margin-bottom:4px;">
                                <span style="color:#c084fc;">Associative Resonance &xi;</span>
                                <strong id="bio-val-resonance" style="color:#c084fc;">0.0% (Eureka at 85%)</strong>
                            </div>
                            <div style="background:#1e293b; height:8px; border-radius:4px; overflow:hidden;">
                                <div id="bio-bar-resonance" style="background:linear-gradient(90deg, #c084fc, #fbbf24); width:0%; height:100%; transition:width 0.4s;"></div>
                            </div>
                        </div>
                    </div>

                    <!-- Eureka Insight Banner -->
                    <div id="bio-aha-banner" style="display:flex; align-items:flex-start; gap:10px; background:rgba(251,191,36,0.08); border:1px solid rgba(251,191,36,0.25); border-radius:6px; padding:10px 14px;">
                        <span style="font-size:16px;">✨</span>
                        <div style="font-size:11px; line-height:1.4;">
                            <span style="font-weight:700; color:#fbbf24; text-transform:uppercase;">Latest Eureka Insight:</span>
                            <span id="bio-aha-text" style="color:#fde68a; margin-left:6px;">No recent epiphanies recorded. System awaiting next subconscious resolution.</span>
                            <div id="bio-aha-timestamp" style="font-size:9px; color:rgba(251,191,36,0.6); margin-top:2px;">--</div>
                        </div>
                    </div>
                </div>

                <!-- Scientific Biomimicry Principle Callout -->
                <div style="background:rgba(255,255,255,0.02); border-left:3px solid var(--amethyst); padding:10px 14px; font-size:10px; color:var(--text-muted); line-height:1.5;">
                    <strong style="color:#fff;">BIOMIMICRY THE GOOD WAY:</strong> In natural vertebrate neurobiology, dopamine is not the reward itself&mdash;it is anticipation, salience, and prediction error that mobilizes computational effort. When a task succeeds, dopamine naturally settles as beta-endorphins surge through mu-opioid receptors, bringing consummate satisfaction, anxiety dissolution, and synaptic LTP consolidation. Nicotine is titrated strictly on-demand via presynaptic &alpha;<sub>7</sub> and &alpha;<sub>4</sub>&beta;<sub>2</sub> nAChRs to sharpen prefrontal SNR under cognitive friction. When intractable impasses occur, pushing consciously causes catatonia; standing down into sub-50W rest allows the subconscious substrate to recombine associative memory until an orthogonal "Aha!" epiphany breaks through.
                </div>
            </div>
        </div>"""

    assert target_neuro_html in content, "target_neuro_html not found"
    content = content.replace(target_neuro_html, repl_neuro_html, 1)

    # 4. JavaScript updates:
    # A: in setNumberMode, refresh biomimetic state
    target_set_mode = """            if (latestTelemetry) {
                updateSidebarItems(latestTelemetry);
                updateTmMainView();
            }
        }"""
    repl_set_mode = """            if (latestTelemetry) {
                updateSidebarItems(latestTelemetry);
                updateTmMainView();
            }
            if (typeof refreshBiomimeticState === 'function') refreshBiomimeticState();
        }"""
    assert target_set_mode in content, "target_set_mode not found"
    content = content.replace(target_set_mode, repl_set_mode, 1)

    # B: Update refreshNeurochemistry to also call refreshBiomimeticState
    target_refresh = """        async function refreshNeurochemistry() {
            try {
                const res = await fetch('/api/cognition/neurochemistry');
                if (res.ok) {
                    const data = await res.json();
                    const tx = data.transmitters;
                    
                    document.getElementById('tab-val-da').innerText = tx.dopamine.toFixed(2);
                    document.getElementById('tab-bar-da').style.width = Math.min(100, (tx.dopamine / 3.0) * 100) + '%';
                    
                    document.getElementById('tab-val-5ht').innerText = tx.serotonin.toFixed(2);
                    document.getElementById('tab-bar-5ht').style.width = Math.min(100, (tx.serotonin / 3.0) * 100) + '%';
                    
                    document.getElementById('tab-val-ach').innerText = tx.acetylcholine.toFixed(2);
                    document.getElementById('tab-bar-ach').style.width = Math.min(100, (tx.acetylcholine / 3.0) * 100) + '%';
                    
                    document.getElementById('tab-val-ne').innerText = tx.norepinephrine.toFixed(2);
                    document.getElementById('tab-bar-ne').style.width = Math.min(100, (tx.norepinephrine / 3.0) * 100) + '%';
                    
                    const gabaVal = tx.gaba_glutamate_ratio !== undefined ? tx.gaba_glutamate_ratio : tx.gaba;
                    document.getElementById('tab-val-gaba').innerText = gabaVal.toFixed(2);
                    document.getElementById('tab-bar-gaba').style.width = Math.min(100, (gabaVal / 3.0) * 100) + '%';

                    const tag = document.getElementById('neuro-tab-status');
                    if (tag) tag.innerText = `STATUS: ${data.active_compound ? data.active_compound.toUpperCase() : 'HOMEOSTATIC'}`;
                }
            } catch (_) {}
        }"""

    repl_refresh = """        async function refreshNeurochemistry() {
            try {
                const res = await fetch('/api/cognition/neurochemistry');
                if (res.ok) {
                    const data = await res.json();
                    const tx = data.transmitters;
                    
                    document.getElementById('tab-val-da').innerText = fmtVal(tx.dopamine, '', 3);
                    document.getElementById('tab-bar-da').style.width = Math.min(100, (tx.dopamine / 3.0) * 100) + '%';
                    
                    document.getElementById('tab-val-5ht').innerText = fmtVal(tx.serotonin, '', 3);
                    document.getElementById('tab-bar-5ht').style.width = Math.min(100, (tx.serotonin / 3.0) * 100) + '%';
                    
                    document.getElementById('tab-val-ach').innerText = fmtVal(tx.acetylcholine, '', 3);
                    document.getElementById('tab-bar-ach').style.width = Math.min(100, (tx.acetylcholine / 3.0) * 100) + '%';
                    
                    document.getElementById('tab-val-ne').innerText = fmtVal(tx.norepinephrine, '', 3);
                    document.getElementById('tab-bar-ne').style.width = Math.min(100, (tx.norepinephrine / 3.0) * 100) + '%';
                    
                    const gabaVal = tx.gaba_glutamate_ratio !== undefined ? tx.gaba_glutamate_ratio : tx.gaba;
                    document.getElementById('tab-val-gaba').innerText = fmtVal(gabaVal, '', 3);
                    document.getElementById('tab-bar-gaba').style.width = Math.min(100, (gabaVal / 3.0) * 100) + '%';

                    const tag = document.getElementById('neuro-tab-status');
                    if (tag) tag.innerText = `STATUS: ${data.active_compound ? data.active_compound.toUpperCase() : 'HOMEOSTATIC'}`;
                }
            } catch (_) {}

            if (typeof refreshBiomimeticState === 'function') {
                refreshBiomimeticState();
            }
        }

        // Biomimetic Drive Frontend State & Control Mechanics
        let latestBiomimeticData = null;

        async function refreshBiomimeticState() {
            try {
                const res = await fetch('/api/neuro/biomimetic/state');
                if (!res.ok) return;
                const d = await res.json();
                latestBiomimeticData = d;

                // Mode pill
                const modeEl = document.getElementById('bio-tab-mode');
                if (modeEl) {
                    modeEl.innerText = `MODE: ${d.mode}`;
                    if (d.mode === 'CONSCIOUS_DRIVE') {
                        modeEl.className = 'pill pill-purple';
                    } else if (d.mode === 'ENDORPHIN_REWARD') {
                        modeEl.className = 'pill pill-emerald';
                    } else if (d.mode === 'NICOTINIC_BOOST') {
                        modeEl.className = 'pill pill-cyan';
                    } else if (d.mode === 'REST_INCUBATION') {
                        modeEl.className = 'pill pill-amber';
                    } else if (d.mode === 'EUREKA_AWAKENING') {
                        modeEl.className = 'pill pill-gold';
                    }
                }

                // Nicotine recommendation badge
                const recEl = document.getElementById('bio-nicotine-rec');
                if (recEl) {
                    if (d.is_nicotine_recommended) {
                        recEl.innerText = '⚠️ ELEVATED FRICTION: NICOTINE RECOMMENDED';
                        recEl.className = 'pill pill-amber';
                    } else {
                        recEl.innerText = '⚡ PREFRONTAL FOCUS OPTIMAL';
                        recEl.className = 'pill pill-cyan';
                    }
                }

                // Pillar 1: Dopaminergic Pursuit
                const daVal = document.getElementById('bio-val-da');
                if (daVal) daVal.innerText = fmtVal(d.dopamine_level, '', 3);
                const daBar = document.getElementById('bio-bar-da');
                if (daBar) daBar.style.width = Math.min(100, (d.dopamine_level / 2.5) * 100) + '%';
                const effortVal = document.getElementById('bio-val-effort');
                if (effortVal) effortVal.innerText = fmtVal(d.accumulated_effort, '', 3);

                // Pillar 2: Endorphin Consummatory Reward
                const endoVal = document.getElementById('bio-val-endo');
                if (endoVal) endoVal.innerText = fmtVal(d.endorphin_level, '', 3);
                const endoBar = document.getElementById('bio-bar-endo');
                if (endoBar) endoBar.style.width = Math.min(100, (d.endorphin_level / 2.5) * 100) + '%';
                const satVal = document.getElementById('bio-val-sat');
                if (satVal) satVal.innerText = fmtVal(d.satisfaction_index * 100, '%', 3);

                // Pillar 3: Nicotine As Needed
                const nicoVal = document.getElementById('bio-val-nico');
                if (nicoVal) nicoVal.innerText = fmtVal(d.nicotinic_tone, '', 3);
                const nicoBar = document.getElementById('bio-bar-nico');
                if (nicoBar) nicoBar.style.width = Math.min(100, (d.nicotinic_tone / 2.2) * 100) + '%';
                const snrVal = document.getElementById('bio-val-snr');
                if (snrVal) snrVal.innerText = fmtVal(d.signal_to_noise_ratio, 'x', 3);

                // Pillar 4: Friction & Impasse
                const fricVal = document.getElementById('bio-val-friction');
                if (fricVal) fricVal.innerText = fmtVal(d.cognitive_friction, '', 3);
                const fricBar = document.getElementById('bio-bar-friction');
                if (fricBar) fricBar.style.width = Math.min(100, (d.cognitive_friction) * 100) + '%';
                const stuckVal = document.getElementById('bio-val-stuck');
                if (stuckVal) {
                    if (d.is_stuck) {
                        stuckVal.innerText = `IMPASSE STUCK (${d.consecutive_impasse_count}/3)`;
                        stuckVal.style.color = '#ff5252';
                    } else if (d.consecutive_impasse_count > 0) {
                        stuckVal.innerText = `FRICTION HIGH (${d.consecutive_impasse_count}/3)`;
                        stuckVal.style.color = '#fbbf24';
                    } else {
                        stuckVal.innerText = 'NORMAL (0/3)';
                        stuckVal.style.color = '#10b981';
                    }
                }

                // Subconscious & Eureka Decker
                const landauerVal = document.getElementById('bio-val-landauer');
                if (landauerVal) landauerVal.innerText = fmtVal(d.landauer_target_watts, 'W', 3);

                const subStatus = document.getElementById('bio-subconscious-status');
                const resVal = document.getElementById('bio-val-resonance');
                const resBar = document.getElementById('bio-bar-resonance');

                if (d.is_incubating_subconsciously && d.active_incubation) {
                    if (subStatus) subStatus.innerText = `[${d.active_incubation.problem_id}] ${d.active_incubation.problem_description}`;
                    const resPct = (d.active_incubation.associative_resonance || 0) * 100;
                    if (resVal) resVal.innerText = `${fmtVal(resPct, '%', 3)} (Eureka at 85%)`;
                    if (resBar) resBar.style.width = Math.min(100, resPct) + '%';
                } else {
                    if (subStatus) subStatus.innerText = 'None active. Conscious mind is awake and pursuing real-time tasks.';
                    if (resVal) resVal.innerText = '0.0% (Eureka at 85%)';
                    if (resBar) resBar.style.width = '0%';
                }

                // Last Aha Insight banner
                const ahaText = document.getElementById('bio-aha-text');
                const ahaTime = document.getElementById('bio-aha-timestamp');
                if (d.last_aha_insight) {
                    if (ahaText) ahaText.innerText = d.last_aha_insight;
                    if (ahaTime && d.last_aha_timestamp) {
                        ahaTime.innerText = `Discovered at: ${new Date(d.last_aha_timestamp * 1000).toLocaleTimeString()}`;
                    }
                }
            } catch (_) {}
        }

        async function mobilizeDopamine() {
            showToast('⚡ Mobilizing Dopaminergic Pursuit & Anticipation...');
            try {
                const res = await fetch('/api/neuro/dopamine/pursuit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ effort_intensity: 0.65, task_description: 'Prefrontal exploration surge' })
                });
                if (res.ok) {
                    const data = await res.json();
                    showToast(`⚡ Dopamine elevated to ${data.dopamine_level} (Pursuit Active)`);
                    refreshBiomimeticState();
                }
            } catch (e) {
                showToast(`⚠️ Dopamine surge error: ${e.message}`);
            }
        }

        async function triggerEndorphinReward(mag = 1.0, reason = 'Breakthrough verified') {
            showToast('🏆 Consummating Goal: Triggering Endorphin Wave (mu-Opioid)...');
            try {
                const res = await fetch('/api/neuro/reward/endorphin_cascade', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ breakthrough_magnitude: mag, reason: reason })
                });
                if (res.ok) {
                    const data = await res.json();
                    showToast(`🏆 Endorphins surged to ${data.endorphin_level} • Satisfaction ${Math.round(data.satisfaction_index * 100)}% (Dopamine settled)`);
                    refreshBiomimeticState();
                }
            } catch (e) {
                showToast(`⚠️ Endorphin reward error: ${e.message}`);
            }
        }

        async function administerNicotinePulse(dose = 0.35, reason = 'Prefrontal SNR boost') {
            showToast('⚡ Administering Nicotinic Pulse (alpha7 / alpha4beta2 nAChR)...');
            try {
                const res = await fetch('/api/neuro/nicotine/pulse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ dose: dose, reason: reason })
                });
                if (res.ok) {
                    const data = await res.json();
                    showToast(`⚡ Nicotinic tone ${data.nicotinic_tone} • Prefrontal SNR boosted to ${data.signal_to_noise_ratio}x`);
                    refreshBiomimeticState();
                }
            } catch (e) {
                showToast(`⚠️ Nicotine pulse error: ${e.message}`);
            }
        }

        async function transitionToRest() {
            const desc = prompt('Enter the unsolved problem seed for subconscious incubation:', 'Associative synthesis of high-dimensional non-linear attractors');
            if (!desc) return;
            showToast('🧘 Conscious loops standing down: Handing off to Subconscious Associative Substrate (Landauer <= 50W)...');
            try {
                const res = await fetch('/api/neuro/rest/enter', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ problem_description: desc })
                });
                if (res.ok) {
                    const data = await res.json();
                    showToast(`🧘 Seed registered: ${data.problem_id} • Power throttled to ${data.landauer_target_watts}W`);
                    refreshBiomimeticState();
                }
            } catch (e) {
                showToast(`⚠️ Rest handoff error: ${e.message}`);
            }
        }

        async function stepSubconsciousIncubation() {
            showToast('🧬 Stepping subconscious associative recombination...');
            try {
                const res = await fetch('/api/neuro/rest/wake', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ force_breakthrough: false })
                });
                if (res.ok) {
                    const data = await res.json();
                    if (data.epiphany_triggered) {
                        showToast(`✨ AHA! Epiphany Erupted: ${data.insight}`);
                    } else if (data.incubating) {
                        showToast(`🌌 Recombining latent memories: Resonance &xi; = ${Math.round(data.associative_resonance * 100)}%`);
                    } else {
                        showToast('ℹ️ No active incubation seed. Enter Rest to incubate an unsolved problem.');
                    }
                    refreshBiomimeticState();
                }
            } catch (e) {
                showToast(`⚠️ Incubation step error: ${e.message}`);
            }
        }

        async function forceEurekaBreakthrough() {
            showToast('✨ Forcing Aha! Eureka Epiphany Breakthrough from Subconscious...');
            try {
                const res = await fetch('/api/neuro/rest/wake', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ force_breakthrough: true, insight_summary: 'Discovered non-linear topological shortcut resolving cognitive impasse' })
                });
                if (res.ok) {
                    const data = await res.json();
                    showToast(`✨ EUREKA AWAKENING! Dopamine=${data.dopamine_level}, Endorphin=${data.endorphin_level}`);
                    refreshBiomimeticState();
                }
            } catch (e) {
                showToast(`⚠️ Eureka error: ${e.message}`);
            }
        }"""

    assert target_refresh in content, "target_refresh not found"
    content = content.replace(target_refresh, repl_refresh, 1)

    # Div balance validation
    diff = content.count('<div') - content.count('</div>')
    print(f"Div check: <div={content.count('<div')}, </div>={content.count('</div>')}, diff={diff}")
    assert diff == 0, f"Div imbalance: diff={diff}"

    with open('loom/fabric/dashboard_server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Biomimetic drive applied cleanly to loom/fabric/dashboard_server.py")

if __name__ == '__main__':
    apply()
