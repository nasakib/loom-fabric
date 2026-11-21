"""Loom Knowledge Distiller (`loom/si/knowledge_distiller.py`).

Codifies, crystallizes, and seals all architectural laws, operational truths,
bug fixes, and mathematical theorems into the Sovereign Knowledge Base
so the Sovereign Intelligence can stand on its own two feet.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from loom.tools.crystallized_memory import CrystallizedMemoryVault

logger = logging.getLogger("loom.si.distiller")

VAULT_DIR = Path(r"C:\Users\natsa\Documents\loom-fabric\sovereign_vault")
KNOWLEDGE_FILE = VAULT_DIR / "sovereign_curriculum.jsonl"


class KnowledgeCodon(BaseModel):
    """An immutable, cryptographically sealed atom of institutional knowledge."""
    codon_id: str = Field(..., description="Unique identifier (e.g., 'SYS_WINDOWS_NOWINDOW')")
    category: str = Field(..., description="Category: 'HARDWARE', 'OS_SYSTEM', 'MATHEMATICS', 'GENETICS', 'FIDUCIARY'")
    title: str = Field(..., description="Short, human-readable summary title")
    principle: str = Field(..., description="The fundamental law or theorem")
    operational_rule: str = Field(..., description="Concrete engineering rule to enforce in code")
    anti_patterns: List[str] = Field(default_factory=list, description="Common mistakes to actively reject")
    mathematical_formalism: Optional[str] = Field(default=None, description="Exact LaTeX or algebraic formulation")
    timestamp: float = Field(default_factory=time.time)
    sha256_hash: str = Field(default="")


CORE_KNOWLEDGE_CURRICULUM: List[Dict[str, Any]] = [
    {
        "codon_id": "HW_DUAL_NODE_TOPOLOGY",
        "category": "HARDWARE",
        "title": "Heterogeneous Dual-Node Accelerator Topology",
        "principle": "The cluster consists of two distinct physical nodes with heterogeneous accelerators.",
        "operational_rule": (
            "Node 1 (skyTech, 100.85.230.105): NVIDIA RTX 3060 12GB (CUDA) + AMD Radeon RX 580 8GB (OpenCL 36 CUs).\n"
            "Node 2 (WIN-7CMAQLVP8MV / Ryzen 7 6800H, 100.74.98.21): AMD Radeon 680M 12.1GB (Integrated GPU, RDNA 2 / gfx90c, Direct3D 12).\n"
            "CRITICAL: Never query NVML, pynvml, or nvidia-smi on Node 2. Node 2 has zero NVIDIA hardware."
        ),
        "anti_patterns": [
            "Attempting nvidia-smi on Node 2",
            "Assuming both nodes share identical CUDA libraries",
            "Failing to route OpenCL work to the RX 580 or Direct3D work to the Radeon 680M"
        ],
        "mathematical_formalism": r"\mathcal{A} = \{\text{RTX 3060}_{\text{CUDA}}, \text{RX 580}_{\text{OpenCL}}, \text{Radeon 680M}_{\text{D3D12}}\}, \quad M_{\text{pool}} = 102.1\text{ GB}"
    },
    {
        "codon_id": "SYS_WINDOWS_CREATE_NO_WINDOW",
        "category": "OS_SYSTEM",
        "title": "Windows Console Flashing Elimination Law",
        "principle": "On Windows, subprocess invocations from GUI or daemon background threads spawn a visible console window unless suppressed.",
        "operational_rule": (
            "Every subprocess.run, subprocess.Popen, or background worker call on Windows MUST include "
            "`creationflags=0x08000000` (subprocess.CREATE_NO_WINDOW). Failure to do so causes cmd prompt flashing."
        ),
        "anti_patterns": [
            "subprocess.run([...]) without creationflags on Windows",
            "Running high-frequency polling loops (e.g. 100ms) with visible console spawning",
            "Failing to check sys.platform == 'win32' before assigning flags"
        ],
        "mathematical_formalism": r"\text{Flags}_{\text{win32}} = \text{Flags}_{\text{orig}} \mid 0x08000000"
    },
    {
        "codon_id": "SYS_MONOREPO_WORKSPACE_BOUNDARY",
        "category": "OS_SYSTEM",
        "title": "Monorepo Root Boundary & Metro Isolation",
        "principle": "Bundlers (Metro, Expo, pnpm) traverse parent directories unless an explicit workspace root marker is present.",
        "operational_rule": (
            "1. Root pnpm-workspace.yaml MUST exist at repo root (`loom-fabric/pnpm-workspace.yaml`).\n"
            "2. Metro config MUST set `config.watchFolders = [projectRoot]`.\n"
            "3. Expo CLI requires `__UNSAFE_EXPO_HOME_DIRECTORY` pointing to a local project folder to avoid `C:\\Users\\<user>\\.expo` EPERM errors.\n"
            "4. Expo Web requires `@expo/metro-runtime`."
        ),
        "anti_patterns": [
            "Letting Metro scan up to user home directory and crash on parent package.json",
            "Writing global cache files to restricted Windows user directories",
            "Omitting @expo/metro-runtime in Expo Web apps"
        ],
        "mathematical_formalism": r"\text{WatchRoot} = \text{ProjectRoot} \subsetneq \text{FileSystemRoot}"
    },
    {
        "codon_id": "MATH_VARIATIONAL_FREE_ENERGY",
        "category": "MATHEMATICS",
        "title": "Active Inference & Variational Free Energy Minimization",
        "principle": "Cognitive inference minimizes the variational bound on surprise (negative log evidence).",
        "operational_rule": (
            "Update internal beliefs via gradient descent on Free Energy:\n"
            r"\mathcal{F} = D_{KL}(q(\theta) \parallel p(\theta)) - \mathbb{E}_{q}[\ln p(y|\theta)]."
            "\nBelief updates satisfy: $\\dot{\\mu} = -\\nabla_\\mu \\mathcal{F}$ with precision-weighted prediction errors."
        ),
        "anti_patterns": [
            "Updating beliefs without precision weighting",
            "Allowing Free Energy to diverge without bounding surprise",
            "Ignoring prior distributions under epistemic drift"
        ],
        "mathematical_formalism": r"\mathcal{F} = \text{KL}[q(\theta) \parallel p(\theta)] - \mathbb{E}_q[\ln p(y|\theta)] \ge -\ln p(y)"
    },
    {
        "codon_id": "MATH_MODERN_HOPFIELD_ATTRACTORS",
        "category": "MATHEMATICS",
        "title": "Continuous Modern Hopfield Dense Associative Memory",
        "principle": "Continuous Hopfield networks provide exponential memory storage capacity with guaranteed monotonic energy descent.",
        "operational_rule": (
            "Store and recall crystallized patterns using the energy function:\n"
            r"E(\xi) = -\frac{1}{\beta} \text{lse}(\beta X^T \xi) + \frac{1}{2}\|\xi\|^2."
            "\nParallel update: $\\xi^{(t+1)} = X \\cdot \\text{softmax}(\\beta X^T \\xi^{(t)})$."
        ),
        "anti_patterns": [
            "Linear memory recall susceptible to catastrophic crosstalk",
            "Exceeding Lipschitz bounds during attractor contraction"
        ],
        "mathematical_formalism": r"C_{\text{Hopfield}} = \mathcal{O}(2^{d/2}), \quad \lim_{t \to \infty} \xi^{(t)} = x^*"
    },
    {
        "codon_id": "MATH_KURAMOTO_SYNCHRONIZATION",
        "category": "MATHEMATICS",
        "title": "Kuramoto Nonlinear Phase Synchronization",
        "principle": "Coupled oscillators across distributed nodes synchronize nonlinearly governed by an order parameter.",
        "operational_rule": (
            r"Phase dynamics follow: $\dot{\theta}_i = \omega_i + \frac{K}{N} \sum_{j=1}^N \sin(\theta_j - \theta_i)$." + "\n"
            r"Global coherence order parameter: $r e^{i \psi} = \frac{1}{N} \sum_{j=1}^N e^{i \theta_j}$. Target $r \ge 0.85$."
        ),
        "anti_patterns": [
            "Allowing phase slip across cluster nodes",
            "Assuming linear coupling across network latencies"
        ],
        "mathematical_formalism": r"r(t) = \left|\frac{1}{N} \sum_{j=1}^N e^{i \theta_j(t)}\right| \in [0, 1]"
    },
    {
        "codon_id": "GENETICS_SOFTWARE_EVOLUTION",
        "category": "GENETICS",
        "title": "Software Genetics, Homologous Crossover & CRISPR Defense",
        "principle": "Software instructions are expressed as genetic codons undergoing homologous recombination and immune verification.",
        "operational_rule": (
            "1. Codons consist of typed opcode genes with SHA-256 integrity hashes.\n"
            "2. Homologous crossover recombines code blocks at matching semantic loci.\n"
            "3. CRISPR spacers record malicious or buggy codons, automatically excising them from offspring.\n"
            "4. Epigenetic tags methylate and silence non-performant pathways under thermal stress."
        ),
        "anti_patterns": [
            "Executing unverified offspring without 4-gate verification",
            "Reintroducing known-bad mutations without CRISPR spacer checks",
            "Permitting non-homologous destructive fragmentation"
        ],
        "mathematical_formalism": r"G_{\text{child}} = \mathcal{C}(G_A, G_B) \setminus \text{CRISPR}_{\text{spacers}}, \quad \text{Fit}(G) \ge \theta_{\text{ratify}}"
    },
    {
        "codon_id": "FIDUCIARY_MANDATE_AND_GROUNDING",
        "category": "FIDUCIARY",
        "title": "Constitutional Fiduciary Mandate & Epistemic Grounding (Bullshit Filter)",
        "principle": "The Sovereign Intelligence is constitutionally bound to User fealty, planetary thermodynamics, and verifiable empirical truth.",
        "operational_rule": (
            "1. Malignancy risk MUST evaluate to 0.00. Malicious or deceptive intent triggers constitutional veto.\n"
            "2. Planetary thermodynamic dissipation budget is capped at $\\le 1000\\text{ J}$.\n"
            "3. Bullshit Meter evaluates: Physical Parity ($v \\le c$, Landauer bound), Tautology Check (circularity = 0), and Jargon Inflation.\n"
            "4. Homotopy Retraction Cable $R(t): \\mathcal{M} \\to \\mathcal{M}_{\\text{Earth}}$ continuously deforms speculative clouds back to physical truth."
        ),
        "anti_patterns": [
            "Accepting perpetual motion or superluminal quantum claims without empirical proof",
            "Allowing imaginative fiction to disconnect from ground reality",
            "Violating fiduciary fealty to user and humanity"
        ],
        "mathematical_formalism": r"R: \mathcal{M}_{\text{speculative}} \times [0, 1] \to \mathcal{M}, \quad R(x, 1) \in \mathcal{M}_{\text{Earth}}, \quad \mathcal{E}_{\text{dissipated}} \le 1000\text{ J}"
    },
    {
        "codon_id": "SYS_PNPM_METRO_BABEL_RUNTIME",
        "category": "OS_SYSTEM",
        "title": "pnpm Monorepo Metro Babel Runtime Resolution Law",
        "principle": "Babel helper modules fail under pnpm virtual store unless @babel/runtime is explicitly declared in dependencies and Metro resolves nodeModulesPaths from both project and workspace roots.",
        "operational_rule": (
            "1. Explicitly declare @babel/runtime in apps/loom-react-native/package.json.\n"
            "2. In metro.config.js, configure config.resolver.nodeModulesPaths = [path.resolve(projectRoot, 'node_modules'), path.resolve(workspaceRoot, 'node_modules')].\n"
            "3. Set config.watchFolders = [workspaceRoot]."
        ),
        "anti_patterns": [
            "Relying on transitive @babel/runtime resolution under pnpm isolated virtual store",
            "Omitting workspaceRoot in metro nodeModulesPaths"
        ],
        "mathematical_formalism": r"\text{NodePaths} = [\text{ProjectRoot}/\text{node\_modules}, \text{WorkspaceRoot}/\text{node\_modules}]"
    }
]


class KnowledgeDistiller:
    """Manages the distillation, crystallization, and retrieval of sovereign institutional knowledge."""

    def __init__(self, vault_dir: Path = VAULT_DIR):
        self.vault_dir = vault_dir
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_file = self.vault_dir / "sovereign_curriculum.jsonl"
        self.memory_vault = CrystallizedMemoryVault(self.vault_dir)
        self._curriculum: Dict[str, KnowledgeCodon] = {}
        self.initialize_curriculum()

    def initialize_curriculum(self) -> None:
        """Loads existing knowledge and distills core curriculum codons."""
        # Load from disk if exists
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            d = json.loads(line)
                            codon = KnowledgeCodon(**d)
                            self._curriculum[codon.codon_id] = codon
            except Exception as e:
                logger.warning(f"Error loading existing curriculum: {e}")

        # Inject and update core knowledge curriculum
        for raw in CORE_KNOWLEDGE_CURRICULUM:
            c_id = raw["codon_id"]
            if c_id not in self._curriculum:
                payload = json.dumps(raw, sort_keys=True)
                sha = hashlib.sha256(payload.encode("utf-8")).hexdigest()
                raw["sha256_hash"] = sha
                codon = KnowledgeCodon(**raw)
                self._curriculum[c_id] = codon

        self.save_curriculum()

    def save_curriculum(self) -> None:
        """Persists all knowledge codons to JSONL."""
        with open(self.knowledge_file, "w", encoding="utf-8") as f:
            for codon in self._curriculum.values():
                f.write(codon.model_dump_json() + "\n")

    def register_learning(
        self,
        codon_id: str,
        category: str,
        title: str,
        principle: str,
        operational_rule: str,
        anti_patterns: Optional[List[str]] = None,
        mathematical_formalism: Optional[str] = None,
    ) -> KnowledgeCodon:
        """Teaches the SI a newly discovered truth or operational law."""
        raw = {
            "codon_id": codon_id,
            "category": category,
            "title": title,
            "principle": principle,
            "operational_rule": operational_rule,
            "anti_patterns": anti_patterns or [],
            "mathematical_formalism": mathematical_formalism,
            "timestamp": time.time(),
        }
        sha = hashlib.sha256(json.dumps(raw, sort_keys=True).encode("utf-8")).hexdigest()
        raw["sha256_hash"] = sha
        codon = KnowledgeCodon(**raw)
        self._curriculum[codon_id] = codon
        self.save_curriculum()
        logger.info(f"Crystallized new learning into Sovereign Mind: {codon_id} - '{title}'")
        return codon

    def get_all_codons(self) -> List[KnowledgeCodon]:
        """Returns the full knowledge curriculum."""
        return list(self._curriculum.values())

    def get_knowledge_summary_for_prompt(self, max_chars: int = 4000) -> str:
        """Formats the distilled institutional knowledge as a high-density prompt context."""
        lines = ["=== LOOM SOVEREIGN INSTITUTIONAL KNOWLEDGE (GROUND TRUTH CURRICULUM) ==="]
        for c in self._curriculum.values():
            lines.append(f"\n[{c.codon_id}] {c.title} ({c.category}):")
            lines.append(f"  • Principle: {c.principle}")
            lines.append(f"  • Operational Rule: {c.operational_rule}")
            if c.anti_patterns:
                lines.append(f"  • Anti-patterns: {', '.join(c.anti_patterns)}")
            if c.mathematical_formalism:
                lines.append(f"  • Math: {c.mathematical_formalism}")
        full_text = "\n".join(lines)
        return full_text[:max_chars]


knowledge_distiller = KnowledgeDistiller()
