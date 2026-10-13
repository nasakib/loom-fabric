# Copyright (c) 2026 Najmos Sakib. All rights reserved.
# Proprietary and confidential. Commercial distribution prohibited.

import pytest
import numpy as np
from pathlib import Path

from loom.clothos.shapeshift import (
    ShapeShiftEngine,
    shape_shift,
    StretchTensor,
    TunnelingAperture,
    MorphedTensor,
)
from loom.clothos.kernel import ClothOSKernel


def test_shapeshift_continuum_stretch():
    engine = ShapeShiftEngine()
    
    # Apply tensile stretch along X, compress Z for volume preservation
    st = engine.apply_stretch(stretch_factors=(2.0, 1.0, 0.5), shear_modulus_mu=10.0)
    
    assert st.is_stretched is True
    assert st.principal_stretches == [2.0, 1.0, 0.5]
    assert st.volumetric_ratio_J == 1.0  # Incompressible (2.0 * 1.0 * 0.5 = 1.0)
    assert st.strain_energy_density_W > 0.0  # Neo-Hookean strain stored


def test_shapeshift_quantum_tunneling_barrier_thinning():
    engine = ShapeShiftEngine()

    # Original barrier (L = 3.0, V0 = 6.0, E = 5.0)
    # Under classical regime (L = 3.0, 2*kappa*L = 8.48), T_orig ≈ 0.0002
    # Stretch thins width from 3.0 down to 1.0 (2*kappa*L' = 2.83), T_thinned ≈ 0.059
    aperture = engine.tunnel_barrier(
        barrier_width_L=3.0,
        barrier_height_V0=6.0,
        particle_energy_E=5.0,
        stretch_multiplier=3.0,
    )

    assert aperture.original_barrier_width_L == 3.0
    assert aperture.thinned_barrier_width_L_prime == 1.0
    assert aperture.stretch_factor_lambda == 3.0
    assert aperture.tunneling_probability_T > 0.01
    assert aperture.quantum_tunnel_achieved is True


def test_shapeshift_morph_tensor_conservation():
    engine = ShapeShiftEngine()

    # 1D array of 4 elements morphed into 2x3 matrix (6 elements)
    original = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    morphed = engine.morph_tensor(original, target_shape=(2, 3))

    assert morphed.original_shape == [4]
    assert morphed.morphed_shape == [2, 3]
    assert morphed.conservation_invariant_preserved is True
    assert len(morphed.data_preview) == 5


def test_shapeshift_dag_elastic_dilatation():
    engine = ShapeShiftEngine()

    # High VRAM pressure test (9000 MB used out of 10000 MB total)
    res = engine.stretch_dag(
        critical_path_ms=25.0,
        vram_pressure_mb=9000.0,
        free_vram_mb=1000.0,
    )

    assert res["pressure_ratio"] == 0.90
    assert res["applied_stretch_lambda"] > 1.0
    assert res["stretched_path_ms"] > 25.0
    assert res["elastic_action"] == "OOM_PREVENTED_VIA_STRETCH"


def test_clothos_kernel_shapeshift_attachment():
    kernel = ClothOSKernel()
    assert hasattr(kernel, "shapeshift")
    assert kernel.shapeshift.secret_seal == "SHAPESHIFT-CLOTHOS-RV64-STRETCH-ALPHA"
