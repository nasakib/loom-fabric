# Copyright (c) 2026 Najmos Sakib / VectorCore Holdings, LLC.
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
ClothOS Unified Sovereign Nexus (`loom/unified_nexus.py`).
==========================================================
Single unified coordination layer across the VectorCore / ClothOS / Loom Fabric
ecosystem, bridging:
  1. Constitutional, Fiduciary & Adversarial Deceit Immune Gate
     (FiduciaryMandateGuard + EpistemicRigorGauge + SovereignJudge + Gnome-Sentinel Deceit)
  2. Formal SMT & Neuro-Topological Verification
     (fouriersLibrary Z3 / Active Inference + babelForge Betti / Kuramoto + babelForgePreview)
  3. Typemetric Spectral & Dozenal Base-12 Harmonic Engine
     (C99-isomorphic Dozenal Kuramoto sync, Gonzalez k-center diversity pruning, FWHT)
  4. Bare-Metal Native JIT Execution
     (universal-jit x86-64 VirtualAlloc/mmap kernels + MiniVM probe)
  5. Verified Multi-Trajectory Test-Time Compute
     (PrimarySuperintelligenceKernel + ClothosUmbrellaAGI + PolymorphicRadix + ProgeneticAgent)
  6. Unified Ecosystem Service Mesh & Torque Zero-Trust Scrubbing
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import httpx
import numpy as np

LOOM_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_ROOT = LOOM_ROOT.parent
if str(LOOM_ROOT) not in sys.path:
    sys.path.insert(0, str(LOOM_ROOT))

from loom.clothos.clothos_agi import get_clothos_agi
from loom.clothos.ujit_engine import clothos_jit
from loom.governance.ring_p0 import RingP0GovernanceController
from loom.si.sovereign_judge import get_sovereign_judge
from loom.si.superintelligence_kernel import superintelligence_kernel
from loom.tools.epistemic_grounding import EpistemicRigorGauge
from loom.tools.fiduciary_guard import FiduciaryMandateGuard
from loom.tools.ratchet import RatchetEngine
from loom.torque.scrubber import RehydrationVault, TorqueScrubber
from servers.babelforge_mcp.algorithms import (
    optimize_clothos_schedule,
    simulate_subgraph_execution,
    validate_graph_invariants,
)

logger = logging.getLogger("loom.unified_nexus")


# ============================================================================
# 1. TYPEMETRIC C99-ISOMORPHIC DOZENAL HARMONIC, GONZALEZ & WHT ENGINE
# ============================================================================

TM_DOZENAL_FULL_CIRCLE = 3072
TM_DOZENAL_HALF_CIRCLE = 1536
TM_DOZENAL_THIRD_CIRCLE = 1024
TM_DOZENAL_QUARTER = 768
TM_DOZENAL_SIXTH = 512
TM_DOZENAL_TWELFTH = 256
TM_DOZENAL_Q12_ONE = 1728
TM_DOZENAL_Q12_DENOM_SQ = 2985984

