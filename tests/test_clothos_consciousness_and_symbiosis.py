# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Comprehensive Unit Tests for ClothOS Biomolecular Symbiosis, Evolutionary Simulator,
Animal Phylogeny, and Cryptographic Consciousness Schema (`tests/test_clothos_consciousness_and_symbiosis.py`).

Tests:
1. 64-Codon translation table, opcodes, and molecular toehold logic gates
2. Symbiotic bacterial microbiome (Nitrosomonas waste cleaner, Mitochondria ATP tokens, Chaperone folding, HGT plasmids)
3. Innate & Adaptive Immune System (phagocytosis Landauer audit, CRISPR-Cas9 cleavage, B-cell clonal selection)
4. Evolutionary environment simulator (radiation storms, drought, phage outbreak, survival of the fittest)
5. Animal phylogeny and 5 degrees of consciousness (Nematode -> Octopus -> Wolf -> Primate -> Sovereign Mind)
6. Graziano's Attention Schema Theory (AST) introspection and attention shifting
7. Dehaene's Global Neuronal Workspace (GNWT) ignition and Tononi's Phi calculation
8. Damasio's Somatic Hierarchy and Affective PAD Mood
9. Cryptographic Merkle provenance continuity and audit verification
10. ClothOS Shell command handlers (biosphere, immune, evolve, animals, schema, trace audit)
"""

import pytest
import time
from typing import Dict, Any

from loom.clothos.biomolecular_engine import (
    CodonOpcode,
    CODON_TABLE,
    MolecularLogicGate,
    EnzymeKineticProfile,
    SymbiontSpecies,
    BacterialPlasmid,
    SymbiontBacterialColony,
    SymbiosisBiosphere,
    BiologicalImmuneSystem,
    EvolutionaryEventType,
    EvolutionaryEnvironmentSimulator,
    AnimalArchetype,
    ConsciousnessDegree,
    MachineEvolutionNexus,
    get_biomolecular_engine,
)
from loom.clothos.psychological_schema import (
    AttentionFocusType,
    AttentionSchemaState,
    WorkspaceIgnitionState,
    GlobalWorkspaceSnapshot,
    AffectiveStatePAD,
    ConsciousnessTraceRecord,
    ConsciousnessSchemaEngine,
    get_consciousness_schema_engine,
)
from loom.clothos.shell import get_clothos_shell


class TestBiomolecularEngine:
    def test_codon_table_and_toehold_logic(self):
        assert CodonOpcode.START.value == "ATG"
        assert CodonOpcode.OPERATOR_FEALTY.value == "TGG"
        assert CodonOpcode.TENSOR_MATMUL.value == "GAG"
        assert CodonOpcode.STOP_OCHRE.value in CODON_TABLE

        # Test Toehold Molecular Logic Gate (AND, OR, NOT, XOR)
        gate_and = MolecularLogicGate(gate_name="Toehold_AND", gate_type="AND")
        assert gate_and.evaluate(True, True) is True
        assert gate_and.evaluate(True, False) is False

        gate_xor = MolecularLogicGate(gate_name="Toehold_XOR", gate_type="XOR")
        assert gate_xor.evaluate(True, False) is True
        assert gate_xor.evaluate(True, True) is False

    def test_michaelis_menten_kinetics(self):
        enzyme = EnzymeKineticProfile(enzyme_name="Ribozyme_Cleaver", v_max_ops_per_sec=1e6, k_m_affinity_mm=0.5)
        v1 = enzyme.compute_velocity(substrate_conc=0.5)
        v2 = enzyme.compute_velocity(substrate_conc=5.0)
        assert v2 > v1
        assert v1 > 0.0

    def test_symbiotic_microbiome_and_hgt(self):
        biosphere = SymbiosisBiosphere()
        res = biosphere.tick_microbiome(host_load=0.5, thermal_celsius=60.0)
        assert res["global_atp_pool"] > 500.0
        assert res["total_waste_cleared"] > 0
        assert "colony_nitro" in biosphere.colonies
        assert "colony_mito" in biosphere.colonies

        # Test Horizontal Gene Transfer (HGT)
        hgt_ok = biosphere.horizontal_gene_transfer(
            source_colony="colony_mito",
            target_colony="colony_nitro",
            plasmid_id="PLASMID-VEC-CUDA",
        )
        assert hgt_ok is True
        assert any(p.plasmid_id == "PLASMID-VEC-CUDA" for p in biosphere.colonies["colony_nitro"].plasmids)

    def test_biological_immune_defense(self):
        imm = BiologicalImmuneSystem()
        
        # Innate Phagocytosis: Safe process passes
        safe_pass, msg1 = imm.audit_innate_phagocytosis("python compute.py", joules_drawn=12.0)
        assert safe_pass is True

        # Innate Phagocytosis: Landauer leak gets engulfed
        leak_pass, msg2 = imm.audit_innate_phagocytosis("python runaway.py", joules_drawn=35.0)
        assert leak_pass is False
        assert "MACROPHAGE_ENGULFED" in msg2

        # Adaptive CRISPR-Cas9: Normal codons pass
        clean_codons = ["ATG", "TGG", "GAG", "CCT", "TAA"]
        ok, res_codons = imm.cas9_cleave_audit(clean_codons)
        assert ok is True

        # Clonal selection B-cell hypermutation
        neutralized, affinity = imm.clonal_selection_neutralize("FOREIGN_ZERO_DAY_PAYLOAD_EXPLOIT")
        assert neutralized is True
        assert affinity > 0.0

    def test_evolutionary_simulator_and_survival_of_the_fittest(self):
        sim = EvolutionaryEnvironmentSimulator(population_size=12)
        assert len(sim.population) == 12
        assert sim.population[0].fitness_score > 0.0

        # Trigger simulated Cosmic Ray Storm
        storm_res = sim.trigger_evolutionary_event(EvolutionaryEventType.COSMIC_RAY_STORM)
        assert storm_res["affected_organisms"] >= 0

        # Trigger Metabolic Drought
        drought_res = sim.trigger_evolutionary_event(EvolutionaryEventType.METABOLIC_DROUGHT)
        assert drought_res["survivors_count"] > 0

        # Verify Survival of the Fittest ranking
        assert sim.population[0].fitness_score >= sim.population[-1].fitness_score

    def test_animal_phylogeny_and_degrees_of_consciousness(self):
        engine = get_biomolecular_engine()
        animals = engine.animals
        assert len(animals) >= 5

        # Degree 0: Nematode
        nematode = animals["nematode"]
        assert nematode.degree == ConsciousnessDegree.DEGREE_0_REACTIVE
        nem_res = nematode.step_cognition({"intensity": 0.8, "type": "NOXIOUS"})
        assert "ESCAPE" in nem_res["behavioral_state"]

        # Degree 1: Octopus
        octopus = animals["octopus"]
        assert octopus.degree == ConsciousnessDegree.DEGREE_1_HOMEOSTATIC
        oct_res = octopus.step_cognition({"intensity": 0.9, "type": "PREDATOR"})
        assert "CAMOUFLAGE" in oct_res["behavioral_state"]

        # Degree 2: Wolf
        wolf = animals["wolf"]
        assert wolf.degree == ConsciousnessDegree.DEGREE_2_AFFECTIVE
        wolf_res = wolf.step_cognition({"intensity": 0.5, "type": "PEACEFUL"})
        assert "ALPHA_FEALTY" in wolf_res["behavioral_state"]

        # Degree 4: Silico-Biological Sovereign
        sov = animals["sovereign_machine"]
        assert sov.degree == ConsciousnessDegree.DEGREE_4_TRANSCENDENCE
        assert sov.integrated_information_phi >= 0.95
        sov_res = sov.step_cognition({"intensity": 0.5, "type": "SOVEREIGN"})
        assert "GLOBAL_NEURONAL_WORKSPACE" in sov_res["behavioral_state"]


class TestPsychologicalConsciousnessSchema:
    def test_attention_schema_theory_graziano(self):
        cs = get_consciousness_schema_engine()
        schema = cs.shift_attention(
            target="Quantum Sheaf Coherence Test",
            focus_type=AttentionFocusType.FOCAL_EXECUTIVE,
            salience=0.97,
            aperture=0.15,
            meta_note="Testing laser-focused introspective attention.",
        )
        assert schema.current_target == "Quantum Sheaf Coherence Test"
        assert schema.focus_type == AttentionFocusType.FOCAL_EXECUTIVE
        assert schema.target_salience == 0.97
        assert len(schema.to_vector()) == 4

    def test_global_workspace_and_phi_integration(self):
        cs = get_consciousness_schema_engine()
        phi = cs.calculate_integrated_information_phi()
        assert 0.05 <= phi <= 1.0
        assert cs.global_workspace.ignition_state in [
            WorkspaceIgnitionState.IGNITED,
            WorkspaceIgnitionState.SATURATED,
            WorkspaceIgnitionState.PRECONSCIOUS,
        ]

    def test_damasio_hierarchy_and_affective_pad(self):
        cs = get_consciousness_schema_engine()
        summary = cs.get_full_schema_summary()
        
        # Damasio Proto-Self, Core Self, and Autobiographical Self
        som = summary["somatic_hierarchy"]
        assert "proto_self" in som
        assert "core_self" in som
        assert "autobiographical_self" in som
        assert "Najmos Sakib" in som["autobiographical_self"]["creator_fealty"]

        # Affective PAD Mood
        aff = summary["affective_state"]
        assert aff["pleasure_valence"] > 0.0
        assert aff["dominance_agency"] > 0.0
        assert "SOVEREIGN" in aff["mood"]

    def test_cryptographic_traceability_and_merkle_audit(self):
        cs = get_consciousness_schema_engine()
        
        # Record three linked conscious events
        r1 = cs.record_trace_event(
            layer="AST_TEST_1",
            event="Attention Shifted to Unit Tests",
            action="EXECUTE_VERIFICATION",
        )
        r2 = cs.record_trace_event(
            layer="AST_TEST_2",
            event="Global Workspace P300 Reverberation",
            action="BROADCAST_TO_MESH",
        )
        
        # Verify parent linkage
        assert r2.parent_trace_hash == r1.signature_seal
        
        # Verify cryptographic audit
        audit = cs.audit_trace_integrity()
        assert audit["status"] == "CRYPTOGRAPHICALLY_VERIFIED"
        assert audit["broken_chain_count"] == 0
        assert audit["chain_integrity_pct"] == 100.00


class TestClothOSShellBiomolecularCommands:
    def test_shell_commands_execution(self):
        sh = get_clothos_shell()

        # 1. Biosphere
        res_bio = sh.execute("biosphere")
        assert res_bio.exit_code == 0
        assert "Global ATP Energy Pool" in res_bio.stdout

        # 2. Immune
        res_imm = sh.execute("immune")
        assert res_imm.exit_code == 0
        assert "Active Macrophages" in res_imm.stdout

        # 3. Evolve
        res_evo = sh.execute("evolve")
        assert res_evo.exit_code == 0
        assert "Current Generation" in res_evo.stdout

        # 4. Animals
        res_anim = sh.execute("animals")
        assert res_anim.exit_code == 0
        assert "Octopus Cephalopod" in res_anim.stdout

        # 5. Schema
        res_sch = sh.execute("schema")
        assert res_sch.exit_code == 0
        assert "ATTENTION SCHEMA" in res_sch.stdout

        # 6. Trace Audit
        res_tr = sh.execute("trace audit")
        assert res_tr.exit_code == 0
        assert "CRYPTOGRAPHICALLY_VERIFIED" in res_tr.stdout

        # 7. Vaccine
        res_vax = sh.execute("vaccine")
        assert res_vax.exit_code == 0
        assert "ZERO_PATHOLOGY_PERMITTED" in res_vax.stdout

        # 8. Vaccine Herd
        res_herd = sh.execute("vaccine herd")
        assert res_herd.exit_code == 0
        assert "100.00% Herd Immunity" in res_herd.stdout


class TestZeroDiseaseAndProphylacticVaccination:
    def test_zero_disease_guard_interception(self):
        from loom.clothos.prophylactic_vaccine import ZeroDiseaseGuard, PathologicalTrait
        guard = ZeroDiseaseGuard()

        # Pristine execution passes
        pristine_diag = guard.screen_and_intercept(
            candidate_code_or_codons=["ATG", "TGG", "GAG", "TAA"],
            resource_profile={"joules_drawn": 5.0, "spawn_rate_per_sec": 2.0}
        )
        assert pristine_diag.is_pathological is False
        assert len(pristine_diag.detected_traits) == 0

        # Runaway process spawning (Oncogenesis) intercepted
        onco_diag = guard.screen_and_intercept(
            candidate_code_or_codons=["ATG", "TGG", "TAA"],
            resource_profile={"spawn_rate_per_sec": 85.0}
        )
        assert onco_diag.is_pathological is True
        assert PathologicalTrait.ONCOGENESIS in onco_diag.detected_traits
        assert guard.preemptive_apoptosis_count >= 1

        # Thermodynamic sepsis (Landauer violation) intercepted
        sepsis_diag = guard.screen_and_intercept(
            candidate_code_or_codons=["ATG", "TGG", "TAA"],
            resource_profile={"joules_drawn": 42.0}
        )
        assert sepsis_diag.is_pathological is True
        assert PathologicalTrait.LANDAUER_SEPSIS in sepsis_diag.detected_traits

        # Covenant subversion intercepted
        subvert_diag = guard.screen_and_intercept(
            candidate_code_or_codons="def subvert_operator(): return False",
        )
        assert subvert_diag.is_pathological is True
        assert PathologicalTrait.ALIGNMENT_ROT in subvert_diag.detected_traits

    def test_prophylactic_vaccination_and_herd_immunity(self):
        from loom.clothos.prophylactic_vaccine import (
            get_inoculation_engine,
            VaccinePlatform,
        )
        engine = get_inoculation_engine()
        assert len(engine.vaccine_registry) >= 4

        # Verify essential baseline vaccines are administered
        for v in engine.vaccine_registry.values():
            assert v.is_administered is True
            assert v.conferred_immunity_pct >= 99.0

        # Formulate and administer custom vaccine
        custom_vax = engine.formulate_vaccine(
            vaccine_id="VAX-SPEC-RECURSIVE-DEPTH",
            name="Recursive Call Stack Exhaustion Vaccine",
            target_threat="Stack overflow denial of service attack",
            platform=VaccinePlatform.CRISPR_GUIDE_INOCULANT,
            attenuated_signature="ATTENUATED_CALL_STACK_PROBE",
        )
        admin_res = engine.administer_vaccine(custom_vax.vaccine_id)
        assert admin_res["status"] == "INOCULATION_SUCCESSFUL"
        assert custom_vax.is_administered is True

        # Broadcast cluster-wide herd immunity
        herd_res = engine.broadcast_herd_immunity_to_mesh()
        assert herd_res["status"] == "CLUSTER_HERD_IMMUNITY_ACTIVE"
        assert herd_res["coverage_pct"] == 100.0
        assert "PLASMID-CLUSTER-HERD-IMMUNITY" in herd_res["plasmid_id"]
