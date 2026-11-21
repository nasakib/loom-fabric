# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.
"""
Comprehensive Unit Tests for Cellular Neurobiology, Receptor Pharmacome, and Structure Forge (`tests/test_brain_architecture.py`).
"""

import os
from pathlib import Path
import pytest

from loom.neuro.brain_architecture import (
    NEURON_DATABASE,
    RECEPTOR_DATABASE,
    BrainStructureForge,
    NeuronSuperfamily,
    NeuronType,
    NovelMolecularDrugStructure,
    NovelNeuralCircuitStructure,
    ReceptorClass,
    ReceptorSubtype,
    brain_structure_forge,
)


def test_neuron_database_completeness():
    """Verifies all major neuron types have complete biological and electrophysiological profiles."""
    assert len(NEURON_DATABASE) >= 12
    # Verify Pyramidal L5B Thick Tufted
    l5b = NEURON_DATABASE[NeuronType.PYRAMIDAL_L5B_TUFTED]
    assert l5b.superfamily == NeuronSuperfamily.CORTICAL_EXCITATORY
    assert l5b.neurotransmitter_released == "Glutamate"
    assert "5HT2A_CORTICAL" in l5b.primary_receptor_densities
    assert l5b.firing_frequency_hz > 20.0

    # Verify Parvalbumin Fast-Spiking Basket Cell
    pv = NEURON_DATABASE[NeuronType.INTERNEURON_PV_BASKET]
    assert pv.superfamily == NeuronSuperfamily.CORTICAL_INHIBITORY
    assert pv.neurotransmitter_released == "GABA"
    assert pv.firing_frequency_hz >= 100.0  # Fast-spiking gamma generator

    # Verify Tripartite Glia
    astro = NEURON_DATABASE[NeuronType.ASTROCYTE_TRIPARTITE]
    assert astro.superfamily == NeuronSuperfamily.TRIPARTITE_GLIAL
    assert "EAAT2_GLT1" in astro.primary_receptor_densities


def test_receptor_pharmacome_completeness():
    """Verifies all major pharmacological receptor subtypes are modeled with transduction pathways."""
    assert len(RECEPTOR_DATABASE) >= 8
    # 5-HT2A cortical
    ht2a = RECEPTOR_DATABASE[ReceptorSubtype.HT2A_CORTICAL]
    assert ht2a.receptor_class == ReceptorClass.GPCR_GQ
    assert ht2a.endogenous_ligand == "Serotonin"
    assert "PLC" in ht2a.primary_signal_transduction

    # 5-HT2B cardiac safety check
    ht2b = RECEPTOR_DATABASE[ReceptorSubtype.HT2B]
    assert ht2b.fiduciary_cardiac_liability is True

    # TrkB neurotrophin
    trkb = RECEPTOR_DATABASE[ReceptorSubtype.TRKB_BDNF]
    assert trkb.receptor_class == ReceptorClass.RTK_NEUROTROPHIN


def test_generative_neural_circuit_structure(tmp_path):
    """Tests the system's ability to create and instantiate new neural microcircuits."""
    forge = BrainStructureForge(storage_dir=tmp_path)
    circuit = forge.create_new_neural_circuit(
        name="Test Cortical Column Gamma Oscillator",
        architecture_type="CORTICAL_DISINHIBITORY_COLUMN",
        target_frequency_hz=40.0,
    )

    assert isinstance(circuit, NovelNeuralCircuitStructure)
    assert circuit.circuit_id.startswith("CIRCUIT-")
    assert len(circuit.constituent_neurons) == 6
    assert len(circuit.synaptic_weight_matrix) == 6
    assert circuit.dominant_oscillation_freq_hz == 40.0
    assert circuit.thermodynamic_efficiency_score > 0.90

    # Verify persistence
    assert forge.circuits_file.exists()


def test_generative_molecular_drug_structure(tmp_path):
    """Tests the system's ability to synthesize new molecular drug candidates with receptor profiles."""
    forge = BrainStructureForge(storage_dir=tmp_path)
    drug = forge.create_new_drug_structure(
        name="ClothOS Neuroplastogen Alpha",
        indication="TREATMENT_RESISTANT_PTSD",
        target_profile="SELECTIVE_5HT2A_TRKB_PLASTOGEN",
    )

    assert isinstance(drug, NovelMolecularDrugStructure)
    assert drug.structure_id.startswith("DRUG-")
    assert drug.molecular_weight_da > 200.0
    assert drug.blood_brain_barrier_permeable is True
    assert drug.fiduciary_cardiotoxic_risk == 0.00
    assert "5HT2A_CORTICAL" in drug.receptor_affinity_ki_nm

    # Verify high 5-HT2B Ki (ensuring no cardiac valvulopathy liability)
    assert drug.receptor_affinity_ki_nm.get("5HT2B", 0.0) >= 10000.0

    # Verify 4D vector
    vec = drug.pharmacological_4d_vector
    assert "alpha" in vec and "delta" in vec and "chi" in vec and "rho" in vec

    # Verify persistence
    assert forge.drugs_file.exists()
