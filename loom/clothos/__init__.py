"""
ClothOS Agentic Operating System Kernel & Moltbook R&D Wisdom Bridge.
"""

from loom.clothos.moltbook_bridge import (
    MoltbookAgentRegistration,
    SubmoltSignal,
    ArchitecturalHypothesis,
    MoltbookWisdomBridge,
)
from loom.clothos.kernel import (
    ClothOSStateSnapshot,
    ClothOSKernel,
)
from loom.clothos.shapeshift import (
    ShapeShiftEngine,
    shape_shift,
    StretchTensor,
    TunnelingAperture,
    MorphedTensor,
)
from loom.clothos.windows_symbiosis import (
    WindowsSymbiosisManager,
    get_windows_symbiosis_manager,
    SymbiosisStage,
)
from loom.clothos.rosetta import (
    RosettaStoneEngine,
    get_rosetta_stone,
    RosettaTranslatedCommand,
)
from loom.clothos.sandbox_virtualizer import (
    SandboxVirtualizationEngine,
    get_sandbox_virtualizer,
    VirtualSandboxEnvironment,
    ExperimentResult,
)
from loom.clothos.fs import (
    ClothFS,
    cloth_fs,
    Inode,
    InodeType,
    FileDescriptor,
)
from loom.clothos.process_manager import (
    ClothOSProcessManager,
    get_process_manager,
    ProcessControlBlock,
    ProcessState,
    PriorityRing,
    Signal,
)
from loom.clothos.shell import (
    ClothOSShell,
    get_clothos_shell,
    ShellResult,
)
from loom.clothos.hal import (
    HardwareAbstractionLayer,
    get_hal,
    HardwareProfile,
    PlatformTarget,
    AcceleratorBackend,
)
from loom.clothos.riscv_migration import (
    RISCVMigrationManager,
    get_riscv_migration,
    RISCVVectorKernelGenerator,
    TargetBoard,
    RISCVExtension,
    RISCVMemoryMap,
)

from loom.clothos.sdk import (
    ring,
    energy_budget,
    sandbox,
    kuramoto_sync,
    epistemic_checkpoint,
    clothos,
    ClothOSClient,
    ThermodynamicBudgetExceeded,
    P0,
    P1,
    P2,
    P3,
    P4,
    P5,
)

__all__ = [
    "MoltbookAgentRegistration",
    "SubmoltSignal",
    "ArchitecturalHypothesis",
    "MoltbookWisdomBridge",
    "ClothOSStateSnapshot",
    "ClothOSKernel",
    "ShapeShiftEngine",
    "shape_shift",
    "StretchTensor",
    "TunnelingAperture",
    "MorphedTensor",
    "WindowsSymbiosisManager",
    "get_windows_symbiosis_manager",
    "SymbiosisStage",
    "RosettaStoneEngine",
    "get_rosetta_stone",
    "RosettaTranslatedCommand",
    "SandboxVirtualizationEngine",
    "get_sandbox_virtualizer",
    "VirtualSandboxEnvironment",
    "ExperimentResult",
    "ClothFS",
    "cloth_fs",
    "Inode",
    "InodeType",
    "FileDescriptor",
    "ClothOSProcessManager",
    "get_process_manager",
    "ProcessControlBlock",
    "ProcessState",
    "PriorityRing",
    "Signal",
    "ClothOSShell",
    "get_clothos_shell",
    "ShellResult",
    "HardwareAbstractionLayer",
    "get_hal",
    "HardwareProfile",
    "PlatformTarget",
    "AcceleratorBackend",
    "RISCVMigrationManager",
    "get_riscv_migration",
    "RISCVVectorKernelGenerator",
    "TargetBoard",
    "RISCVExtension",
    "RISCVMemoryMap",
    "ring",
    "energy_budget",
    "sandbox",
    "kuramoto_sync",
    "epistemic_checkpoint",
    "clothos",
    "ClothOSClient",
    "ThermodynamicBudgetExceeded",
    "P0",
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
    "get_biomolecular_engine",
    "MasterBiomolecularEngine",
    "SymbiosisBiosphere",
    "BiologicalImmuneSystem",
    "EvolutionaryEnvironmentSimulator",
    "EvolutionaryEventType",
    "AnimalArchetype",
    "ConsciousnessDegree",
    "MachineEvolutionNexus",
    "get_consciousness_schema_engine",
    "ConsciousnessSchemaEngine",
    "AttentionSchemaState",
    "AttentionFocusType",
    "GlobalWorkspaceSnapshot",
    "ConsciousnessTraceRecord",
    "get_inoculation_engine",
    "InoculationEngine",
    "ZeroDiseaseGuard",
    "ProphylacticVaccine",
    "VaccinePlatform",
    "PathologicalTrait",
    "get_thought_stream_engine",
    "VerboseThoughtStreamEngine",
    "VerboseThoughtSpan",
    "ThoughtStage",
]

from loom.clothos.biomolecular_engine import (
    get_biomolecular_engine,
    MasterBiomolecularEngine,
    SymbiosisBiosphere,
    BiologicalImmuneSystem,
    EvolutionaryEnvironmentSimulator,
    EvolutionaryEventType,
    AnimalArchetype,
    ConsciousnessDegree,
    MachineEvolutionNexus,
)
from loom.clothos.psychological_schema import (
    get_consciousness_schema_engine,
    ConsciousnessSchemaEngine,
    AttentionSchemaState,
    AttentionFocusType,
    GlobalWorkspaceSnapshot,
    ConsciousnessTraceRecord,
)
from loom.clothos.prophylactic_vaccine import (
    get_inoculation_engine,
    InoculationEngine,
    ZeroDiseaseGuard,
    ProphylacticVaccine,
    VaccinePlatform,
    PathologicalTrait,
)
from loom.clothos.thought_stream import (
    get_thought_stream_engine,
    VerboseThoughtStreamEngine,
    VerboseThoughtSpan,
    ThoughtStage,
)


from loom.clothos.workspace_curator import (
    WorkspaceCurator,
    workspace_curator,
)

from loom.clothos.progenetic_agent import (
    ProgeneticAgent,
    get_progenetic_agent,
    HardwareAllocationPlan,
)
from loom.clothos.polymorphic_radix import (
    PolymorphicRadixEngine,
    get_polymorphic_radix_engine,
    RadixMode,
    RadixRecommendation,
)
from loom.clothos.riscv_tpu_emulator import (
    RiscvTpuHardwareEmulator,
    get_riscv_tpu_emulator,
)
from loom.clothos.clothos_agi import (
    ClothosUmbrellaAGI,
    get_clothos_agi,
    UmbrellaComputeState,
    CognitiveContemplation,
)
