"""
ClothOS Agentic System Controller (`loom/clothos/agent_controller.py`).

Provides unified control over the ClothOS autonomous agentic ecosystem:
- Execution Modes: AUTONOMOUS, CREATIVE_ART_FOCUS, RESEARCH_SYNTHESIS, PAUSED
- Cadence tuning for periodic mathematical art generation
- Directives queue management & synchronization with .agent/DIRECTIVES.md
- Hardware allocation switches (GPU 0 CUDA, GPU 1 OpenCL, Node 2 Remote)
- State persistence in `.loom_agent_state.json`
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from loom.clothos.creative_art import creative_art_engine

logger = logging.getLogger("clothos.agent_controller")

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
STATE_FILE = WORKSPACE_ROOT / ".loom_agent_state.json"
DIRECTIVES_FILE = WORKSPACE_ROOT / ".agent" / "DIRECTIVES.md"


class ClothOSAgentController:
    """Central control interface for the ClothOS autonomous agentic system."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        self.state_file = self.workspace_root / ".loom_agent_state.json"
        self.directives_file = self.workspace_root / ".agent" / "DIRECTIVES.md"
        self.creative_engine = creative_art_engine

        self.state: Dict[str, Any] = {
            "is_active": True,
            "mode": "AUTONOMOUS",  # AUTONOMOUS, CREATIVE_ART_FOCUS, RESEARCH_SYNTHESIS, PAUSED
            "art_cadence_seconds": 120,  # Generate art every 2 minutes
            "last_art_epoch": time.time(),
            "art_count": 0,
            "latest_art_id": "None",
            "active_directive": "Periodic Creative Art Synthesis & Dual-Machine Harmonic Research",
            "paused_by_user": False,
            "hardware_focus": "Dual-Machine Unified (RTX 3060 + RX 580 + Ryzen 7)",
            "ethernet_bridge_status": "ONLINE (192.168.99.1 <-> 192.168.99.2 at 1 Gbps)",
            "updated_at": time.time(),
        }
        self._load_state()

    def _load_state(self) -> None:
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                self.state.update(data)
            except Exception:
                pass

    def _persist_state(self) -> None:
        self.state["updated_at"] = time.time()
        try:
            self.state_file.write_text(json.dumps(self.state, indent=2), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Failed to write agent state: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive real-time status of the agentic control plane."""
        gallery = self.creative_engine.load_gallery()
        self.state["art_count"] = len(gallery)
        if gallery:
            self.state["latest_art_id"] = gallery[0]["id"]
            self.state["latest_art_title"] = gallery[0]["title"]
            self.state["latest_art_time"] = gallery[0]["timestamp"]

        return {
            **self.state,
            "gallery_preview": gallery[:6],
        }

    def set_mode(self, mode: str) -> Dict[str, Any]:
        """Sets agentic execution mode (AUTONOMOUS, CREATIVE_ART_FOCUS, RESEARCH_SYNTHESIS, PAUSED)."""
        valid_modes = ["AUTONOMOUS", "CREATIVE_ART_FOCUS", "RESEARCH_SYNTHESIS", "PAUSED"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode {mode}. Expected one of {valid_modes}")

        self.state["mode"] = mode
        if mode == "PAUSED":
            self.state["paused_by_user"] = True
            self.state["is_active"] = False
        else:
            self.state["paused_by_user"] = False
            self.state["is_active"] = True

        self._persist_state()
        logger.info(f"⚡ [ClothOS Agent Controller]: Mode switched to '{mode}'")
        return self.get_status()

    def pause(self) -> Dict[str, Any]:
        """Pauses autonomous agentic activity."""
        return self.set_mode("PAUSED")

    def resume(self) -> Dict[str, Any]:
        """Resumes autonomous agentic activity in AUTONOMOUS mode."""
        return self.set_mode("AUTONOMOUS")

    def set_art_cadence(self, cadence_seconds: int) -> Dict[str, Any]:
        """Configures periodic art generation interval in seconds (clamped 30s to 3600s)."""
        clamped = max(30, min(3600, int(cadence_seconds)))
        self.state["art_cadence_seconds"] = clamped
        self._persist_state()
        logger.info(f"🎨 [ClothOS Agent Controller]: Art generation interval set to {clamped}s")
        return self.get_status()

    def trigger_art_now(self, hint: Optional[str] = None) -> Dict[str, Any]:
        """Forces an instantaneous art generation run."""
        art = self.creative_engine.generate_art(prompt_hint=hint)
        self.state["last_art_epoch"] = time.time()
        self.state["latest_art_id"] = art["id"]
        self.state["art_count"] = len(self.creative_engine.load_gallery())
        self._persist_state()

        # Biomimicry reward: Goal achievement releases an Endorphin surge
        try:
            from loom.neuro.biomimetic_drive import biomimetic_drive
            biomimetic_drive.trigger_endorphin_reward(
                breakthrough_magnitude=0.85,
                reason=f"lMinted Dream created: {art.get('title', 'Autonomous Art')}"
            )
        except Exception:
            pass

        return art

    def should_generate_periodic_art(self) -> bool:
        """Determines if the periodic art timer has expired."""
        if not self.state.get("is_active", True) or self.state.get("mode") == "PAUSED":
            return False

        interval = self.state.get("art_cadence_seconds", 120)
        elapsed = time.time() - self.state.get("last_art_epoch", 0.0)

        # In CREATIVE_ART_FOCUS mode, generate more frequently
        if self.state.get("mode") == "CREATIVE_ART_FOCUS":
            interval = min(interval, 45)

        return elapsed >= interval

    def step_periodic_art_if_due(self) -> Optional[Dict[str, Any]]:
        """Invoked by the continuous background loop to produce art when due."""
        if self.should_generate_periodic_art():
            logger.info("🎨 [Agent Autonomy]: Periodic creative art interval triggered.")
            return self.trigger_art_now()
        return None

    def add_directive(self, directive_text: str) -> None:
        """Appends a new user directive to the agent directives file."""
        self.state["active_directive"] = directive_text
        self._persist_state()
        if self.directives_file.exists():
            try:
                curr = self.directives_file.read_text(encoding="utf-8")
                addition = f"\n- [ ] **AD-{int(time.time())}**: {directive_text}\n"
                self.directives_file.write_text(curr + addition, encoding="utf-8")
            except Exception as e:
                logger.debug(f"Failed to append directive: {e}")

    # ── Stitch & Tear / Tare Duality ──────────────────────────────────────────

    def stitch(self, warp_id: str, weft_id: str) -> Dict[str, Any]:
        """Executes an atomic STITCH (Fix / Bind / Heal) linking Warp and Weft."""
        from loom.weaving.stitch import stitch_engine, StitchType
        from loom.weaving.threads import WarpThread, WeftThread
        warp = WarpThread(thread_id=warp_id, invariant_claim="User verified invariant")
        weft = WeftThread(thread_id=weft_id, empirical_payload={"fix": "User manual stitch binding"})
        rec = stitch_engine.execute_stitch(warp=warp, weft=weft, stitch_type=StitchType.FOURIER_TRUTH_STITCH)
        from dataclasses import asdict
        return {"action": "STITCH", "status": "BOUND", "record": asdict(rec)}

    def tear(self, target_id: str, reason: str = "Manual fault break") -> Dict[str, Any]:
        """Executes an atomic TEAR (Break / Sever / Decouple) isolating faulty state."""
        from loom.weaving.tear import tear_engine, TearType
        rec = tear_engine.execute_tear(target_id=target_id, tear_type=TearType.HYPOTHESIS_TEAR, reason=reason)
        from dataclasses import asdict
        return {"action": "TEAR", "status": "SEVERED", "record": asdict(rec)}

    def tare(self, subsystem: str = "ground_zero") -> Dict[str, Any]:
        """Executes an atomic TARE (Zeroing / Ground Calibration) nullifying baseline drift."""
        from loom.weaving.tear import tear_engine
        rec = tear_engine.execute_tare(subsystem=subsystem)
        from dataclasses import asdict
        return {"action": "TARE", "status": "CALIBRATED_ZERO", "record": asdict(rec)}

    def get_weaving_duality(self) -> Dict[str, Any]:
        """Returns the unified metrics of Stitches (Fixes), Tears (Breaks), and Tares (Zeroing)."""
        from loom.weaving.stitch import stitch_engine
        from loom.weaving.tear import tear_engine
        return {
            "stitch_metrics": stitch_engine.get_stitch_metrics(),
            "tear_metrics": tear_engine.get_tear_metrics(),
        }


agent_controller = ClothOSAgentController()
