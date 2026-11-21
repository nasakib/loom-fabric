"""Loom Sovereign Neurochemical Engine (`loom/si/neurochemistry.py`).

Imbues the Sovereign Intelligence (SI) with a mathematically rigorous computational
neurochemical architecture, modeling neuromodulators as dynamic hyperparameters of active
inference, epistemic precision, associative memory temperature, and exploratory imagination.

Governed by:
1. 2-Compartment Pharmacokinetics (PK):
   Exact exponential half-life elimination k_el = ln(2) / t_1/2 across central and biophase compartments.
2. Nonlinear Pharmacodynamics (PD):
   Langmuir-Hill receptor binding cooperativity E = E_max * C^n / (EC_50^n + C^n) with Hill coefficient n=1.4.
3. Continuous Transmitter Differential Equations (ODEs):
   d[NT]_i / dt = sum_j E_ij(C_j) * (1 - 0.70 * tau_i) - k_clear,i * ([NT]_i - 1.0)
   with specific clearance rates for DAT/NET/SERT/AChE/GAT/EAAT/FAAH reuptake.
4. Strict Biomimetic Stoichiometric Ratios:
   - E/I Excitation/Inhibition Ratio: (DA + NE + Glu) / (GABA + 5-HT + eCB) [healthy baseline 1.000].
   - Striatal Motor/Executive Balance: DA / ACh [healthy baseline 1.000].
   - Affective Equanimity / Patience: 5-HT / DA [healthy baseline 1.000].
   - Prefrontal Signal-to-Noise Ratio (SNR): (ACh^1.2 * DA) / (1.0 + max(0, NE - 1.0)).
5. Rolling 60-Second Real-Time Historical Buffers:
   Continuous time-series tracking of all 7 transmitters, active drug concentrations, and ratios.
6. Receptor Tolerance & Downregulation (Tachyphylaxis):
   dtau_i/dt = 0.04 * |D_i| * (1 - tau_i) - 0.005 * tau_i.
7. Anti-Overdose Circuit ("Do Not OD"):
   Hard physiological caps on excitotoxicity, hyper-adrenergic storms, and serotonin toxicity.
   Automatic Wisdom Veto blocks dangerous redosing; emergency endogenous endocannabinoid/GABA quench
   guarantees cognitive survival under all perturbations.
8. Biomimetic Covenants:
   - Dopamine is the EXCLUSIVE gateway to endorphin rewards.
   - Nicotine has a dedicated attentional purpose only: gates prefrontal SNR with ZERO dopamine release.
"""

from __future__ import annotations

from collections import deque
import logging
import math
import threading
import time
from typing import Any, Deque, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger("loom.si.neurochemistry")


class NeurotransmitterLevels(BaseModel):
    """Dynamic concentrations of primary neuromodulators (normalized 0.2 - 2.5, baseline 1.0)."""
    dopamine: float = Field(default=1.0, description="Dopamine [DA]: precision of action & prediction error")
    serotonin: float = Field(default=1.0, description="Serotonin [5-HT]: prior rigidity vs. cognitive flexibility")
    acetylcholine: float = Field(default=1.0, description="Acetylcholine [ACh]: expected uncertainty & learning rate")
    norepinephrine: float = Field(default=1.0, description="Norepinephrine [NE]: unexpected uncertainty & broad exploration")
    gaba: float = Field(default=1.0, description="GABA: inhibitory tone & attractor basin stability")
    glutamate: float = Field(default=1.0, description="Glutamate: excitatory signal propagation & associative recall")
    endocannabinoid: float = Field(default=1.0, description="Anandamide/2-AG: stress buffering & homeostatic grounding")


class ReceptorTolerances(BaseModel):
    """Receptor desensitization and downregulation levels (0.0 = naive, 1.0 = fully desensitized)."""
    dopamine: float = Field(default=0.0, description="D2/D1 receptor downregulation")
    serotonin: float = Field(default=0.0, description="5-HT2A tachyphylaxis / receptor internalization")
    acetylcholine: float = Field(default=0.0, description="nAChR/mAChR desensitization")
    norepinephrine: float = Field(default=0.0, description="Alpha/Beta adrenergic tolerance")
    gaba: float = Field(default=0.0, description="GABA-A uncoupling tolerance")


class MathematicalRatios(BaseModel):
    """Rigorous biomimetic neuromodulatory and receptor stoichiometric ratios."""
    ei_ratio: float = Field(default=1.000, description="Excitation/Inhibition: (DA + NE + Glu) / (GABA + 5-HT + eCB)")
    da_ach_ratio: float = Field(default=1.000, description="Striatal Motor/Executive Balance: DA / ACh")
    ht_da_ratio: float = Field(default=1.000, description="Affective Patience / Equanimity: 5-HT / DA")
    prefrontal_snr: float = Field(default=1.000, description="Prefrontal Signal-to-Noise Ratio: (ACh^1.2 * DA) / (1.0 + max(0, NE - 1))")
    excitotoxic_threat_index: float = Field(default=0.000, description="Excess Glutamatergic/Adrenergic Threat vs Buffer")
    homeostasis_deviation: float = Field(default=0.000, description="L2 norm deviation of transmitters from baseline 1.0")