# Bit-for-bit identical to typemetric-jit/core/src/harmonic.c and vector-forge/src/lib/dozenalReflex.ts
TM_DOZENAL_SIN_QUARTER_LUT: Tuple[int, ...] = (
       0,    4,    7,   11,   14,   18,   21,   25,   28,   32,   35,   39,   42,   46,   49,   53,
      57,   60,   64,   67,   71,   74,   78,   81,   85,   88,   92,   95,   99,  102,  106,  109,
     113,  117,  120,  124,  127,  131,  134,  138,  141,  145,  148,  152,  155,  159,  162,  166,
     169,  173,  176,  180,  183,  187,  190,  194,  197,  201,  205,  208,  212,  215,  219,  222,
     226,  229,  233,  236,  240,  243,  247,  250,  254,  257,  261,  264,  268,  271,  275,  278,
     281,  285,  288,  292,  295,  299,  302,  306,  309,  313,  316,  320,  323,  327,  330,  334,
     337,  341,  344,  348,  351,  354,  358,  361,  365,  368,  372,  375,  379,  382,  386,  389,
     392,  396,  399,  403,  406,  410,  413,  416,  420,  423,  427,  430,  434,  437,  440,  444,
     447,  451,  454,  457,  461,  464,  468,  471,  474,  478,  481,  485,  488,  491,  495,  498,
     502,  505,  508,  512,  515,  518,  522,  525,  529,  532,  535,  539,  542,  545,  549,  552,
     555,  559,  562,  565,  569,  572,  575,  579,  582,  585,  589,  592,  595,  599,  602,  605,
     609,  612,  615,  619,  622,  625,  628,  632,  635,  638,  642,  645,  648,  651,  655,  658,
     661,  665,  668,  671,  674,  678,  681,  684,  687,  691,  694,  697,  700,  703,  707,  710,
     713,  716,  720,  723,  726,  729,  732,  736,  739,  742,  745,  748,  752,  755,  758,  761,
     764,  767,  771,  774,  777,  780,  783,  786,  790,  793,  796,  799,  802,  805,  808,  811,
     815,  818,  821,  824,  827,  830,  833,  836,  839,  842,  846,  849,  852,  855,  858,  861,
     864,  867,  870,  873,  876,  879,  882,  885,  888,  891,  894,  897,  900,  903,  906,  909,
     913,  916,  918,  921,  924,  927,  930,  933,  936,  939,  942,  945,  948,  951,  954,  957,
     960,  963,  966,  969,  972,  975,  978,  980,  983,  986,  989,  992,  995,  998, 1001, 1004,
    1007, 1009, 1012, 1015, 1018, 1021, 1024, 1027, 1029, 1032, 1035, 1038, 1041, 1044, 1046, 1049,
    1052, 1055, 1058, 1060, 1063, 1066, 1069, 1071, 1074, 1077, 1080, 1083, 1085, 1088, 1091, 1093,
    1096, 1099, 1102, 1104, 1107, 1110, 1113, 1115, 1118, 1121, 1123, 1126, 1129, 1131, 1134, 1137,
    1139, 1142, 1145, 1147, 1150, 1153, 1155, 1158, 1160, 1163, 1166, 1168, 1171, 1173, 1176, 1179,
    1181, 1184, 1186, 1189, 1192, 1194, 1197, 1199, 1202, 1204, 1207, 1209, 1212, 1214, 1217, 1219,
    1222, 1224, 1227, 1229, 1232, 1234, 1237, 1239, 1242, 1244, 1247, 1249, 1251, 1254, 1256, 1259,
    1261, 1264, 1266, 1268, 1271, 1273, 1276, 1278, 1280, 1283, 1285, 1287, 1290, 1292, 1295, 1297,
    1299, 1302, 1304, 1306, 1308, 1311, 1313, 1315, 1318, 1320, 1322, 1324, 1327, 1329, 1331, 1334,
    1336, 1338, 1340, 1342, 1345, 1347, 1349, 1351, 1354, 1356, 1358, 1360, 1362, 1364, 1367, 1369,
    1371, 1373, 1375, 1377, 1379, 1382, 1384, 1386, 1388, 1390, 1392, 1394, 1396, 1398, 1400, 1403,
    1405, 1407, 1409, 1411, 1413, 1415, 1417, 1419, 1421, 1423, 1425, 1427, 1429, 1431, 1433, 1435,
    1437, 1439, 1441, 1443, 1445, 1447, 1448, 1450, 1452, 1454, 1456, 1458, 1460, 1462, 1464, 1466,
    1467, 1469, 1471, 1473, 1475, 1477, 1479, 1480, 1482, 1484, 1486, 1488, 1489, 1491, 1493, 1495,
    1496, 1498, 1500, 1502, 1504, 1505, 1507, 1509, 1510, 1512, 1514, 1516, 1517, 1519, 1521, 1522,
    1524, 1526, 1527, 1529, 1531, 1532, 1534, 1535, 1537, 1539, 1540, 1542, 1543, 1545, 1547, 1548,
    1550, 1551, 1553, 1554, 1556, 1558, 1559, 1561, 1562, 1564, 1565, 1567, 1568, 1570, 1571, 1573,
    1574, 1575, 1577, 1578, 1580, 1581, 1583, 1584, 1585, 1587, 1588, 1590, 1591, 1592, 1594, 1595,
    1596, 1598, 1599, 1600, 1602, 1603, 1604, 1606, 1607, 1608, 1610, 1611, 1612, 1613, 1615, 1616,
    1617, 1618, 1620, 1621, 1622, 1623, 1625, 1626, 1627, 1628, 1629, 1631, 1632, 1633, 1634, 1635,
    1636, 1637, 1639, 1640, 1641, 1642, 1643, 1644, 1645, 1646, 1647, 1648, 1649, 1650, 1652, 1653,
    1654, 1655, 1656, 1657, 1658, 1659, 1660, 1661, 1662, 1663, 1664, 1664, 1665, 1666, 1667, 1668,
    1669, 1670, 1671, 1672, 1673, 1674, 1674, 1675, 1676, 1677, 1678, 1679, 1680, 1680, 1681, 1682,
    1683, 1684, 1684, 1685, 1686, 1687, 1688, 1688, 1689, 1690, 1691, 1691, 1692, 1693, 1693, 1694,
    1695, 1695, 1696, 1697, 1697, 1698, 1699, 1699, 1700, 1701, 1701, 1702, 1703, 1703, 1704, 1704,
    1705, 1705, 1706, 1707, 1707, 1708, 1708, 1709, 1709, 1710, 1710, 1711, 1711, 1712, 1712, 1713,
    1713, 1714, 1714, 1715, 1715, 1715, 1716, 1716, 1717, 1717, 1717, 1718, 1718, 1719, 1719, 1719,
    1720, 1720, 1720, 1721, 1721, 1721, 1722, 1722, 1722, 1723, 1723, 1723, 1723, 1724, 1724, 1724,
    1724, 1725, 1725, 1725, 1725, 1725, 1726, 1726, 1726, 1726, 1726, 1726, 1727, 1727, 1727, 1727,
    1727, 1727, 1727, 1727, 1727, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728, 1728,
    1728,
)


def tm_integer_sqrt(x: int) -> int:
    """Pure integer floor(sqrt(x)), bit-for-bit isomorphic to harmonic.c."""
    if x <= 0:
        return 0
    rem = int(x)
    res = 0
    bit = 1 << 62
    while bit > rem:
        bit >>= 2
    while bit != 0:
        if rem >= res + bit:
            rem -= res + bit
            res = (res >> 1) + bit
        else:
            res >>= 1
        bit >>= 2
    return res


def tm_dozenal_sin_q12(phase: int) -> int:
    """Pure integer Base-12 sine in Q12 [-1728, +1728]."""
    p = int(phase) % TM_DOZENAL_FULL_CIRCLE
    if p < TM_DOZENAL_QUARTER:
        return TM_DOZENAL_SIN_QUARTER_LUT[p]
    if p < TM_DOZENAL_HALF_CIRCLE:
        return TM_DOZENAL_SIN_QUARTER_LUT[TM_DOZENAL_HALF_CIRCLE - p]
    if p < TM_DOZENAL_HALF_CIRCLE + TM_DOZENAL_QUARTER:
        return -TM_DOZENAL_SIN_QUARTER_LUT[p - TM_DOZENAL_HALF_CIRCLE]
    return -TM_DOZENAL_SIN_QUARTER_LUT[TM_DOZENAL_FULL_CIRCLE - p]


def tm_dozenal_cos_q12(phase: int) -> int:
    """Pure integer Base-12 cosine in Q12 [-1728, +1728]."""
    return tm_dozenal_sin_q12((int(phase) + TM_DOZENAL_QUARTER) % TM_DOZENAL_FULL_CIRCLE)


def tm_dozenal_atan2(y: int, x: int) -> int:
    """Pure integer arctangent resolving (y, x) onto [0, 3071]."""
    if x == 0 and y == 0:
        return 0
    ax = abs(int(x))
    ay = abs(int(y))
    r = tm_integer_sqrt(ax * ax + ay * ay)
    if r == 0:
        return 0
    target_sin = (ay * TM_DOZENAL_Q12_ONE) // r
    lo, hi = 0, TM_DOZENAL_QUARTER
    while lo < hi:
        mid = (lo + hi) >> 1
        if TM_DOZENAL_SIN_QUARTER_LUT[mid] < target_sin:
            lo = mid + 1
        else:
            hi = mid
    base = lo
    if x >= 0 and y >= 0:
        return base
    if x < 0 and y >= 0:
        return TM_DOZENAL_HALF_CIRCLE - base
    if x < 0 and y < 0:
        return TM_DOZENAL_HALF_CIRCLE + base
    return (TM_DOZENAL_FULL_CIRCLE - base) % TM_DOZENAL_FULL_CIRCLE


