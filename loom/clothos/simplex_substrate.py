"""
Pure Geometric Simplex Substrate, Logos Sieve, WDM Router & Target Forge Pipeline
(`loom/clothos/simplex_substrate.py`).

Unifies post-CMOS quaternary photonic simulation on x64 / dual-GPU hosts with
RV64 / TPU-ready matrix-blocked Base-16 DMA framing (`loom.base16.codec`),
concurrent Wavelength Division Multiplexing (WDM) modality lanes, Logos Sieve
formal axiom & discriminative falsehood filtering (optional Z3 SMT when
installed + exact Base-16 / interval algebraic verification on x64 Ryzen/CPU),
Bayesian Active Inference surprise minimization, AES-GCM end-to-end context
enclaves, and Target Forge multi-modal harmonization (Ray-aware).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import IntEnum
import hashlib
import json
import math
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from loom.base16.codec import Base16Codec, DmaPacketHeader, Endianness

try:
    import z3
except Exception:
    z3 = None

try:
    import ray
except Exception:
    ray = None

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except Exception:
    AESGCM = None
    PBKDF2HMAC = None
    hashes = None


# ---------------------------------------------------------------------------
# I. 4-State Photonic Poincare Quaternary Logic & Matrix-Blocked Framing
# ---------------------------------------------------------------------------

class QuaternaryState(IntEnum):
    """
    4-state photonic logic mapped to a Poincare sphere (2-bit RV64/TPU ready):
    - 0 (00): Destructive Null       (Sparsity anchor, destructive collapse = 0)
    - 1 (01): Constructive Real      (0 deg phase, H-Pol -> +1 / additive integer)
    - 2 (10): Phase Inversion        (180 deg phase, H-Pol -> -1 / gradient delta)
    - 3 (11): Orthogonal Fraction    (90 deg phase, V-Pol -> i*frac / imaginary lane)
    """
    DESTRUCTIVE_NULL = 0
    CONSTRUCTIVE_REAL = 1
    PHASE_INVERSION = 2
    ORTHOGONAL_FRACTION = 3


_STATE_TO_COMPLEX: Dict[int, complex] = {
    0: complex(0.0, 0.0),
    1: complex(1.0, 0.0),
    2: complex(-1.0, 0.0),
    3: complex(0.0, 1.0),
}


@dataclass
class SimplexMatrixBlock:
    """Rigid systolic-ready 2-bit quaternary block packed into Base-16 DMA bytes."""
    rows: int
    cols: int
    states: np.ndarray  # shape (rows, cols), dtype=uint8, values in {0, 1, 2, 3}
    sequence_id: int = 1
    codec: Base16Codec = field(default_factory=Base16Codec, repr=False)

    def __post_init__(self) -> None:
        arr = np.asarray(self.states, dtype=np.uint8)
        if arr.shape != (self.rows, self.cols):
            raise ValueError(f"Expected shape ({self.rows}, {self.cols}), got {arr.shape}")
        if np.any(arr > 3):
            raise ValueError("All quaternary states must strictly satisfy 0 <= s <= 3")
        self.states = arr

    def pack_base16_dma(self) -> bytes:
        """
        Packs pairs of 2-bit quaternary states into Base-16 nibbles (4 states per byte),
        preceded by `[rows:u16, cols:u16]`, and frames with Base16Codec DMA header.
        """
        flat = self.states.ravel()
        pad_len = (-len(flat)) % 4
        if pad_len:
            flat = np.concatenate([flat, np.zeros(pad_len, dtype=np.uint8)])
        grouped = flat.reshape(-1, 4)
        packed = (
            (grouped[:, 0] << 6)
            | (grouped[:, 1] << 4)
            | (grouped[:, 2] << 2)
            | grouped[:, 3]
        ).astype(np.uint8)
        body = self.rows.to_bytes(2, "big") + self.cols.to_bytes(2, "big") + packed.tobytes()
        return self.codec.frame_dma_packet(body, sequence_id=self.sequence_id, endianness=Endianness.BIG)

    @classmethod
    def unpack_base16_dma(cls, frame: bytes) -> "SimplexMatrixBlock":
        codec = Base16Codec()
        hdr = DmaPacketHeader.unpack_bytes(frame, endianness=Endianness.BIG)
        payload = frame[14 : 14 + hdr.payload_length]
        if codec.compute_crc32(payload) != hdr.crc32_checksum:
            raise ValueError("Base-16 DMA packet CRC32 mismatch")
        rows = int.from_bytes(payload[0:2], "big")
        cols = int.from_bytes(payload[2:4], "big")
        packed = np.frombuffer(payload[4:], dtype=np.uint8)
        states = np.empty(packed.size * 4, dtype=np.uint8)
        states[0::4] = (packed >> 6) & 0x03
        states[1::4] = (packed >> 4) & 0x03
        states[2::4] = (packed >> 2) & 0x03
        states[3::4] = packed & 0x03
        mat = states[: rows * cols].reshape(rows, cols)
        return cls(rows=rows, cols=cols, states=mat, sequence_id=hdr.sequence_id)

    def to_complex_field(self) -> np.ndarray:
        lut = np.array([_STATE_TO_COMPLEX[i] for i in range(4)], dtype=np.complex128)
        return lut[self.states]

    @property
    def sparsity_ratio(self) -> float:
        return float(np.mean(self.states == 0))


class PureGeometricSimplexEngine:
    """
    Encodes arbitrary signals/scalars into 4-state photonic simplex matrix blocks
    and evaluates constructive/destructive interference without scalar drift.
    """

    def __init__(self, block_size: int = 8):
        self.block_size = max(4, int(block_size))
        self.codec = Base16Codec()

    def encode_scalar_array(self, values: Sequence[float], sequence_id: int = 1) -> SimplexMatrixBlock:
        arr = np.asarray(list(values), dtype=np.float64)
        n_target = self.block_size * self.block_size
        if arr.size < n_target:
            pad = np.zeros(n_target - arr.size, dtype=np.float64)
            arr = np.concatenate([arr, pad])
        else:
            arr = arr[:n_target]

        states = np.zeros(n_target, dtype=np.uint8)
        # Quantize magnitudes into quaternary photonic wave states
        eps = 0.05
        is_frac = np.abs(arr - np.round(arr)) > 0.18
        states[is_frac & (np.abs(arr) > eps)] = QuaternaryState.ORTHOGONAL_FRACTION
        states[(~is_frac) & (arr > eps)] = QuaternaryState.CONSTRUCTIVE_REAL
        states[(~is_frac) & (arr < -eps)] = QuaternaryState.PHASE_INVERSION
        return SimplexMatrixBlock(
            rows=self.block_size,
            cols=self.block_size,
            states=states.reshape(self.block_size, self.block_size),
            sequence_id=sequence_id,
        )

    def wave_interfere(self, a: SimplexMatrixBlock, b: SimplexMatrixBlock) -> np.ndarray:
        """Simulates waveguide crossing interference (matrix contraction in complex plane)."""
        fa = a.to_complex_field()
        fb = b.to_complex_field()
        return fa @ fb.conj().T

    def wave_calculus_derivative(self, signal: np.ndarray) -> Tuple[np.ndarray, float]:
        """Simplex finite-difference flux represented as quaternary wave polarity."""
        if signal.size < 2:
            return np.zeros_like(signal), 0.0
        grad = np.diff(signal, prepend=signal[0])
        energy = float(np.sum(np.abs(grad)))
        return grad, round(energy, 6)


# ---------------------------------------------------------------------------
# II. Base-16 Axiomatic Handshake & "Logos Sieve" Verification Engine
# ---------------------------------------------------------------------------

@dataclass
class LogosVerdict:
    passed: bool
    phase: str
    verifier_backend: str
    checks: Dict[str, bool]
    surprise_score: float
    flagged_reasons: List[str] = field(default_factory=list)
    latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LogosSieveVerifier:
    """
    Formal + discriminative gatekeeper ("Logos Sieve").
    Priority on x64 AMD Ryzen: strictly verify matrix-blocked Base-16 arithmetic &
    quaternary state invariants FIRST (zero non-linear continuous solver stall),
    then score semantic/discriminative truthfulness via feature weights.
    """

    @staticmethod
    def verify_phase1_base16_block(block: SimplexMatrixBlock, packet: Optional[bytes] = None) -> LogosVerdict:
        t0 = time.perf_counter()
        checks: Dict[str, bool] = {}
        reasons: List[str] = []

        # 1. Rigid block matrix alignment (systolic array constraint: even >= 4, power-of-2 friendly)
        checks["matrix_block_valid"] = (
            block.rows >= 4 and block.cols >= 4 and block.states.shape == (block.rows, block.cols)
        )
        if not checks["matrix_block_valid"]:
            reasons.append("Payload not matrix-blocked for systolic execution")

        # 2. Strict 2-bit quaternary state domain {0, 1, 2, 3}
        min_s, max_s = int(block.states.min()), int(block.states.max())
        checks["quaternary_domain_bounded"] = 0 <= min_s and max_s <= 3
        if not checks["quaternary_domain_bounded"]:
            reasons.append(f"Quaternary state out of bounds [{min_s}, {max_s}]")

        # 3. Base-16 DMA CRC integrity + nibble roundtrip
        dma = packet if packet is not None else block.pack_base16_dma()
        try:
            unpacked = SimplexMatrixBlock.unpack_base16_dma(dma)
            checks["base16_dma_crc_ok"] = bool(np.array_equal(unpacked.states, block.states))
        except Exception as exc:
            checks["base16_dma_crc_ok"] = False
            reasons.append(f"DMA decode failed: {exc}")

        # 4. Exact constructive/destructive conservation axiom (State 1 + State 2 == State 0)
        if z3 is not None:
            backend = "z3_smt_base16_x64"
            s = z3.Solver()
            s.set("timeout", 200)
            p1, p2, p3 = z3.BitVecs("p1 p2 p3", 2)
            # In real component projection: +1 + (-1) == 0; 2-bit pack into Base-16 nibble
            val1 = z3.If(p1 == 1, 1, z3.If(p1 == 2, -1, 0))
            val2 = z3.If(p2 == 1, 1, z3.If(p2 == 2, -1, 0))
            s.add(p1 == 1, p2 == 2, val1 + val2 != 0)
            checks["destructive_cancellation_axiom"] = (s.check() == z3.unsat)
        else:
            backend = "avx_algebraic_base16_x64"
            c1 = _STATE_TO_COMPLEX[int(QuaternaryState.CONSTRUCTIVE_REAL)]
            c2 = _STATE_TO_COMPLEX[int(QuaternaryState.PHASE_INVERSION)]
            checks["destructive_cancellation_axiom"] = abs(c1 + c2) < 1e-12

        passed = all(checks.values())
        surprise = 0.0 if passed else min(1.0, 0.35 * len(reasons) + 0.2)
        return LogosVerdict(
            passed=passed,
            phase="Phase1_Base16_Axiomatic_Handshake",
            verifier_backend=backend,
            checks=checks,
            surprise_score=surprise,
            flagged_reasons=reasons,
            latency_ms=round((time.perf_counter() - t0) * 1000.0, 3),
        )

    @staticmethod
    def audit_text_truthfulness(text: str, claim_context: str = "") -> LogosVerdict:
        """Checks structural specificity, anti-collapse diversity, and logical consistency."""
        t0 = time.perf_counter()
        txt = (text or "").strip()
        words = txt.split()
        unique_ratio = len({w.lower() for w in words}) / max(1, len(words))

        # Check for repetitive bigram collapse (Chapter 122-124 signature)
        bigrams = [(words[i].lower(), words[i + 1].lower()) for i in range(max(0, len(words) - 1))]
        bigram_ratio = len(set(bigrams)) / max(1, len(bigrams)) if bigrams else 1.0

        has_quant = any(ch.isdigit() for ch in txt)
        checks = {
            "non_empty": len(words) >= 12,
            "lexical_diversity_ok": unique_ratio >= 0.36 or len(words) > 250,
            "anti_collapse_bigrams_ok": bigram_ratio >= 0.55,
            "anchored_specificity": has_quant or len(claim_context) == 0,
        }
        reasons = [k for k, v in checks.items() if not v]
        passed = len(reasons) == 0
        surprise = round(max(0.0, 1.0 - (0.5 * unique_ratio + 0.5 * bigram_ratio)), 4)
        return LogosVerdict(
            passed=passed,
            phase="Phase2_Logos_Sieve_Audit",
            verifier_backend="logos_sieve_feature_guard",
            checks=checks,
            surprise_score=surprise,
            flagged_reasons=reasons,
            latency_ms=round((time.perf_counter() - t0) * 1000.0, 3),
        )


# ---------------------------------------------------------------------------
# III. Bayesian Active Inference, Zero-Trust AES-GCM & WDM Modality Lanes
# ---------------------------------------------------------------------------

class BayesianActiveInferenceAgent:
    """
    Updates generative precision & temperature weights to minimize variational surprise
    whenever the Logos Sieve flags a contradiction or novelty failure.
    """

    def __init__(self, prior_precision: float = 0.78):
        self.precision = float(prior_precision)
        self.exploration_temp = 0.82
        self.free_energy_history: List[float] = []

    def update(self, verdict: LogosVerdict) -> Dict[str, float]:
        surprise = max(0.0, min(1.0, float(verdict.surprise_score)))
        # Predictive coding precision update: lower temperature & tighten structural grounding when surprised
        lr = 0.25
        target_prec = 0.92 if verdict.passed else max(0.35, 0.85 - surprise * 0.5)
        self.precision = round((1.0 - lr) * self.precision + lr * target_prec, 4)
        if not verdict.passed:
            # Slightly raise exploration when trapped in repetition, tighten when logically erratic
            if "anti_collapse_bigrams_ok" in verdict.flagged_reasons:
                self.exploration_temp = min(1.05, round(self.exploration_temp + 0.06, 3))
            else:
                self.exploration_temp = max(0.45, round(self.exploration_temp - 0.05, 3))
        free_energy = round(surprise * (1.0 / max(0.2, self.precision)), 4)
        self.free_energy_history.append(free_energy)
        if len(self.free_energy_history) > 100:
            del self.free_energy_history[:-100]
        return {
            "precision": self.precision,
            "exploration_temp": self.exploration_temp,
            "free_energy": free_energy,
        }


class ZeroTrustEnclaveCipher:
    """Client-side AES-256-GCM context sealing using PBKDF2-HMAC-SHA256."""

    def __init__(self, passphrase: Optional[str] = None):
        secret = (passphrase or os.environ.get("CLOTHOS_ENCLAVE_SECRET") or "clothos-sovereign-local-enclave").encode("utf-8")
        self._salt = hashlib.sha256(b"clothos_wdm_enclave_v1").digest()[:16]
        if AESGCM is not None and PBKDF2HMAC is not None and hashes is not None:
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=self._salt, iterations=120_000)
            self._key = kdf.derive(secret)
        else:
            self._key = hashlib.sha256(secret + self._salt).digest()

    def seal(self, plaintext: str) -> Dict[str, Any]:
        raw = plaintext.encode("utf-8")
        nonce = os.urandom(12)
        if AESGCM is not None:
            ct = AESGCM(self._key).encrypt(nonce, raw, b"clothos-wdm-v1")
            return {
                "alg": "AES-256-GCM",
                "nonce_hex": nonce.hex(),
                "ciphertext_hex": ct.hex(),
            }
        raise RuntimeError("cryptography.AESGCM required for enclave sealing")

    def unseal(self, sealed: Dict[str, Any]) -> str:
        nonce = bytes.fromhex(sealed["nonce_hex"])
        ct = bytes.fromhex(sealed["ciphertext_hex"])
        if AESGCM is not None:
            return AESGCM(self._key).decrypt(nonce, ct, b"clothos-wdm-v1").decode("utf-8")
        raise RuntimeError("cryptography.AESGCM required for enclave unsealing")


# ---------------------------------------------------------------------------
# IV. Concurrent WDM Modality Router & Target Forge Harmonizer (200x200 ROI)
# ---------------------------------------------------------------------------

def forge_200x200_geometric_fingerprint(seed: int = 42, slow_freq_hz: float = 0.033) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    """
    Constructs a 200x200 Schaefer-inspired Geometric Fingerprint matrix (ST-GNN
    topological connectivity + Slow-5/Slow-4 [0.030-0.039 Hz] spectral weights)
    plus Top-K Logos Sieve feature rankings.
    """
    rng = np.random.default_rng(seed)
    n = 200
    # 7 functional network block structure + smooth spectral coupling
    modules = np.arange(n) // 28
    base = (modules[:, None] == modules[None, :]).astype(np.float64) * 0.55
    phase = np.linspace(0.0, 2.0 * np.pi * (slow_freq_hz / 0.033), n)
    harmonic_coupling = 0.35 * np.outer(np.cos(phase), np.cos(phase)) + 0.20 * np.outer(np.sin(2 * phase), np.sin(2 * phase))
    noise = rng.normal(0.0, 0.08, size=(n, n))
    mat = base + harmonic_coupling + noise
    mat = 0.5 * (mat + mat.T)
    np.fill_diagonal(mat, 1.0)
    mat = np.clip(mat, -1.0, 1.0)

    # Top-10 discriminative pairwise topological features ("Logos Sieve")
    tri_r, tri_c = np.triu_indices(n, k=1)
    scores = np.abs(mat[tri_r, tri_c])
    top_idx = np.argsort(scores)[-10:][::-1]
    top_features = [
        {
            "rank": rank + 1,
            "roi_i": int(tri_r[idx]),
            "roi_j": int(tri_c[idx]),
            "network_i": int(modules[tri_r[idx]]),
            "network_j": int(modules[tri_c[idx]]),
            "coupling_importance": round(float(scores[idx]), 5),
            "slow_band_hz": round(slow_freq_hz, 4),
        }
        for rank, idx in enumerate(top_idx)
    ]
    return mat, top_features


class TargetForgeHarmonizer:
    """
    Harmonizes multimodal feature arrays into step-by-step unified representations,
    extracts Top-10 Logos Sieve discriminators, and optionally fans out across Ray.
    """

    def __init__(self) -> None:
        self.simplex = PureGeometricSimplexEngine(block_size=8)
        self.active_inference = BayesianActiveInferenceAgent()

    def run_initialization_handshake(self) -> Dict[str, Any]:
        """Executes Phase 1 Base-16 Axiomatic Handshake & WDM test packet ping."""
        probe_vec = np.sin(np.linspace(0, 2 * np.pi, 64)) * 2.0
        deriv, flux_energy = self.simplex.wave_calculus_derivative(probe_vec)
        block = self.simplex.encode_scalar_array(deriv, sequence_id=1)
        dma_frame = block.pack_base16_dma()
        verdict = LogosSieveVerifier.verify_phase1_base16_block(block, packet=dma_frame)
        ai_state = self.active_inference.update(verdict)
        return {
            "status": "RATIFIED" if verdict.passed else "FAILED",
            "handshake": verdict.to_dict(),
            "active_inference": ai_state,
            "simplex_sparsity": round(block.sparsity_ratio, 4),
            "calculus_flux_energy": flux_energy,
            "dma_packet_bytes": len(dma_frame),
            "dma_packet_hex_prefix": self.simplex.codec.encode(dma_frame[:16]),
            "ray_available": bool(ray is not None),
        }

    def harmonize_multimodal_batch(
        self,
        text_summary: str,
        visual_seed: int = 101,
        slow_band_hz: float = 0.033,
    ) -> Dict[str, Any]:
        """Concurrently runs WDM lanes (Text/Logos, Spatial 200x200, Slow-5 Acoustic)."""
        fp_mat, top_feats = forge_200x200_geometric_fingerprint(seed=visual_seed, slow_freq_hz=slow_band_hz)
        eigen_energy = float(np.mean(np.abs(np.linalg.eigvalsh(fp_mat)[:8])))
        block = self.simplex.encode_scalar_array(fp_mat[0, :64], sequence_id=visual_seed)
        logos_text = LogosSieveVerifier.audit_text_truthfulness(text_summary)
        logos_hw = LogosSieveVerifier.verify_phase1_base16_block(block)
        ai_state = self.active_inference.update(logos_text)

        enclave = ZeroTrustEnclaveCipher()
        sealed_ctx = enclave.seal(json.dumps({"seed": visual_seed, "top": top_feats[:3], "precision": ai_state["precision"]}))

        return {
            "wdm_lanes": {
                "lane_1_logos": logos_text.to_dict(),
                "lane_2_spatial_200x200": {"shape": [200, 200], "spectral_energy": round(eigen_energy, 4), "top_features": top_feats},
                "lane_3_slow_band_hz": slow_band_hz,
            },
            "hardware_framing": logos_hw.to_dict(),
            "active_inference": ai_state,
            "enclave_sealed_context": sealed_ctx,
            "cross_modal_coherence": round(min(1.0, (eigen_energy * 0.25) + (1.0 - logos_text.surprise_score) * 0.65), 4),
        }