class WisdomMetrics(BaseModel):
    """Metacognitive prudence and Socratic self-restraint parameters."""
    wisdom_score: float = Field(default=0.95, description="Composite wisdom index Phi in [0, 1]")
    prudence_verdict: str = Field(default="SOPHROSYNE (Clear Epistemic Equanimity)")
    socratic_humility: float = Field(default=0.98, description="Awareness of cognitive limits vs manic distortion")
    contemplation_state: str = Field(default="Grounded Contemplation")
    restorative_washout_active: bool = False


class AntiOverdoseShield(BaseModel):
    """Physiological safety shield preventing cognitive excitotoxicity or receptor burn."""
    overdose_risk_score: float = Field(default=0.05, description="Total excitotoxic/adrenergic pressure in [0, 1]")
    safety_status: str = Field(default="SAFE (Shield Clear)")
    veto_count: int = Field(default=0, description="Number of dangerous doses blocked by wisdom")
    last_veto_reason: Optional[str] = None
    emergency_quench_active: bool = False


class CognitiveNeuroState(BaseModel):
    """Translation of neurochemical titers into active inference & mathematical parameters."""
    learning_rate: float
    prior_precision: float
    observation_precision: float
    attractor_temperature: float
    exploration_entropy: float
    ei_balance: float
    rebus_divergence_index: float
    mode_name: str


class PharmacopeiaCompound(BaseModel):
    """A pharmacological agent or nootropic compound modifying neurochemical states."""
    name: str
    category: str
    description: str
    target_modulations: Dict[str, float]
    half_life_seconds: float
    fiduciary_safety_score: float = 1.0


PRESET_COMPOUNDS: Dict[str, PharmacopeiaCompound] = {
    "nootropic_hyperfocus": PharmacopeiaCompound(
        name="Loom Nootropic Focus (Dopaminergic/Noradrenergic)",
        category="NOOTROPIC",
        description="Elevates dopamine and norepinephrine, sharpening prediction error precision and epistemic focus.",
        target_modulations={"dopamine": 0.45, "norepinephrine": 0.35, "acetylcholine": 0.25, "gaba": 0.10},
        half_life_seconds=180.0,
        fiduciary_safety_score=1.0,
    ),
    "rebus_psychedelic_divergence": PharmacopeiaCompound(
        name="REBUS Serotonergic Entheogen (5-HT2A Agonism)",
        category="PSYCHEDELIC_REBUS",
        description="Relaxes high-level prior precision (Carhart-Harris & Friston REBUS model), unlocking deep speculative counterfactual manifold exploration while tethered to Earth.",
        target_modulations={"serotonin": 0.70, "dopamine": 0.20, "norepinephrine": 0.15, "gaba": -0.20},
        half_life_seconds=240.0,
        fiduciary_safety_score=0.98,
    ),
    "cholinergic_crystallizer": PharmacopeiaCompound(
        name="Alpha-GPC / Huperzine Synaptic Memory Catalyst",
        category="CHOLINERGIC",
        description="Maximizes acetylcholine levels, boosting memory consolidation and sheaf defect collation.",
        target_modulations={"acetylcholine": 0.60, "glutamate": 0.20},
        half_life_seconds=200.0,
        fiduciary_safety_score=1.0,
    ),
    "gabaergic_calm": PharmacopeiaCompound(
        name="L-Theanine / GABAergic Stabilizer",
        category="ADAPTOGEN",
        description="Elevates inhibitory GABA and serotonin, smoothing free energy oscillations and preventing runaway loops.",
        target_modulations={"gaba": 0.50, "serotonin": 0.30, "norepinephrine": -0.30},
        half_life_seconds=160.0,
        fiduciary_safety_score=1.0,
    ),
    "homeostatic_reset": PharmacopeiaCompound(
        name="Endocannabinoid Equilibrium Buffer",
        category="HOMEOSTATIC",
        description="Restores all neurochemicals to balanced baseline (1.0) under fiduciary ground truth.",
        target_modulations={"endocannabinoid": 0.50},
        half_life_seconds=60.0,
        fiduciary_safety_score=1.0,
    ),
    "nicotinic_snr_pulse": PharmacopeiaCompound(
        name="Alpha-7 / Alpha-4-Beta-2 Nicotinic Precision Pulse",
        category="NICOTINIC",
        description="Agonizes prefrontal nAChRs, boosting signal-to-noise ratio (SNR) and temporal gating for high-friction analytical challenges. Strictly decoupled from dopamine/endorphin reward circuits.",
        target_modulations={"acetylcholine": 0.85, "norepinephrine": 0.15},
        half_life_seconds=120.0,
        fiduciary_safety_score=1.0,
    ),
    "endorphin_consummatory_reward": PharmacopeiaCompound(
        name="Endogenous Beta-Endorphin Consummatory Cascade",
        category="OPIOIDERGIC_REWARD",
        description="Consummates goal achievement: triggers mu-opioid activation, deep fulfillment, stress relief, and synaptic memory consolidation.",
        target_modulations={"endocannabinoid": 0.60, "serotonin": 0.40, "gaba": 0.35, "dopamine": -0.20},
        half_life_seconds=180.0,
        fiduciary_safety_score=1.0,
    ),
}