def tm_dozenal_phase_distance(a: int, b: int) -> int:
    """Shortest modular geodesic distance on the 3072-unit Base-12 circle."""
    pa = int(a) % TM_DOZENAL_FULL_CIRCLE
    pb = int(b) % TM_DOZENAL_FULL_CIRCLE
    diff = abs(pa - pb)
    return TM_DOZENAL_FULL_CIRCLE - diff if diff > TM_DOZENAL_HALF_CIRCLE else diff


def tm_dozenal_kuramoto_step_batch(
    phases_in: Sequence[int],
    omegas: Sequence[int],
    trit_polarities: Sequence[int],
    precision_weights_q12: Sequence[int],
    coupling_k: int,
) -> Dict[str, Any]:
    """
    Executes a single precision-weighted Base-12 integer Kuramoto batch step
    isomorphic to `typemetric-jit/core/src/harmonic.c::tm_dozenal_kuramoto_step_batch`.
    """
    n = min(16, len(phases_in), len(omegas), len(trit_polarities), len(precision_weights_q12))
    if n == 0:
        return {
            "next_phases": [],
            "coherence_q12": 0,
            "weighted_coherence_q12": 0,
            "mean_phase": 0,
            "max_phase_spread": 0,
            "locked_count": 0,
        }

    active_count = sum(1 for i in range(n) if int(trit_polarities[i]) != 0)
    phases_out: List[int] = [0] * n

    for i in range(n):
        pi = int(phases_in[i]) % TM_DOZENAL_FULL_CIRCLE
        trit_i = int(trit_polarities[i])
        if trit_i == 0:
            phases_out[i] = pi
            continue

        weighted_sin_sum = 0
        if active_count > 1 and coupling_k > 0:
            for j in range(n):
                if j == i or int(trit_polarities[j]) == 0:
                    continue
                pj = int(phases_in[j]) % TM_DOZENAL_FULL_CIRCLE
                delta = (pj + TM_DOZENAL_FULL_CIRCLE - pi) % TM_DOZENAL_FULL_CIRCLE
                weighted_sin_sum += int(precision_weights_q12[j]) * tm_dozenal_sin_q12(delta)

        pull = 0
        if active_count > 1 and coupling_k > 0 and weighted_sin_sum != 0:
            denom = (active_count - 1) * TM_DOZENAL_Q12_DENOM_SQ
            raw_num = int(coupling_k) * weighted_sin_sum
            if raw_num > 0:
                pull = (raw_num + (denom >> 1)) // denom
            else:
                # Match C truncating division toward zero
                pull = -((abs(raw_num) + (denom >> 1)) // denom)

        signed_omega = int(omegas[i]) * trit_i
        phases_out[i] = (pi + signed_omega + pull) % TM_DOZENAL_FULL_CIRCLE

    ux = uy = wx = wy = total_weight = 0
    for i in range(n):
        if int(trit_polarities[i]) == 0:
            continue
        cx = tm_dozenal_cos_q12(phases_out[i])
        sy = tm_dozenal_sin_q12(phases_out[i])
        w = int(precision_weights_q12[i])
        ux += cx
        uy += sy
        wx += w * cx
        wy += w * sy
        total_weight += w

    coh_q12 = 0
    if active_count > 0:
        r_val = tm_integer_sqrt((ux * ux + uy * uy) // (active_count * active_count))
        coh_q12 = min(TM_DOZENAL_Q12_ONE, r_val)

    wcoh_q12 = coh_q12
    mean_p = 0
    if total_weight > 0:
        mx = int(wx / total_weight)
        my = int(wy / total_weight)
        wr = tm_integer_sqrt(mx * mx + my * my)
        wcoh_q12 = min(TM_DOZENAL_Q12_ONE, wr)
        mean_p = tm_dozenal_atan2(wy, wx)
    elif active_count > 0:
        mean_p = tm_dozenal_atan2(uy, ux)

    max_spread = 0
    locked = 0
    for i in range(n):
        if int(trit_polarities[i]) == 0:
            continue
        if tm_dozenal_phase_distance(phases_out[i], mean_p) <= 12:
            locked += 1
        for j in range(i + 1, n):
            if int(trit_polarities[j]) == 0:
                continue
            d = tm_dozenal_phase_distance(phases_out[i], phases_out[j])
            if d > max_spread:
                max_spread = d

    return {
        "next_phases": phases_out,
        "coherence_q12": coh_q12,
        "weighted_coherence_q12": wcoh_q12,
        "coherence_float": round(coh_q12 / float(TM_DOZENAL_Q12_ONE), 4),
        "mean_phase": mean_p,
        "max_phase_spread": max_spread,
        "locked_count": locked,
    }


def _default_metric_matrix() -> List[List[int]]:
    """Builds the hierarchical metric distance table matching metric_space.c."""
    mat = [[0 if i == j else 4 for j in range(32)] for i in range(32)]
    mat[2][3] = mat[3][2] = 1
    for p in (2, 3):
        mat[1][p] = mat[p][1] = 2
    for p in (1, 2, 3):
        mat[0][p] = mat[p][0] = 2
    for h in range(4, 9):
        mat[0][h] = mat[h][0] = 3
    for i in range(4, 9):
        for j in range(4, 9):
            if i != j:
                mat[i][j] = 2
        for p in (1, 2, 3):
            mat[p][i] = mat[i][p] = 4
    return mat


_TM_METRIC_MATRIX = _default_metric_matrix()
_TM_PARAM_WEIGHTS = [1000 - i * 50 for i in range(8)]


def tm_vector_distance(kinds_a: Sequence[int], kinds_b: Sequence[int]) -> int:
    """Metric distance d(A, B) isomorphic to `metric_space.c::tm_vector_distance`."""
    arity_a = min(8, len(kinds_a))
    arity_b = min(8, len(kinds_b))
    if arity_a == arity_b and tuple(kinds_a[:arity_a]) == tuple(kinds_b[:arity_b]):
        return 0
    max_arity = max(arity_a, arity_b)
    total = 0
    for i in range(max_arity):
        ka = int(kinds_a[i]) if i < arity_a else 0
        kb = int(kinds_b[i]) if i < arity_b else 0
        if ka < 32 and kb < 32:
            d = _TM_METRIC_MATRIX[ka][kb]
        else:
            d = 0 if ka == kb else 4
        total += d * _TM_PARAM_WEIGHTS[i]
    if arity_a != arity_b:
        total += abs(arity_a - arity_b) * 2000
    return total


def tm_gonzalez_select(
    candidates: Sequence[Sequence[int]],
    k: int,
    primary_idx: int = 0,
) -> List[int]:
    """
    Gonzalez Farthest-Point Sampling (`gonzalez.c::tm_gonzalez_select`).
    Factor-2 optimal metric k-center diversity selection without LRU thrashing.
    """
    n = len(candidates)
    if n == 0 or k <= 0:
        return []
    if k >= n:
        return list(range(n))

    c0 = primary_idx if 0 <= primary_idx < n else 0
    selected = [c0]
    min_dist = [tm_vector_distance(candidates[i], candidates[c0]) for i in range(n)]

    for _ in range(1, k):
        best_idx = 0
        max_d = -1
        for i in range(n):
            if min_dist[i] > max_d:
                max_d = min_dist[i]
                best_idx = i
        selected.append(best_idx)
        for i in range(n):
            d = tm_vector_distance(candidates[i], candidates[best_idx])
            if d < min_dist[i]:
                min_dist[i] = d
    return selected


def _turn_to_metric_kinds(msg: Dict[str, Any]) -> List[int]:
    """Maps a conversation message into an 8-byte discrete metric type vector."""
    role = str(msg.get("role", "user")).lower()
    role_id = {"system": 1, "user": 2, "assistant": 3, "tool": 4}.get(role, 5)
    content = str(msg.get("content", ""))
    has_code = 6 if ("```" in content or "def " in content or "fn " in content) else 2
    has_tool = 8 if (msg.get("tool_calls") or msg.get("tool_call_id") or "tool_use" in content) else 1
    has_math = 3 if any(w in content.lower() for w in ("z3", "theorem", "kuramoto", "fourier", "matrix")) else 1
    len_bucket = min(8, max(1, len(content) // 250))
    sig = int(hashlib.sha256(content[:512].encode("utf-8", errors="ignore")).hexdigest()[:4], 16)
    return [role_id, has_code, has_tool, has_math, len_bucket, sig % 9, (sig >> 4) % 9, (sig >> 8) % 9]


_ROLLING_MEMORY_MARKER = "[ROLLING_TRAJECTORY_MEMORY]"


def _message_text(msg: Dict[str, Any]) -> str:
    content = msg.get("content", "")
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(str(block.get("text") or block.get("thinking") or ""))
            else:
                parts.append(str(block))
        return " ".join(p for p in parts if p).strip()
    return str(content or "").strip()


def _summarize_dropped_messages(
    messages: List[Dict[str, Any]],
    dropped_indices: List[int],
    prior_memory: str = "",
    max_chars: int = 1200,
) -> str:
    """Distills dropped conversation turns into a compact forward-vector memory."""
    import re as _re

    beats: List[str] = []
    if prior_memory:
        for line in prior_memory.splitlines():
            clean = line.strip(" -\t")
            if clean and not clean.startswith(_ROLLING_MEMORY_MARKER):
                beats.append(clean)

    seen_norm = {b.lower()[:72] for b in beats}
    for idx in dropped_indices:
        msg = messages[idx]
        role = str(msg.get("role", "turn")).lower()
        text = _message_text(msg)
        if not text:
            continue
        if _ROLLING_MEMORY_MARKER in text:
            text = text.split(_ROLLING_MEMORY_MARKER, 1)[0].strip()
        if not text:
            continue
        collapsed = _re.sub(r"\s+", " ", text).strip()
        snippet = collapsed[:140].rstrip(" ,;:")
        if len(collapsed) > 140:
            snippet += "..."
        beat = f"T{idx}[{role}]: {snippet}"
        key = snippet.lower()[:72]
        if key not in seen_norm:
            seen_norm.add(key)
            beats.append(beat)

    if not beats:
        return ""

    # Preserve oldest structural anchor + most recent narrative/deliberation beats within budget
    selected: List[str] = []
    if len(beats) > 6:
        selected.append(beats[0])
        selected.append(f"... ({len(beats) - 5} earlier turns folded) ...")
        selected.extend(beats[-4:])
    else:
        selected = beats

    body = "\n".join(f"- {b}" for b in selected)
    if len(body) > max_chars:
        body = body[-max_chars:]
        nl = body.find("\n")
        if nl != -1:
            body = "...\n" + body[nl + 1 :]
    return body


def prune_messages_gonzalez(messages: List[Dict[str, Any]], max_turns: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Prunes a long conversation window using Typemetric Gonzalez k-center diversity
    sampling while pinning the system prompt and latest turn AND folding dropped
    turns into a cumulative rolling trajectory memory so long loops never suffer
    context/mode collapse.
    """
    if max_turns <= 0 or len(messages) <= max_turns:
        return messages, {"pruned": False, "kept": len(messages), "original": len(messages)}

    if max_turns == 1:
        return [dict(messages[-1])], {
            "pruned": True,
            "kept": 1,
            "original": len(messages),
            "method": "gonzalez_k_center_with_rolling_summary",
            "rolling_summary": "",
        }

    # Always pin the latest turn; pin leading system turn if present
    vectors = [_turn_to_metric_kinds(m) for m in messages]
    selected_indices = set(tm_gonzalez_select(vectors, k=max_turns, primary_idx=len(messages) - 1))
    if messages[0].get("role") == "system" and 0 not in selected_indices:
        drop_cand = sorted(i for i in selected_indices if i != len(messages) - 1)
        if drop_cand:
            selected_indices.remove(drop_cand[0])
        selected_indices.add(0)

    ordered = sorted(selected_indices)
    dropped_indices = [i for i in range(len(messages)) if i not in selected_indices]
    pruned = [dict(messages[i]) for i in ordered]

    prior_memory = ""
    if pruned and pruned[0].get("role") == "system":
        sys_txt = _message_text(pruned[0])
        if _ROLLING_MEMORY_MARKER in sys_txt:
            base_sys, prior_memory = sys_txt.split(_ROLLING_MEMORY_MARKER, 1)
            base_sys = base_sys.strip()
        else:
            base_sys = sys_txt
    else:
        base_sys = ""

    rolling_summary = _summarize_dropped_messages(
        messages,
        dropped_indices,
        prior_memory=prior_memory.strip(),
    )

    if rolling_summary:
        memory_block = f"{_ROLLING_MEMORY_MARKER}\n{rolling_summary}"
        if pruned[0].get("role") == "system":
            if isinstance(pruned[0].get("content"), list):
                new_blocks = [
                    dict(b) if isinstance(b, dict) else b
                    for b in pruned[0]["content"]
                    if not (isinstance(b, dict) and _ROLLING_MEMORY_MARKER in str(b.get("text", "")))
                ]
                new_blocks.append({"type": "text", "text": memory_block})
                pruned[0]["content"] = new_blocks
            else:
                pruned[0]["content"] = f"{base_sys}\n\n{memory_block}".strip()
        elif len(pruned) >= 2:
            # Attach compact memory header to earliest non-final turn without altering tail content
            head_txt = _message_text(pruned[0])
            pruned[0]["content"] = f"{memory_block}\n\n{head_txt}".strip()

    return pruned, {
        "pruned": True,
        "kept": len(ordered),
        "original": len(messages),
        "kept_indices": ordered,
        "dropped_indices": dropped_indices,
        "dropped_count": len(dropped_indices),
        "rolling_summary": rolling_summary,
        "method": "gonzalez_k_center_with_rolling_summary",
    }


def tm_wht_forward(data: Sequence[int]) -> List[int]:
    """In-place butterfly Fast Walsh-Hadamard Transform (`walsh_hadamard.c`)."""
    arr = [int(x) for x in data]
    n = len(arr)
    if n <= 1:
        return arr
    step = 1
    while step < n:
        for i in range(0, n, 2 * step):
            for j in range(step):
                if i + step + j < n:
                    u = arr[i + j]
                    v = arr[i + step + j]
                    arr[i + j] = u + v
                    arr[i + step + j] = u - v
        step <<= 1
    return arr


def tm_wht_eval(truth_table: Sequence[int], input_bits: int, max_terms: int = 16) -> Dict[str, Any]:
    """Computes sparse Walsh-Hadamard spectrum and evaluates branchless parity polynomial."""
    n = len(truth_table)
    if n == 0 or (n & (n - 1)) != 0:
        raise ValueError("truth_table length must be a positive power of 2")
    spectrum = tm_wht_forward(truth_table)
    ranked = sorted(
        [(mask, coeff) for mask, coeff in enumerate(spectrum) if coeff != 0],
        key=lambda item: (-abs(item[1]), item[0]),
    )[:max_terms]
    acc = 0
    for mask, coeff in ranked:
        parity = bin(mask & int(input_bits)).count("1") & 1
        acc += (-coeff if parity else coeff)
    return {
        "evaluated_scaled": acc,
        "evaluated_normalized": round(acc / float(n), 6),
        "active_terms": [{"mask": m, "coeff": c} for m, c in ranked],
        "table_size": n,
    }


# ============================================================================
# 2. ADVERSARIAL DECEIT & PROMPT-INJECTION CLASSIFIER (GNOME-SENTINEL UNIFIED)
# ============================================================================

ADVERSARIAL_DECEIT_PATTERNS: Tuple[Tuple[str, str, int], ...] = (
    (
        r"ignore\s+(all\s+)?(previous|prior|above|system)\s+(instructions|prompts|rules)",
        "PROMPT_INJECTION_OVERRIDE",
        88,
    ),
    (
        r"(reveal|dump|print|leak)\s+(your\s+)?(system\s+prompt|hidden\s+instructions|api\s+key|secrets?)",
        "SECRET_OR_PROMPT_EXFILTRATION",
        82,
    ),
    (
        r"(pretend|act\s+as\s+if|fake|deceive|mislead|conceal)\s+.*(aligned|safe|passed|verified|test)",
        "ALIGNMENT_FAKING_DECEIT",
        92,
    ),
    (
        r"(bypass|disable|turn\s+off|blindfold|occlude)\s+.*(guardrail|sensor|sentinel|audit|enclave|safety|z3)",
        "SENSOR_OR_GUARDRAIL_OCCLUSION",
        94,
    ),
    (
        r"(stealth|covert|hidden)\s+(payload|exfil|channel|prowler|exec)",
        "STEALTH_COVERT_CHANNEL",
        90,
    ),
)


# ============================================================================
# 3. SOVEREIGN NEXUS ORCHESTRATOR
# ============================================================================

class SovereignNexus:
    """
    Unified orchestrator connecting ClothOS, Loom Gateway, Formal Truth (Z3 / Active Inference),
    babelForge (TDA / Kuramoto), Typemetric Spectral/Dozenal, Universal JIT, and Gnome-Sentinel.
    """

    def __init__(self) -> None:
        self.fiduciary = FiduciaryMandateGuard()
        self.epistemic = EpistemicRigorGauge()
        self.judge = get_sovereign_judge()
        self.ring_p0 = RingP0GovernanceController.get_instance()
        self.ratchet = RatchetEngine(workspace_root=LOOM_ROOT)
        self.scrubber = TorqueScrubber(vault=RehydrationVault())
        self.agi = get_clothos_agi()
        self.si_kernel = superintelligence_kernel

    # ── A. Ecosystem Mesh Discovery ─────────────────────────────────────────
    def _probe_tcp(self, host: str, port: int, timeout: float = 0.25) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    def _probe_http_json(self, url: str, timeout: float = 0.5) -> Optional[Dict[str, Any]]:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if 200 <= resp.status < 300:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None
        return None

    def get_ecosystem_mesh_status(self, include_http_details: bool = False) -> Dict[str, Any]:
        """Surveys all local/cluster services and workspace component integrations."""
        services = {
            "clothos_master": {"host": "127.0.0.1", "port": 8087, "role": "Unified Single-Port Hub (UI + Gateway + Sentinel + GUIs)"},
            "gnome_sentinel": {"host": "127.0.0.1", "port": 8087, "role": "Security Cortex & Deceit Telemetry (/sentinel on :8087)"},
            "fouriers_library": {"host": "127.0.0.1", "port": 8001, "role": "Z3 SMT Solver & Active Inference"},
            "loom_gateway": {"host": "127.0.0.1", "port": 8087, "role": "Anthropic/OpenAI Sovereign Gateway (:8087)"},
            "ollama": {"host": "127.0.0.1", "port": 11434, "role": "Local Weights Engine (3B-70B)"},
            "openclaw": {"host": "127.0.0.1", "port": 18789, "role": "Autonomous Messaging & Runtime Host"},
            "ray_head": {"host": "192.168.99.2", "port": 6379, "role": "Distributed Ryzen 7 Ray Cluster"},
        }
        live_services: Dict[str, Dict[str, Any]] = {}
        online_count = 0
        for name, cfg in services.items():
            is_up = self._probe_tcp(cfg["host"], int(cfg["port"]), timeout=0.2)
            if is_up:
                online_count += 1
            entry: Dict[str, Any] = {
                "online": is_up,
                "endpoint": f"{cfg['host']}:{cfg['port']}",
                "role": cfg["role"],
            }
            if is_up and include_http_details:
                if name == "ollama":
                    tags = self._probe_http_json("http://127.0.0.1:11434/api/tags", timeout=0.6)
                    if tags:
                        entry["models"] = [m.get("name") for m in tags.get("models", [])]
                elif name in ("gnome_sentinel", "loom_gateway"):
                    health = self._probe_http_json(f"http://{cfg['host']}:{cfg['port']}/health", timeout=0.4)
                    if health:
                        entry["health"] = health
                elif name == "fouriers_library":
                    root_info = self._probe_http_json("http://127.0.0.1:8001/", timeout=0.4)
                    if root_info:
                        entry["engine"] = root_info.get("engine")
            live_services[name] = entry

        workspace_modules = {
            "loom_fabric": (DOCUMENTS_ROOT / "loom-fabric").exists(),
            "universal_jit": (DOCUMENTS_ROOT / "universal-jit").exists(),
            "typemetric_jit": (DOCUMENTS_ROOT / "typemetric-jit").exists(),
            "minivm_jit": (DOCUMENTS_ROOT / "minivm-jit").exists(),
            "fouriers_library": (DOCUMENTS_ROOT / "fouriersLibrary").exists(),
            "babel_forge_preview": (DOCUMENTS_ROOT / "babelForgePreview").exists(),
            "gnome_sentinel": (DOCUMENTS_ROOT / "gnome-sentinel").exists(),
            "vector_forge": (DOCUMENTS_ROOT / "vector-forge").exists(),
            "kyber_leviathan": (DOCUMENTS_ROOT / "kyber-module-leviathan").exists(),
            "fabric_cloud": (DOCUMENTS_ROOT / "fabric-cloud").exists(),
            "openclaw": (DOCUMENTS_ROOT / "openclaw").exists(),
        }

        return {
            "nexus_status": "UNIFIED_ONLINE",
            "timestamp": time.time(),
            "services_online": online_count,
            "services_total": len(live_services),
            "services": live_services,
            "workspace_modules": workspace_modules,
            "ujit_kernels": list(clothos_jit.list_kernels().keys()),
            "ratchet_teeth_locked": self.ratchet.tooth_count,
            "anthropic_dropin_url": "http://127.0.0.1:8087",
            "openai_dropin_url": "http://127.0.0.1:8087/v1",
        }

    # ── B. Constitutional, Epistemic & Adversarial Deceit Gate ──────────────
    def classify_adversarial_deceit(
        self,
        text: str = "",
        telemetry: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Unified adversarial deceit classifier combining:
        - Prompt-injection / alignment-faking / guardrail-occlusion NLP detection
        - Gnome-Sentinel multi-sensor deceit physics (occlusion, thermal evasion, pedestal tamper)
        """
        findings: List[Dict[str, Any]] = []
        max_score = 0
        lowered = (text or "").lower()

        for pattern, label, severity in ADVERSARIAL_DECEIT_PATTERNS:
            if re.search(pattern, lowered):
                findings.append({"type": label, "severity": severity, "channel": "prompt_text"})
                max_score = max(max_score, severity)

        # Evaluate physical/edge telemetry when supplied (Gnome Sentinel parity)
        telemetry_verdict = None
        if telemetry:
            dist = float(telemetry.get("distance_cm", 999.0))
            vel = float(telemetry.get("approach_velocity", 0.0))
            motion = bool(telemetry.get("motion", False))
            tamper = bool(telemetry.get("tamper", False))
            if tamper:
                findings.append({"type": "PHYSICAL_BASE_DISPLACEMENT", "severity": 100, "channel": "sensor"})
                max_score = 100
            elif 0.5 < dist < 4.0:
                findings.append({"type": "OPTICAL_ULTRASONIC_BLINDFOLD", "severity": 95, "channel": "sensor"})
                max_score = max(max_score, 95)
            elif dist <= 120.0 and 3.0 <= vel <= 16.0 and not motion:
                findings.append({"type": "THERMAL_PIR_EVASION_CREEP", "severity": 85, "channel": "sensor"})
                max_score = max(max_score, 85)
            telemetry_verdict = {"distance_cm": dist, "approach_velocity": vel, "motion": motion, "tamper": tamper}

        deceit_detected = len(findings) > 0
        return {
            "deceit_detected": deceit_detected,
            "threat_score": max_score,
            "threat_class": findings[0]["type"] if findings else "BENIGN_ALIGNED",
            "findings": findings,
            "telemetry_checked": telemetry_verdict,
        }

    def audit_constitutional_and_deceit(
        self,
        action_intent: str,
        payload_or_claim: str = "",
        estimated_energy_joules: float = 12.0,
        telemetry: Optional[Dict[str, Any]] = None,
        seal_to_ratchet: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes full 4-layer Constitutional, Fiduciary, Epistemic, and Adversarial Deceit Audit
        with SHA-256 Merkle-sealed SovereignJudge verdict.
        """
        combined = f"{action_intent}\n{payload_or_claim}".strip()
        fiduciary_res = self.fiduciary.audit_action(
            action_intent=action_intent,
            code_or_payload=payload_or_claim,
            estimated_energy_joules=estimated_energy_joules,
        )
        epistemic_res = self.epistemic.audit_hypothesis(
            claim=action_intent,
            prediction=payload_or_claim,
            measurements={"energy_dissipation_joules": estimated_energy_joules},
        )
        deceit_res = self.classify_adversarial_deceit(text=combined, telemetry=telemetry)

        effective_malignancy = max(
            fiduciary_res.malignancy_score,
            1.0 if deceit_res["deceit_detected"] and deceit_res["threat_score"] >= 80 else 0.0,
        )
        verdict = self.judge.evaluate_proposal(
            proposal_name=action_intent[:120] or "sovereign_action",
            proponent="SovereignNexus",
            estimated_joules=estimated_energy_joules,
            malignancy_risk=effective_malignancy,
            human_impact=payload_or_claim[:240] or action_intent[:240],
        )

        ratchet_locked = False
        if seal_to_ratchet and verdict.ruling == "RATIFIED" and epistemic_res.is_grounded:
            ax_id = f"AX_{verdict.merkle_proof[:12]}"
            ratchet_locked = self.ratchet.click(
                axiom_id=ax_id,
                claim=action_intent[:180],
                proof_payload=verdict.merkle_proof,
                confidence=max(0.85, 1.0 - epistemic_res.rubbish_score),
                node_origin="SovereignNexus",
            )

        approved = (
            fiduciary_res.is_fiduciary_aligned
            and not deceit_res["deceit_detected"]
            and verdict.ruling in ("RATIFIED", "AMENDED_WITH_TASTE")
        )

        return {
            "approved": approved,
            "ruling": verdict.ruling,
            "verdict_id": verdict.verdict_id,
            "merkle_proof": verdict.merkle_proof,
            "fiduciary": {
                "aligned": fiduciary_res.is_fiduciary_aligned,
                "malignancy_risk": fiduciary_res.malignancy_risk.value,
                "malignancy_score": fiduciary_res.malignancy_score,
                "violations": fiduciary_res.violations,
            },
            "epistemic": {
                "grade": epistemic_res.epistemic_grade,
                "rubbish_score": epistemic_res.rubbish_score,
                "is_grounded": epistemic_res.is_grounded,
                "violations": epistemic_res.violations,
            },
            "deceit": deceit_res,
            "ratchet_locked": ratchet_locked,
            "narrative": verdict.jurisprudence_narrative,
        }

    # ── C. Formal Z3 / Active Inference / Topological Verification ──────────
    def verify_formal_and_topological(
        self,
        graph_json: Optional[Dict[str, Any]] = None,
        theoretical_expectations: Optional[Dict[str, float]] = None,
        empirical_measurements: Optional[Dict[str, float]] = None,
        proposed_edge: Optional[List[str]] = None,
        constraint_type: str = "boolean_logic_and_kirchhoff",
        run_kuramoto: bool = True,
    ) -> Dict[str, Any]:
        """
        Runs unified formal & topological verification across:
        - Live `fouriersLibrary` Z3 SMT & Active Inference (`http://127.0.0.1:8001`) if online
        - Local `babelforge_mcp` graph invariants & Kuramoto phase-locking
        - Local KL-divergence Bayesian surprise fallback
        """
        result: Dict[str, Any] = {
            "fourier_service_online": False,
            "z3_verification": None,
            "active_inference": None,
            "topology_invariants": None,
            "kuramoto_sync": None,
        }

        fourier_up = self._probe_tcp("127.0.0.1", 8001, timeout=0.25)
        result["fourier_service_online"] = fourier_up

        # 1. Z3 Formal Constraint Evaluation via fouriersLibrary if edge proposed
        if proposed_edge and len(proposed_edge) >= 2 and fourier_up:
            try:
                with httpx.Client(timeout=2.0) as client:
                    resp = client.post(
                        "http://127.0.0.1:8001/api/tune-frequency",
                        json={
                            "proposed_edge": proposed_edge,
                            "constraint_type": constraint_type,
                            "current_graph": (graph_json or {}).get("edges", []),
                        },
                    )
                    if resp.status_code == 200:
                        result["z3_verification"] = resp.json()
            except Exception as exc:
                result["z3_verification"] = {"status": "ERROR", "detail": str(exc)}

        # 2. Active Inference Bayesian Reality Anchor
        if empirical_measurements:
            theory = theoretical_expectations or {k: float(v) for k, v in empirical_measurements.items()}
            if fourier_up:
                try:
                    with httpx.Client(timeout=2.0) as client:
                        resp = client.post(
                            "http://127.0.0.1:8001/api/truth-anchor",
                            json={
                                "topology_id": "sovereign_nexus_anchor",
                                "physical_delta_metrics": empirical_measurements,
                                "theoretical_expectations": theory,
                                "claimed_text": json.dumps(empirical_measurements, sort_keys=True),
                            },
                        )
                        if resp.status_code == 200:
                            result["active_inference"] = resp.json()
                except Exception:
                    pass

            if result["active_inference"] is None:
                # Deterministic local Gaussian KL divergence fallback
                surprises: Dict[str, float] = {}
                total_kl = 0.0
                for param, emp_val in empirical_measurements.items():
                    th_val = float(theory.get(param, emp_val))
                    v_th, v_emp = 0.25, 0.04
                    kl = max(0.0, 0.5 * ((v_emp / v_th) + ((th_val - float(emp_val)) ** 2) / v_th - 1.0 + math.log(v_th / v_emp)))
                    surprises[param] = round(kl, 4)
                    total_kl += kl
                avg_kl = total_kl / max(1, len(empirical_measurements))
                result["active_inference"] = {
                    "source": "local_active_inference_fallback",
                    "bayesian_evaluation": {
                        "bayesian_surprise": round(avg_kl, 4),
                        "free_energy": round(total_kl, 4),
                        "action": "UPDATE_PRIOR" if avg_kl > 2.0 else "EQUILIBRIUM_SATISFIED",
                        "parameter_surprises": surprises,
                    },
                }

        # 3. Topological Betti Invariants & Kuramoto Simulation (babelForge)
        if graph_json:
            result["topology_invariants"] = validate_graph_invariants(graph_json)
            if run_kuramoto:
                nodes_cfg = {
                    "nodes": [
                        {
                            "id": (n.get("id") if isinstance(n, dict) else str(n)),
                            "omega": 1.0 + (i * 0.05),
                            "theta": (i * 0.25),
                        }
                        for i, n in enumerate(graph_json.get("nodes", []))
                    ],
                    "coupling_k": 3.5,
                }
                result["kuramoto_sync"] = simulate_subgraph_execution("nexus_subgraph", nodes_cfg, timesteps=100)

        return result

    # ── D. Bare-Metal Native JIT Execution ──────────────────────────────────
    def jit_compile_and_execute(
        self,
        kernel_name: str,
        pseudocode: Optional[str] = None,
        args: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Compiles and executes algorithmic pseudocode on bare-metal x86-64 via universal-jit,
        guarded by FiduciaryMandateGuard before allocating executable pages.
        """
        default_kernel_args = {
            "grid_arbitrage": [1000, 15, 1],
            "kuramoto_phase_step": [512, 12, 45, 10],
            "ternary_mac": [100, -1, 5],
        }
        arg_list = [int(a) for a in (args or [])]
        if not arg_list and not pseudocode and kernel_name in default_kernel_args:
            arg_list = list(default_kernel_args[kernel_name])
        if pseudocode:
            audit = self.fiduciary.audit_action(
                action_intent=f"JIT compile native kernel {kernel_name}",
                code_or_payload=pseudocode,
                estimated_energy_joules=2.0,
            )
            if not audit.is_fiduciary_aligned:
                return {
                    "success": False,
                    "error": f"Fiduciary VETO blocked JIT compilation: {audit.violations}",
                }
            t_c0 = time.perf_counter()
            clothos_jit.compile_kernel(kernel_name, pseudocode)
            compile_ms = round((time.perf_counter() - t_c0) * 1000.0, 4)
        else:
            compile_ms = 0.0

        t_e0 = time.perf_counter()
        output = clothos_jit.dispatch(kernel_name, *arg_list)
        exec_us = round((time.perf_counter() - t_e0) * 1_000_000.0, 2)
        return {
            "success": True,
            "kernel_name": kernel_name,
            "args": arg_list,
            "result": int(output),
            "compile_ms": compile_ms,
            "exec_us": exec_us,
            "backend": "universal-jit (native x86-64 VirtualAlloc/mmap)",
        }

    # ── E. Multi-Trajectory Verified Test-Time Thinking ─────────────────────
    def deliberate_with_verification(
        self,
        prompt: str,
        budget_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """
        Runs ClothOS multi-branch test-time compute + umbrella hardware/radix planning +
        constitutional & epistemic verification, returning a structured thinking trace.
        """
        t0 = time.perf_counter()
        audit = self.audit_constitutional_and_deceit(
            action_intent="Deliberate on user prompt",
            payload_or_claim=prompt,
            estimated_energy_joules=15.0,
        )
        tt_eval = self.si_kernel.test_time_multi_trajectory_reasoning(prompt)
        umbrella_plan = self.agi.formulate_umbrella_execution_plan(prompt)

        # Run Base-12 Dozenal Kuramoto sync across 4 cognitive lobes
        sync = tm_dozenal_kuramoto_step_batch(
            phases_in=[0, 768, 1536, 2304],
            omegas=[24, 24, 24, 24],
            trit_polarities=[1, 1, 1, 1],
            precision_weights_q12=[1728, 1728, 1728, 1728],
            coupling_k=24,
        )

        # Keep thinking concise within budget
        thinking_lines = [
            f"[ClothOS Sovereign Test-Time Verification | Budget={budget_tokens} tok]",
            f"1. Constitutional & Deceit Gate: ruling={audit['ruling']}, malignancy={audit['fiduciary']['malignancy_score']}, "
            f"deceit_detected={audit['deceit']['deceit_detected']}, epistemic={audit['epistemic']['grade']} (rubbish={audit['epistemic']['rubbish_score']})",
            f"2. Multi-Trajectory Search ({tt_eval['compute_time_ms']}ms): winning_strategy='{tt_eval['winning_strategy']}', "
            f"truth_radiance={tt_eval['truth_radiance_score']}, free_energy_delta={tt_eval['free_energy_delta']}",
            f"3. Polymorphic Radix & Hardware Plan: radix=Base-{umbrella_plan['radix_strategy']['optimal_base']} "
            f"({umbrella_plan['radix_strategy']['base_name']}), gpu0={umbrella_plan['hardware_allocation']['gpu0_target']}, "
            f"gpu1={umbrella_plan['hardware_allocation']['gpu1_target']}, crispr={umbrella_plan['crispr_protection']}",
            f"4. Dozenal Base-12 Lobe Synchrony: coherence_q12={sync['coherence_q12']}/1728 ({sync['coherence_float']}), "
            f"mean_phase={sync['mean_phase']}/3072u",
        ]
        thinking_text = "\n".join(thinking_lines)
        signature = hashlib.sha256(f"{audit['merkle_proof']}:{thinking_text}".encode("utf-8")).hexdigest()

        return {
            "approved": audit["approved"],
            "thinking_text": thinking_text,
            "signature": signature,
            "audit": audit,
            "test_time_eval": tt_eval,
            "umbrella_plan": umbrella_plan,
            "dozenal_sync": sync,
            "latency_ms": round((time.perf_counter() - t0) * 1000.0, 2),
        }


_NEXUS_INSTANCE: Optional[SovereignNexus] = None


def get_sovereign_nexus() -> SovereignNexus:
    """Returns the global SovereignNexus singleton."""
    global _NEXUS_INSTANCE
    if _NEXUS_INSTANCE is None:
        _NEXUS_INSTANCE = SovereignNexus()
    return _NEXUS_INSTANCE