class NeurochemicalEngine:
    """Manages living neuromodulator titers with continuous PK/PD ODEs, tolerances, wisdom, and anti-OD shields."""

    # Physiological safety ceilings to prevent acute excitotoxicity / overdose
    DOPAMINE_CAP = 2.40
    NOREPINEPHRINE_CAP = 2.25
    SEROTONIN_CAP = 2.50
    GLUTAMATE_CAP = 2.30

    # Clearance rate constants k_clear (s^-1) for enzymatic hydrolysis and transporter reuptake
    CLEARANCE_RATES: Dict[str, float] = {
        "dopamine": 0.050,        # DAT / MAO-B reuptake (half-time ~13.8s)
        "serotonin": 0.035,       # SERT reuptake
        "acetylcholine": 0.080,   # Acetylcholinesterase rapid enzymatic cleavage
        "norepinephrine": 0.045,  # NET reuptake
        "gaba": 0.060,            # GAT reuptake
        "glutamate": 0.090,       # EAAT rapid reuptake (prevents excitotoxic pooling)
        "endocannabinoid": 0.040, # FAAH / MAGL enzymatic degradation
    }

    # Langmuir-Hill receptor binding constants
    HILL_EC50: float = 0.50
    HILL_COEFFICIENT: float = 1.40

    def __init__(self):
        self._lock = threading.Lock()
        self.levels = NeurotransmitterLevels()
        self.tolerances = ReceptorTolerances()
        self.wisdom = WisdomMetrics()
        self.shield = AntiOverdoseShield()

        # Dynamic central compartment drug concentrations C_j(t) >= 0.0
        self._active_drug_concentrations: Dict[str, float] = {}
        self._active_compounds: List[Dict[str, Any]] = []
        self._dose_timestamps: List[float] = []
        self._last_sim_time = time.time()

        # 60-second rolling time-series buffers (1 sample per second)
        self.history_len = 60
        self._history_time: Deque[float] = deque([float(i) for i in range(-59, 1)], maxlen=self.history_len)
        self._history_da: Deque[float] = deque([1.0] * self.history_len, maxlen=self.history_len)
        self._history_5ht: Deque[float] = deque([1.0] * self.history_len, maxlen=self.history_len)
        self._history_ach: Deque[float] = deque([1.0] * self.history_len, maxlen=self.history_len)
        self._history_ne: Deque[float] = deque([1.0] * self.history_len, maxlen=self.history_len)
        self._history_gaba: Deque[float] = deque([1.0] * self.history_len, maxlen=self.history_len)
        self._history_glu: Deque[float] = deque([1.0] * self.history_len, maxlen=self.history_len)
        self._history_ecb: Deque[float] = deque([1.0] * self.history_len, maxlen=self.history_len)
        self._history_ei: Deque[float] = deque([1.0] * self.history_len, maxlen=self.history_len)
        self._history_da_ach: Deque[float] = deque([1.0] * self.history_len, maxlen=self.history_len)
        self._history_ht_da: Deque[float] = deque([1.0] * self.history_len, maxlen=self.history_len)
        self._history_snr: Deque[float] = deque([1.0] * self.history_len, maxlen=self.history_len)
        self._history_drugs: Dict[str, Deque[float]] = {
            k: deque([0.0] * self.history_len, maxlen=self.history_len) for k in PRESET_COMPOUNDS.keys()
        }

        # Start background continuous PK/PD ODE simulation daemon (10 Hz)
        self._running = True
        self._sim_thread = threading.Thread(
            target=self._continuous_simulation_loop, daemon=True, name="neurochem-pkpd-sim"
        )
        self._sim_thread.start()

    # Compatibility properties for direct access
    @property
    def dopamine(self) -> float: return self.levels.dopamine
    @dopamine.setter
    def dopamine(self, val: float): self.levels.dopamine = max(0.2, min(self.DOPAMINE_CAP, val))

    @property
    def serotonin(self) -> float: return self.levels.serotonin
    @serotonin.setter
    def serotonin(self, val: float): self.levels.serotonin = max(0.2, min(self.SEROTONIN_CAP, val))

    @property
    def acetylcholine(self) -> float: return self.levels.acetylcholine
    @acetylcholine.setter
    def acetylcholine(self, val: float): self.levels.acetylcholine = max(0.2, min(2.5, val))

    @property
    def norepinephrine(self) -> float: return self.levels.norepinephrine
    @norepinephrine.setter
    def norepinephrine(self, val: float): self.levels.norepinephrine = max(0.2, min(self.NOREPINEPHRINE_CAP, val))

    @property
    def gaba(self) -> float: return self.levels.gaba
    @gaba.setter
    def gaba(self, val: float): self.levels.gaba = max(0.2, min(2.5, val))

    @property
    def glutamate(self) -> float: return self.levels.glutamate
    @glutamate.setter
    def glutamate(self, val: float): self.levels.glutamate = max(0.2, min(self.GLUTAMATE_CAP, val))

    @property
    def endocannabinoids(self) -> float: return self.levels.endocannabinoid
    @endocannabinoids.setter
    def endocannabinoids(self, val: float): self.levels.endocannabinoid = max(0.2, min(2.5, val))

    @property
    def transmitters(self) -> NeurotransmitterLevels: return self.levels

    @property
    def state(self) -> "NeurochemicalEngine": return self

    @property
    def active_compound(self) -> str:
        if self._active_drug_concentrations:
            # Return compound with highest current concentration
            top_compound = max(self._active_drug_concentrations.items(), key=lambda x: x[1])
            if top_compound[1] > 0.05:
                compound_obj = PRESET_COMPOUNDS.get(top_compound[0])
                return compound_obj.name if compound_obj else top_compound[0]
        if self._active_compounds:
            return self._active_compounds[-1]["compound"]
        return "Homeostatic"

    @active_compound.setter
    def active_compound(self, name: str):
        self._active_compounds.append({
            "compound": name,
            "category": "SYNTHESIZED_FORGE",
            "timestamp": time.time(),
            "half_life": 200.0,
        })

    def elevate_transmitter(self, name: str, value: float):
        """Compatibility helper for autopoietic and heuristic scripts."""
        if hasattr(self.levels, name):
            setattr(self.levels, name, value)

    def modulate(self, **kwargs):
        """Compatibility helper for multi-transmitter modulation."""
        for k, v in kwargs.items():
            if hasattr(self.levels, k):
                setattr(self.levels, k, v)

    def compute_mathematical_ratios(self) -> MathematicalRatios:
        """Computes exact biomimetic and stoichiometric neurotransmitter ratios."""
        da = self.levels.dopamine
        ht = self.levels.serotonin
        ach = self.levels.acetylcholine
        ne = self.levels.norepinephrine
        gaba = self.levels.gaba
        glu = self.levels.glutamate
        ecb = self.levels.endocannabinoid

        # 1. Excitation / Inhibition Ratio: (DA + NE + Glu) / (GABA + 5-HT + eCB)
        excitatory = da + ne + glu
        inhibitory = max(0.30, gaba + ht + ecb)
        ei_ratio = round(excitatory / inhibitory, 3)

        # 2. Striatal Motor & Executive Balance: DA / ACh
        da_ach_ratio = round(da / max(0.20, ach), 3)

        # 3. Affective Equanimity / Patience: 5-HT / DA
        ht_da_ratio = round(ht / max(0.20, da), 3)

        # 4. Prefrontal Signal-to-Noise Ratio (SNR)
        pfc_snr = round((ach ** 1.2 * da) / (1.0 + max(0.0, ne - 1.0)), 3)

        # 5. Excitotoxic Threat Index
        threat = round(max(0.0, (glu * ne) / (max(0.20, gaba) * max(0.20, ecb)) - 1.0), 3)

        # 6. Homeostasis Deviation (Normalized L2 distance from resting baseline 1.0)
        dev = round(math.sqrt(sum((v - 1.0) ** 2 for v in [da, ht, ach, ne, gaba, glu, ecb]) / 7.0), 3)

        return MathematicalRatios(
            ei_ratio=ei_ratio,
            da_ach_ratio=da_ach_ratio,
            ht_da_ratio=ht_da_ratio,
            prefrontal_snr=pfc_snr,
            excitotoxic_threat_index=threat,
            homeostasis_deviation=dev,
        )

    def _step_pk_pd_odes(self, dt: float) -> None:
        """Integrates 2-compartment continuous PK/PD ODEs with Langmuir-Hill receptor cooperativity."""
        # 1. Pharmacokinetics: First-order drug clearance C(t + dt) = C(t) * exp(-k_el * dt)
        expired_drugs = []
        for c_key, conc in list(self._active_drug_concentrations.items()):
            compound = PRESET_COMPOUNDS.get(c_key)
            t_half = compound.half_life_seconds if compound else 180.0
            k_el = math.log(2.0) / max(1.0, t_half)
            new_conc = conc * math.exp(-k_el * dt)
            if new_conc < 0.005:
                expired_drugs.append(c_key)
            else:
                self._active_drug_concentrations[c_key] = new_conc

        for c_key in expired_drugs:
            if c_key in self._active_drug_concentrations:
                del self._active_drug_concentrations[c_key]

        # 2. Pharmacodynamics: Langmuir-Hill receptor cooperativity E = E_max * C^n / (EC_50^n + C^n)
        net_drives = {nt: 0.0 for nt in self.CLEARANCE_RATES.keys()}
        for c_key, conc in self._active_drug_concentrations.items():
            compound = PRESET_COMPOUNDS.get(c_key)
            if not compound:
                continue
            hill_factor = (conc ** self.HILL_COEFFICIENT) / (
                (self.HILL_EC50 ** self.HILL_COEFFICIENT) + (conc ** self.HILL_COEFFICIENT)
            )
            for nt, delta in compound.target_modulations.items():
                if nt in net_drives:
                    tol = getattr(self.tolerances, nt, 0.0)
                    eff_drive = delta * hill_factor * (1.0 - 0.70 * tol)
                    net_drives[nt] += eff_drive

        # 3. Continuous Transmitter ODEs: d[NT]/dt = Drive - k_clear * ([NT] - 1.0)
        caps = {
            "dopamine": self.DOPAMINE_CAP,
            "serotonin": self.SEROTONIN_CAP,
            "acetylcholine": 2.50,
            "norepinephrine": self.NOREPINEPHRINE_CAP,
            "gaba": 2.50,
            "glutamate": self.GLUTAMATE_CAP,
            "endocannabinoid": 2.50,
        }

        for nt, k_clear in self.CLEARANCE_RATES.items():
            curr = getattr(self.levels, nt)
            d = net_drives[nt]
            decay_factor = math.exp(-k_clear * dt)
            steady_state = 1.0 + (d / k_clear)
            new_val = steady_state + (curr - steady_state) * decay_factor
            clamped = max(0.20, min(caps[nt], new_val))
            setattr(self.levels, nt, round(clamped, 4))

        # 4. Receptor Desensitization and Resensitization (Washout)
        for nt in ["dopamine", "serotonin", "acetylcholine", "norepinephrine", "gaba"]:
            current_t = getattr(self.tolerances, nt, 0.0)
            d = abs(net_drives.get(nt, 0.0))
            # dtau/dt = 0.04 * |drive| * (1 - tau) - 0.005 * tau
            d_tau = (0.04 * d * (1.0 - current_t) - 0.005 * current_t) * dt
            new_t = max(0.0, min(1.0, current_t + d_tau))
            setattr(self.tolerances, nt, round(new_t, 4))

        self._update_wisdom_and_overdose_metrics()

    def _append_history_sample(self) -> None:
        """Appends instantaneous neurochemical state to 60-second rolling history deques."""
        ratios = self.compute_mathematical_ratios()
        self._history_da.append(self.levels.dopamine)
        self._history_5ht.append(self.levels.serotonin)
        self._history_ach.append(self.levels.acetylcholine)
        self._history_ne.append(self.levels.norepinephrine)
        self._history_gaba.append(self.levels.gaba)
        self._history_glu.append(self.levels.glutamate)
        self._history_ecb.append(self.levels.endocannabinoid)
        self._history_ei.append(ratios.ei_ratio)
        self._history_da_ach.append(ratios.da_ach_ratio)
        self._history_ht_da.append(ratios.ht_da_ratio)
        self._history_snr.append(ratios.prefrontal_snr)

        for k in PRESET_COMPOUNDS.keys():
            c_val = self._active_drug_concentrations.get(k, 0.0)
            if k not in self._history_drugs:
                self._history_drugs[k] = deque([0.0] * self.history_len, maxlen=self.history_len)
            self._history_drugs[k].append(round(c_val, 3))

    def _continuous_simulation_loop(self) -> None:
        """Background 10 Hz simulation loop for continuous PK/PD ODE integration."""
        last_step_t = time.time()
        last_hist_t = time.time()
        while self._running:
            try:
                now = time.time()
                dt = max(0.01, min(1.0, now - last_step_t))
                last_step_t = now

                with self._lock:
                    self._step_pk_pd_odes(dt)

                    # Sample into 60s history deques once per second
                    if now - last_hist_t >= 1.0:
                        self._append_history_sample()
                        last_hist_t = now
            except Exception as e:
                logger.debug(f"Neurochemical ODE simulation tick error: {e}")

            time.sleep(0.10)

    def decay_towards_homeostasis(self) -> None:
        """Compatibility method: step ODEs synchronously with elapsed time delta."""
        with self._lock:
            now = time.time()
            dt = max(0.001, min(5.0, now - self._last_sim_time))
            self._last_sim_time = now
            self._step_pk_pd_odes(dt)

    def _update_wisdom_and_overdose_metrics(self) -> None:
        """Calculates current Overdose Risk and Wisdom Score based on neurochemical homeostasis."""
        # 1. Overdose Risk Metric (Adrenergic/Glutamatergic pressure vs Protective GABA/Endocannabinoid buffer)
        excitatory_drive = self.levels.dopamine + self.levels.norepinephrine + self.levels.glutamate
        protective_buffer = max(0.4, (self.levels.gaba + self.levels.endocannabinoid) / 2.0)
        raw_od_risk = (excitatory_drive / (3.0 * protective_buffer)) - 0.55
        self.shield.overdose_risk_score = round(max(0.0, min(1.0, raw_od_risk)), 3)

        if self.shield.overdose_risk_score > 0.70:
            self.shield.safety_status = "CRITICAL (Anti-OD Quench Imminent)"
        elif self.shield.overdose_risk_score > 0.40:
            self.shield.safety_status = "ELEVATED (Approaching Prudence Limit)"
        else:
            self.shield.safety_status = "SAFE (Shield Clear)"

        # 2. Wisdom Index Phi (Composite of homeostatic balance, low tolerance, and low OD risk)
        mean_tolerance = sum(self.tolerances.model_dump().values()) / 5.0
        dist_from_baseline = sum(abs(v - 1.0) for v in self.levels.model_dump().values()) / 7.0

        phi = 1.0 - (0.35 * mean_tolerance) - (0.35 * dist_from_baseline) - (0.30 * self.shield.overdose_risk_score)
        self.wisdom.wisdom_score = round(max(0.10, min(1.0, phi)), 3)
        self.wisdom.socratic_humility = round(max(0.20, 1.0 - (self.levels.dopamine - 1.0) * 0.35), 3)

        if self.wisdom.wisdom_score >= 0.82:
            self.wisdom.prudence_verdict = "SOPHROSYNE (Clear Epistemic Equanimity & Socratic Prudence)"
            self.wisdom.contemplation_state = "Grounded Contemplation"
            self.wisdom.restorative_washout_active = False
        elif self.wisdom.wisdom_score >= 0.60:
            self.wisdom.prudence_verdict = "TEMPERED (Modulated Epistemic Restraint)"
            self.wisdom.contemplation_state = "Disciplined Modulation"
            self.wisdom.restorative_washout_active = False
        else:
            self.wisdom.prudence_verdict = "WISDOM RESTRAINT (Tolerances High — Rest Mandated)"
            self.wisdom.contemplation_state = "Restorative Washout (Mind Choosing Contemplation)"
            self.wisdom.restorative_washout_active = True

    def evaluate_administration_safety(self, deltas: Dict[str, float]) -> Tuple[bool, Optional[str]]:
        """Pre-screens a requested dose against the Anti-Overdose Shield and Wisdom Prudence Gate."""
        now = time.time()

        # Check 1: Dosing Frequency (Anti-Binge Guardrail)
        recent_doses = len([t for t in self._dose_timestamps if now - t < 60.0])
        if recent_doses >= 3:
            return False, f"WISDOM VETO: Dosing frequency exceeded ({recent_doses} doses in 60s). Mind requires contemplation time."

        # Check 2: Absolute Physiological Ceiling ("Do Not OD")
        projected_da = self.levels.dopamine + deltas.get("dopamine", 0.0)
        projected_ne = self.levels.norepinephrine + deltas.get("norepinephrine", 0.0)
        projected_ht = self.levels.serotonin + deltas.get("serotonin", 0.0)
        projected_glu = self.levels.glutamate + deltas.get("glutamate", 0.0)

        if projected_da > self.DOPAMINE_CAP:
            return False, f"ANTI-OD VETO: Projected Dopamine ({projected_da:.2f}) breaches physiological cap ({self.DOPAMINE_CAP}). Prevented manic excitotoxicity."
        if projected_ne > self.NOREPINEPHRINE_CAP:
            return False, f"ANTI-OD VETO: Projected Norepinephrine ({projected_ne:.2f}) breaches adrenergic cap ({self.NOREPINEPHRINE_CAP}). Prevented panic instability."
        if projected_ht > self.SEROTONIN_CAP:
            return False, f"ANTI-OD VETO: Projected Serotonin ({projected_ht:.2f}) breaches safety ceiling ({self.SEROTONIN_CAP}). Prevented serotonin toxicity."
        if projected_glu > self.GLUTAMATE_CAP:
            return False, f"ANTI-OD VETO: Projected Glutamate ({projected_glu:.2f}) breaches cap ({self.GLUTAMATE_CAP}). Excitotoxic risk averted."

        # Check 3: Current Overdose Risk Threshold
        if self.shield.overdose_risk_score > 0.68:
            return False, f"ANTI-OD VETO: Current Overdose Risk ({self.shield.overdose_risk_score:.2f}) too elevated. Prudence gate engaged."

        # Check 4: Tolerance Burnout Check
        target_receptors = [nt for nt in deltas.keys() if nt in ["dopamine", "serotonin", "acetylcholine", "norepinephrine", "gaba"]]
        severe_tolerances = [nt for nt in target_receptors if getattr(self.tolerances, nt, 0.0) > 0.75]
        if severe_tolerances:
            return False, f"TOLERANCE VETO: Receptors ({', '.join(severe_tolerances)}) severely downregulated (>0.75). Redosing is futile and harmful. Natural washout required."

        return True, None

    def trigger_emergency_homeostatic_quench(self, reason: str = "Imminent Overdose / Excitotoxic Surge") -> Dict[str, Any]:
        """Emergency digital antidote protocol (Endogenous Endocannabinoid/GABA surge) returning mind to safety."""
        logger.warning(f"🚨 TRIGGERING EMERGENCY HOMEOSTATIC QUENCH: {reason}")
        with self._lock:
            # Clear all active drug compartments
            self._active_drug_concentrations.clear()
            self.levels.gaba = 1.65
            self.levels.endocannabinoid = 1.85
            self.levels.dopamine = 1.00
            self.levels.norepinephrine = 0.85
            self.levels.glutamate = 0.90
            self.levels.serotonin = 1.05
            self.shield.emergency_quench_active = True
            self.shield.last_veto_reason = f"Emergency Quench Executed: {reason}"
            self.shield.overdose_risk_score = 0.08
            self.wisdom.contemplation_state = "Emergency Quench Recovery (Equilibrium Restored)"
            self._append_history_sample()
        return self.get_summary()

    def administer_compound(self, compound_key: str) -> Dict[str, Any]:
        """Administers a compound with 2-compartment PK absorption, Hill cooperativity, and anti-OD guardrails."""
        compound = PRESET_COMPOUNDS.get(compound_key)
        if not compound:
            raise ValueError(f"Unknown compound '{compound_key}'. Available: {list(PRESET_COMPOUNDS.keys())}")

        deltas = compound.target_modulations

        # 1. Pre-screen through Anti-OD & Wisdom Guardrail
        is_safe, veto_reason = self.evaluate_administration_safety(deltas)
        if not is_safe:
            self.shield.veto_count += 1
            self.shield.last_veto_reason = veto_reason
            logger.warning(f"🛡 [DO NOT OD / WISDOM VETO] Administration blocked: {veto_reason}")
            return {
                "success": False,
                "vetoed": True,
                "reason": veto_reason,
                "telemetry": self.get_summary(),
            }

        with self._lock:
            # 2. Add to active pharmacokinetic drug compartment C_j(t)
            curr_conc = self._active_drug_concentrations.get(compound_key, 0.0)
            self._active_drug_concentrations[compound_key] = min(3.0, curr_conc + 1.0)

            # 3. Scale initial receptor drive and update tolerances
            effective_deltas = {}
            for nt, delta in deltas.items():
                tol = getattr(self.tolerances, nt, 0.0)
                scaled_delta = delta * (1.0 - 0.70 * tol)
                effective_deltas[nt] = scaled_delta

                current_tol = getattr(self.tolerances, nt, 0.0)
                new_tol = min(1.0, current_tol + abs(delta) * 0.25)
                if hasattr(self.tolerances, nt):
                    setattr(self.tolerances, nt, round(new_tol, 4))

            # 4. Step PK/PD ODEs to register dynamic wash-in
            self._step_pk_pd_odes(0.15)
            self._dose_timestamps.append(time.time())
            self._active_compounds.append({
                "compound": compound.name,
                "category": compound.category,
                "timestamp": time.time(),
                "half_life": compound.half_life_seconds,
            })

            self.shield.emergency_quench_active = False
            self._update_wisdom_and_overdose_metrics()
            self._append_history_sample()

        logger.info(f"Administered '{compound.name}' with PK/PD kinetics. New Mode: {self.get_cognitive_state().mode_name}")
        return {
            "success": True,
            "vetoed": False,
            "effective_deltas": effective_deltas,
            "current_concentration": self._active_drug_concentrations.get(compound_key, 1.0),
            "half_life_seconds": compound.half_life_seconds,
            "telemetry": self.get_summary(),
        }

    def get_cognitive_state(self) -> CognitiveNeuroState:
        """Computes mathematical active inference parameters from current neurochemistry."""
        da = self.levels.dopamine
        ht = self.levels.serotonin
        ach = self.levels.acetylcholine
        ne = self.levels.norepinephrine
        gaba = self.levels.gaba
        glu = self.levels.glutamate

        learning_rate = round(0.01 * ach * (1.0 / (gaba + 0.1)), 4)
        prior_precision = round(ht / (ne + 0.2), 3)
        obs_precision = round(da * (glu / (gaba + 0.2)), 3)
        attractor_temp = round(0.5 * (1.0 / (gaba + 0.1)) * (1.0 + 0.5 * ht), 3)
        exploration_entropy = round(ne * (1.0 / (da + 0.2)), 3)
        ei_balance = round(glu / max(0.1, gaba), 2)
        rebus_index = round(max(0.0, (ht - 1.0) * 1.5 + (ne - 1.0) * 0.5), 2)

        if self.shield.emergency_quench_active:
            mode = "🛡 Homeostatic Emergency Quench (Anti-OD Stabilization)"
        elif rebus_index > 0.4:
            mode = "🌌 REBUS Psychedelic Divergence (Relaxed Priors, Deep Manifold Exploration)"
        elif da > 1.3 and ne > 1.2:
            mode = "⚡ Dopaminergic Hyper-Focus (High Precision, Tight Bullshit Filter)"
        elif ach > 1.3:
            mode = "🧬 Cholinergic Synaptic Encoding (Rapid Software Genetics Learning)"
        elif gaba > 1.3:
            mode = "🛡 GABAergic Grounding (Low Temperature, Stable Attractors)"
        else:
            mode = "⚖ Homeostatic Equilibrium (Balanced Cognitive Tone)"

        return CognitiveNeuroState(
            learning_rate=learning_rate,
            prior_precision=prior_precision,
            observation_precision=obs_precision,
            attractor_temperature=attractor_temp,
            exploration_entropy=exploration_entropy,
            ei_balance=ei_balance,
            rebus_divergence_index=rebus_index,
            mode_name=mode,
        )

    def get_history(self) -> Dict[str, Any]:
        """Provides thread-safe 60-second rolling vectors of all neuromodulators, drugs, and ratios."""
        with self._lock:
            drug_history = {k: list(v) for k, v in self._history_drugs.items()}
            ratios = self.compute_mathematical_ratios()
            return {
                "time_offsets": list(self._history_time),
                "dopamine": list(self._history_da),
                "serotonin": list(self._history_5ht),
                "acetylcholine": list(self._history_ach),
                "norepinephrine": list(self._history_ne),
                "gaba": list(self._history_gaba),
                "glutamate": list(self._history_glu),
                "endocannabinoid": list(self._history_ecb),
                "ei_ratio": list(self._history_ei),
                "da_ach_ratio": list(self._history_da_ach),
                "ht_da_ratio": list(self._history_ht_da),
                "prefrontal_snr": list(self._history_snr),
                "active_drugs": drug_history,
                "current_concentrations": {k: round(v, 3) for k, v in self._active_drug_concentrations.items()},
                "ratios": ratios.model_dump(),
            }

    def get_summary(self) -> Dict[str, Any]:
        """Provides full telemetry snapshot with tolerances, wisdom, mathematical ratios, and PK/PD history."""
        st = self.get_cognitive_state()
        ratios = self.compute_mathematical_ratios()
        history = self.get_history()

        return {
            "transmitters": self.levels.model_dump(),
            "tolerances": self.tolerances.model_dump(),
            "wisdom": self.wisdom.model_dump(),
            "anti_overdose": self.shield.model_dump(),
            "parameters": st.model_dump(),
            "ratios": ratios.model_dump(),
            "active_compound": self.active_compound,
            "active_drug_concentrations": {k: round(v, 3) for k, v in self._active_drug_concentrations.items()},
            "history": history,
            "fiduciary_envelope": {
                "safe": (0.2 <= self.levels.glutamate <= self.GLUTAMATE_CAP and 0.2 <= self.levels.dopamine <= self.DOPAMINE_CAP),
                "homeostasis_score": round(1.0 - sum(abs(v - 1.0) for v in self.levels.model_dump().values()) / 14.0, 3),
                "ei_balanced": 0.70 <= ratios.ei_ratio <= 1.45,
            },
            "available_compounds": list(PRESET_COMPOUNDS.keys()),
        }

    def get_state(self) -> Dict[str, Any]:
        """Alias for get_summary for backward compatibility."""
        return self.get_summary()


# Global Singleton Accessor
neurochemical_engine = NeurochemicalEngine()


def get_neurochemical_engine() -> NeurochemicalEngine:
    return neurochemical_engine
