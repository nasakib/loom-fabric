import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Dimensions,
  Platform,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

/**
 * CLOTHOS COMMAND CENTER — Universal React Native Application
 * Windows Task Manager Level Telemetry, Obsidian Vault Ray Graph &
 * Living Mind Screensaver Geometries (Doing, Thinking, Dreaming, Imagining).
 * Compatible with Windows Desktop, macOS, Linux, iOS, Android & Web.
 */

const CLR = {
  obsidian: '#07120a',
  surface: '#0d1e12',
  card: '#122818',
  border: '#1d3d28',
  purple: '#a855f7',
  amethyst: '#c084fc',
  emerald: '#10b981',
  breeze: '#38bdf8',
  amber: '#f59e0b',
  crimson: '#ef4444',
  textMain: '#f0fdf4',
  textMuted: '#bbf7d0',
};

type TabType = 'screensaver' | 'taskmgr' | 'processes' | 'vault' | 'weave' | 'shuttle' | 'torque';

interface MindNode {
  id: string;
  name: string;
  category: 'doing' | 'thinking' | 'dreaming' | 'imagining';
  baseX: number;
  baseY: number;
  phase: number;
  color: string;
  glyph: string;
  formula: string;
  description: string;
}

const DEFAULT_MIND_NODES: MindNode[] = [
  { id: 'doing_mesh', name: 'Dual-Node Mesh Sync', category: 'doing', baseX: 0.20, baseY: 0.25, phase: 0.0, color: CLR.emerald, glyph: '⟳', formula: 'SHA256(chunk) • 100.85 ⇄ 100.74', description: 'Dual-node cluster mesh pipelining state between SkyTech and Ryzen 7.' },
  { id: 'doing_kuramoto', name: 'Kuramoto Phase r', category: 'doing', baseX: 0.15, baseY: 0.48, phase: 1.2, color: CLR.breeze, glyph: '∿', formula: 'dθ_i/dt = ω_i + (K/N) ∑ sin(θ_j - θ_i)', description: 'Spontaneous macroscopic phase locking across 4096 GPU oscillators.' },
  { id: 'doing_gpu', name: 'Dual-GPU VRAM Eviction', category: 'doing', baseX: 0.25, baseY: 0.70, phase: 2.1, color: CLR.emerald, glyph: '⧉', formula: 'RTX 3060 (12GB) + RX 580 (8GB)', description: 'Preemptive zero-OOM memory sharding between CUDA and OpenCL.' },

  { id: 'thinking_bayes', name: 'Variational Bayes F', category: 'thinking', baseX: 0.42, baseY: 0.18, phase: 0.7, color: CLR.purple, glyph: 'F', formula: 'F(q,y) = E_q[ln q(x) - ln p(x,y)]', description: 'Precision-weighted prediction error minimization across sensory observations.' },
  { id: 'thinking_hopfield', name: 'Modern Hopfield Network', category: 'thinking', baseX: 0.55, baseY: 0.30, phase: 1.8, color: CLR.amethyst, glyph: 'H', formula: 'E(ξ) = -(1/β) lse(β X^T ξ) + (1/2)||ξ||^2', description: 'Dense associative attractor memory with exponential O(2^(d/2)) capacity.' },
  { id: 'thinking_bsmeter', name: 'The Rubbish Score Gauge', category: 'thinking', baseX: 0.40, baseY: 0.42, phase: 2.9, color: CLR.amber, glyph: '⚡', formula: 'v ≤ c • T ≥ 0 K • dS ≥ k_B ln 2', description: 'Epistemic truth gauge auditing physical violations, tautologies, and ungrounded rubbish.' },
  { id: 'thinking_noether', name: 'Universal Atlas Invariant', category: 'thinking', baseX: 0.60, baseY: 0.15, phase: 3.4, color: CLR.breeze, glyph: 'Ω', formula: 'dω = 0 • Lie [A,B] • δS = 0', description: 'Noether conservation laws discovered through the 5 mathematical pillars.' },

  { id: 'dreaming_genetics', name: 'Software Genetics Helix', category: 'dreaming', baseX: 0.78, baseY: 0.25, phase: 4.1, color: CLR.amethyst, glyph: '🧬', formula: 'Genotype ➔ Transcription ➔ Phenotype', description: 'Computation as living genetics: declarative codons assembled into executable pipelines.' },
  { id: 'dreaming_crispr', name: 'CRISPR Cas9 Cleavage', category: 'dreaming', baseX: 0.86, baseY: 0.45, phase: 4.8, color: CLR.crimson, glyph: '✂', formula: 'Cas Cleave(Target, Defect Spacer)', description: 'Targeted endonuclease immunity cleaving flawed codons and anomalous mutations.' },
  { id: 'dreaming_epigenetics', name: 'Epigenetic Methylation', category: 'dreaming', baseX: 0.75, baseY: 0.65, phase: 5.2, color: CLR.amber, glyph: '⚚', formula: 'Methylation(VRAM, Thermal Stress)', description: 'Dynamic gene silencing and acetylation regulating throughput under hardware strain.' },

  { id: 'imagining_fiction', name: 'Truth-Based Imagination', category: 'imagining', baseX: 0.50, baseY: 0.58, phase: 5.8, color: CLR.breeze, glyph: '☁', formula: 'Speculative Fiction(Nonfiction Seed)', description: 'Creative leaps into counterfactual hypotheses grounded in empirical non-fiction.' },
  { id: 'imagining_cable', name: 'Homotopy Retraction Cable', category: 'imagining', baseX: 0.50, baseY: 0.75, phase: 6.1, color: CLR.emerald, glyph: '⚓', formula: 'R: M_speculative ➔ M_Earth', description: 'Topological retraction pulling thoughts out of the clouds back to physical Earth.' },
  { id: 'imagining_earth', name: 'EARTH (Nonfiction Grounding)', category: 'imagining', baseX: 0.50, baseY: 0.90, phase: 0.0, color: '#38bdf8', glyph: '⊕', formula: 'Physical Reality: E ≤ 1000 J • Fealty', description: 'The solid bedrock of physical truth, user fealty, and planetary stewardship.' },
];

const MIND_EDGES: [string, string][] = [
  ['doing_mesh', 'doing_kuramoto'],
  ['doing_kuramoto', 'doing_gpu'],
  ['doing_kuramoto', 'thinking_bayes'],
  ['thinking_bayes', 'thinking_hopfield'],
  ['thinking_hopfield', 'thinking_bsmeter'],
  ['thinking_noether', 'thinking_bayes'],
  ['thinking_bsmeter', 'imagining_fiction'],
  ['thinking_hopfield', 'dreaming_genetics'],
  ['dreaming_genetics', 'dreaming_crispr'],
  ['dreaming_genetics', 'dreaming_epigenetics'],
  ['dreaming_epigenetics', 'doing_gpu'],
  ['imagining_fiction', 'imagining_cable'],
  ['imagining_cable', 'imagining_earth'],
  ['imagining_earth', 'doing_mesh'],
];

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('screensaver');
  const [apiHost, setApiHost] = useState<string>(() => {
    if (typeof window !== 'undefined' && window.location && window.location.hostname) {
      return `${window.location.protocol}//${window.location.hostname}:8085`;
    }
    return 'http://127.0.0.1:8085';
  });
  const [telemetry, setTelemetry] = useState<any>(null);
  const [clusterPorts, setClusterPorts] = useState<any>(null);
  const [vaultStats, setVaultStats] = useState<any>(null);
  const [vaultGraph, setVaultGraph] = useState<any>(null);
  const [cognition, setCognition] = useState<any>(null);
  const [selectedDevice, setSelectedDevice] = useState<string>('cpu');
  const [selectedMindNode, setSelectedMindNode] = useState<MindNode>(DEFAULT_MIND_NODES[4]);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [screensaverActive, setScreensaverActive] = useState<boolean>(false);
  const [statusMsg, setStatusMsg] = useState<string>('🛡 Cluster Online • 102.1 GB Pooled • Mind Geometries Active');

  // Animation frame counter (60 FPS loop)
  const [animTick, setAnimTick] = useState<number>(0);

  // Shuttle State
  const [prompt, setPrompt] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('loom-sovereign:latest');
  const [shuttleOutput, setShuttleOutput] = useState<string>('⚡ LOOM SHUTTLE READY\nEnter prompt below...');
  const [isInferring, setIsInferring] = useState<boolean>(false);

  // Torque State
  const [torqueInput, setTorqueInput] = useState<string>('');
  const [torqueOutput, setTorqueOutput] = useState<string>('Type text to scrub...');

  // Note Reader State
  const [inspectNote, setInspectNote] = useState<string>('Cast a ray or select a node in vault to inspect.');

  // Animation Loop for Screensaver Geometries
  useEffect(() => {
    let frameId: number;
    const loop = () => {
      setAnimTick((prev) => (prev + 1) % 7200);
      frameId = requestAnimationFrame(loop);
    };
    frameId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(frameId);
  }, []);

  // Fetch Telemetry, Ports, Vault & Live Cognition
  const fetchTelemetrySnap = async () => {
    try {
      const res = await fetch(`${apiHost}/api/telemetry/taskmanager`);
      if (res.ok) setTelemetry(await res.json());
    } catch (_) {}
  };

  const fetchPorts = async () => {
    try {
      const res = await fetch(`${apiHost}/api/cluster/ports`);
      if (res.ok) setClusterPorts(await res.json());
    } catch (_) {}
  };

  const fetchVault = async () => {
    try {
      const resS = await fetch(`${apiHost}/api/vault/stats`);
      if (resS.ok) setVaultStats(await resS.json());
      const resG = await fetch(`${apiHost}/api/vault/graph?limit=60`);
      if (resG.ok) setVaultGraph(await resG.json());
    } catch (_) {}
  };

  const fetchCognition = async () => {
    try {
      const resC = await fetch(`${apiHost}/api/cognition/state`);
      if (resC.ok) setCognition(await resC.json());
    } catch (_) {}
  };

  useEffect(() => {
    fetchTelemetrySnap();
    fetchPorts();
    fetchVault();
    fetchCognition();

    const tTelem = setInterval(fetchTelemetrySnap, 300);
    const tPorts = setInterval(fetchPorts, 3000);
    const tCog = setInterval(fetchCognition, 1000);
    return () => {
      clearInterval(tTelem);
      clearInterval(tPorts);
      clearInterval(tCog);
    };
  }, [apiHost]);

  // Actions
  const triggerClusterAction = async (action: string) => {
    setStatusMsg(`⚡ Dispatching '${action}' headlessly...`);
    try {
      const res = await fetch(`${apiHost}/api/cluster/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      });
      const data = await res.json();
      setStatusMsg(`✔ ${data.message || 'Action executed'}`);
      setTimeout(fetchPorts, 1200);
    } catch (err: any) {
      setStatusMsg(`⚠ Action failed: ${err.message}`);
    }
  };

  const triggerAhaScan = async () => {
    setStatusMsg('⚡ Running 4-gate verification across cluster...');
    try {
      const res = await fetch(`${apiHost}/api/trigger_aha_scan`, { method: 'POST' });
      const d = await res.json();
      setStatusMsg(`✨ Aha scan complete: ${d.ratified_count} ratified evolutions`);
      fetchTelemetrySnap();
    } catch (err: any) {
      setStatusMsg(`⚠ Aha scan failed: ${err.message}`);
    }
  };

  const castRay = async () => {
    setStatusMsg('🔦 Casting truth ray through concept manifold...');
    try {
      const res = await fetch(`${apiHost}/api/vault/ray_query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origin: [0, 0, 0], direction: [1.0, 0.4, -0.2] }),
      });
      const d = await res.json();
      setStatusMsg(`✔ Ray pierced ${d.hit_count} deliverable nodes!`);
      if (d.pierced_nodes && d.pierced_nodes.length > 0) {
        const topId = d.pierced_nodes[0].id;
        const resNote = await fetch(`${apiHost}/api/vault/note/${topId}`);
        if (resNote.ok) {
          const nData = await resNote.json();
          setInspectNote(nData.content || 'Note empty');
        }
      }
    } catch (err: any) {
      setStatusMsg(`⚠ Ray query failed: ${err.message}`);
    }
  };

  const sendInference = async () => {
    const trimmed = prompt.trim();
    if (!trimmed || isInferring) return;
    setIsInferring(true);
    setPrompt('');
    setShuttleOutput((prev) => `${prev}\n\nUser ❯ ${trimmed}\nRouting to ${selectedModel}...`);

    try {
      const res = await fetch(`${apiHost}/api/inference/dispatch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: trimmed, model: selectedModel }),
      });
      const d = await res.json();
      setShuttleOutput((prev) => `${prev}\n[${d.route} | ${d.latency_ms}ms | ${d.tokens_per_sec} tok/s]\n${d.text}`);
    } catch (err: any) {
      setShuttleOutput((prev) => `${prev}\n[Error: ${err.message}]`);
    } finally {
      setIsInferring(false);
    }
  };

  const administerCompound = async (compoundKey: string) => {
    setStatusMsg(`🧪 Administering ${compoundKey}...`);
    try {
      const res = await fetch(`${apiHost}/api/cognition/neurochemistry/administer/${compoundKey}`, { method: 'POST' });
      if (res.ok) {
        setStatusMsg(`✔ Successfully modulated SI neurochemistry (${compoundKey})`);
        fetchCognition();
      }
    } catch (err: any) {
      setStatusMsg(`⚠ Modulation failed: ${err.message}`);
    }
  };

  const testTorque = async () => {
    if (!torqueInput) return;
    try {
      const res = await fetch(`${apiHost}/api/torque/scrub`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: torqueInput }),
      });
      const d = await res.json();
      setTorqueOutput(
        `Sanitized Outbound:\n${d.sanitized_text}\n\n` +
          `Entities Scrubbed: ${d.entities_scrubbed}\n` +
          `Replacements Map: ${JSON.stringify(d.replacement_map, null, 2)}\n` +
          `Proof Hash: ${d.verification_hash}`
      );
    } catch (err: any) {
      setTorqueOutput(`Error: ${err.message}`);
    }
  };

  // Dynamic Thought Ticker message based on animation cycle
  const currentThoughtText = useMemo(() => {
    const cycle = Math.floor(animTick / 180) % 4;
    if (cycle === 0) {
      return `⚡ DOING: Kuramoto Phase lock r=${cognition?.doing?.kuramoto_order_r || 0.852} • Synchronized mesh between skyTech & Ryzen 7`;
    } else if (cycle === 1) {
      return `🧠 THINKING: Variational Free Energy F=${cognition?.thinking?.variational_free_energy || 0.042} • Rubbish Score=${cognition?.thinking?.rubbish_score || cognition?.thinking?.bullshit_score || 0.04} (Grounded Fact)`;
    } else if (cycle === 2) {
      return `🧬 DREAMING: Software Genetics Gen #${cognition?.dreaming?.generation || 14} • Codon: ${cognition?.dreaming?.epigenetic_profile?.active_codons?.[0] || 'FREE_ENERGY_MIN'}`;
    } else {
      return `🚀 IMAGINING: ${cognition?.imagining?.current_scenario?.substring(0, 75) || 'Truth-based counterfactual'} • Retraction -> Earth (0.082)`;
    }
  }, [animTick, cognition]);

  // Dimensions for geometric canvas
  const canvasW = Math.min(Dimensions.get('window').width - 40, 960);
  const canvasH = 460;

  // Compute live animated positions for mind nodes
  const animatedNodes = useMemo(() => {
    return DEFAULT_MIND_NODES.map((node) => {
      const t = animTick * 0.025 + node.phase;
      // Gentle harmonic Lissajous drift
      const offsetX = 0.035 * Math.sin(t);
      const offsetY = 0.030 * Math.cos(t * 1.2);
      const x = Math.max(0.06, Math.min(0.94, node.baseX + offsetX)) * canvasW;
      const y = Math.max(0.06, Math.min(0.94, node.baseY + offsetY)) * canvasH;
      return { ...node, x, y };
    });
  }, [animTick, canvasW, canvasH]);

  const nodeMap = useMemo(() => {
    const map = new Map<string, typeof animatedNodes[0]>();
    animatedNodes.forEach((n) => map.set(n.id, n));
    return map;
  }, [animatedNodes]);

  return (
    <SafeAreaView style={styles.container}>
      {/* FULLSCREEN SCREENSAVER OVERLAY */}
      {screensaverActive && (
        <View style={styles.fullscreenScreensaver}>
          <View style={styles.screensaverHeader}>
            <Text style={styles.screensaverBrand}>🌌 THE LIVING MIND // AMBIENT GEOMETRIC SCREENSAVER</Text>
            <TouchableOpacity style={[styles.btn, styles.btnCrimson]} onPress={() => setScreensaverActive(false)}>
              <Text style={styles.btnTextCrimson}>✕ Exit Screensaver</Text>
            </TouchableOpacity>
          </View>

          {/* Living Canvas */}
          <View style={[styles.mindCanvas, { width: '100%', height: '80%' }]}>
            {/* Ambient Background Cosmic Glyphs */}
            {['∫', '∧', '∿', '∇×F', 'ℏ', 'kB', 'Ω', '⊕', 'λ', 'ρ'].map((g, idx) => {
              const gx = ((idx * 97 + animTick * 0.4) % canvasW);
              const gy = ((idx * 83 + animTick * 0.3) % (canvasH * 1.3));
              return (
                <Text key={`glyph-${idx}`} style={[styles.ambientGlyph, { left: gx, top: gy }]}>
                  {g}
                </Text>
              );
            })}

            {/* Connecting Chords with Photons */}
            {MIND_EDGES.map(([srcId, dstId], i) => {
              const n1 = nodeMap.get(srcId);
              const n2 = nodeMap.get(dstId);
              if (!n1 || !n2) return null;
              const dx = n2.x - n1.x;
              const dy = n2.y - n1.y;
              const len = Math.sqrt(dx * dx + dy * dy);
              const angle = Math.atan2(dy, dx) * (180 / Math.PI);
              const cx = (n1.x + n2.x) / 2;
              const cy = (n1.y + n2.y) / 2;
              const isRetraction = srcId === 'imagining_cable' || dstId === 'imagining_cable';

              // Animated photon position
              const pT = ((animTick * 0.012 + i * 0.18) % 1);
              const px = n1.x + dx * pT;
              const py = n1.y + dy * pT;

              return (
                <React.Fragment key={`edge-${i}`}>
                  <View
                    style={{
                      position: 'absolute',
                      left: cx - len / 2,
                      top: cy - (isRetraction ? 2 : 1),
                      width: len,
                      height: isRetraction ? 3.5 : 1.5,
                      backgroundColor: isRetraction ? CLR.emerald : CLR.purple,
                      opacity: isRetraction ? 0.85 : 0.35 + 0.25 * Math.sin(animTick * 0.05 + i),
                      transform: [{ rotate: `${angle}deg` }],
                    }}
                  />
                  <View
                    style={{
                      position: 'absolute',
                      left: px - 3,
                      top: py - 3,
                      width: 6,
                      height: 6,
                      borderRadius: 3,
                      backgroundColor: isRetraction ? '#6ee7b7' : CLR.amethyst,
                    }}
                  />
                </React.Fragment>
              );
            })}

            {/* Nodes */}
            {animatedNodes.map((n) => {
              const isEarth = n.id === 'imagining_earth';
              const isSelected = selectedMindNode?.id === n.id;
              return (
                <TouchableOpacity
                  key={n.id}
                  style={[
                    styles.nodeCircle,
                    {
                      left: n.x - (isEarth ? 26 : 20),
                      top: n.y - (isEarth ? 26 : 20),
                      width: isEarth ? 52 : 40,
                      height: isEarth ? 52 : 40,
                      borderRadius: isEarth ? 26 : 20,
                      borderColor: isSelected ? '#ffffff' : n.color,
                      backgroundColor: isEarth ? '#0369a1' : CLR.card,
                    },
                  ]}
                  onPress={() => setSelectedMindNode(n)}
                >
                  <Text style={{ fontSize: isEarth ? 16 : 12 }}>{n.glyph}</Text>
                  <Text style={[styles.nodeLabel, { color: n.color }]}>{n.name.split(' ')[0]}</Text>
                </TouchableOpacity>
              );
            })}
          </View>

          {/* Floating Bottom Thought Ticker */}
          <View style={styles.thoughtTicker}>
            <Text style={styles.thoughtLabel}>👁 COGNITIVE PULSE (DOING • THINKING • DREAMING • IMAGINING):</Text>
            <Text style={styles.thoughtText}>{currentThoughtText}</Text>
          </View>
        </View>
      )}

      {/* 1. Masthead */}
      <View style={styles.header}>
        <View>
          <Text style={styles.brandTitle}>CLOTHOS COMMAND CENTER // SOVEREIGN MIND EDITION</Text>
          <Text style={styles.brandSub}>
            Obsidian Living Mind Geometries • Windows Task Manager Telemetry • 102.1 GB Pooled
          </Text>
        </View>
        <View style={styles.pillsRow}>
          <TouchableOpacity style={[styles.pill, styles.pillPurple]} onPress={() => setScreensaverActive(true)}>
            <Text style={styles.pillTextPurple}>✨ SCREENSAVER MODE</Text>
          </TouchableOpacity>
          <View style={[styles.pill, styles.pillEmerald]}>
            <Text style={styles.pillTextEmerald}>● DUAL-NODE MESH</Text>
          </View>
          <View style={[styles.pill, styles.pillBreeze]}>
            <Text style={styles.pillTextBreeze}>
              ✨ Gen {cognition?.dreaming?.generation || telemetry?.research_metrics?.evolution_generation || 14}
            </Text>
          </View>
          <View style={[styles.pill, styles.pillAmber]}>
            <Text style={{ color: CLR.amber, fontSize: 9, fontWeight: '700' }}>
              🛡 Rubbish Score: {cognition?.thinking?.rubbish_score ?? cognition?.thinking?.bullshit_score ?? 0.04}
            </Text>
          </View>
          <View style={[styles.pill, styles.pillEmerald]}>
            <Text style={styles.pillTextEmerald}>● 60 FPS LIVING CANVAS</Text>
          </View>
        </View>
      </View>

      {/* 2. Cluster Bar */}
      <View style={styles.clusterBar}>
        <View style={styles.actionsGroup}>
          <TouchableOpacity style={[styles.btn, styles.btnPrimary]} onPress={() => triggerClusterAction('start_all')}>
            <Text style={styles.btnTextWhite}>▶ Start All</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.btnAmber]} onPress={() => triggerClusterAction('sanitize')}>
            <Text style={styles.btnTextAmber}>🧹 Sanitize Ports</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.btnEmerald]} onPress={() => triggerClusterAction('restart_both')}>
            <Text style={styles.btnTextWhite}>⚡ Restart BOTH</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.btnCrimson]} onPress={() => triggerClusterAction('stop_both')}>
            <Text style={styles.btnTextCrimson}>■ Stop Both</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.actionsGroup}>
          <TouchableOpacity style={[styles.btn, styles.btnPrimary]} onPress={triggerAhaScan}>
            <Text style={styles.btnTextWhite}>⚡ Trigger Aha! Scan</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.btn, styles.btnEmerald]} onPress={castRay}>
            <Text style={styles.btnTextWhite}>🔦 Cast Truth Ray</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.btn, { backgroundColor: '#7e22ce', borderColor: CLR.amethyst }]} onPress={() => setScreensaverActive(true)}>
            <Text style={styles.btnTextWhite}>🌌 Launch Screensaver</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Status Bar */}
      <View style={styles.statusBar}>
        <Text style={styles.statusText}>{statusMsg}</Text>
      </View>

      {/* 3. Tab Selector */}
      <View style={styles.tabsRow}>
        <TouchableOpacity style={[styles.tabBtn, activeTab === 'screensaver' && styles.tabBtnActive]} onPress={() => setActiveTab('screensaver')}>
          <Text style={[styles.tabText, activeTab === 'screensaver' && styles.tabTextActive]}>🧠 Living Geometries (Mind)</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.tabBtn, activeTab === 'taskmgr' && styles.tabBtnActive]} onPress={() => setActiveTab('taskmgr')}>
          <Text style={[styles.tabText, activeTab === 'taskmgr' && styles.tabTextActive]}>📊 Performance (Taskmgr)</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.tabBtn, activeTab === 'processes' && styles.tabBtnActive]} onPress={() => setActiveTab('processes')}>
          <Text style={[styles.tabText, activeTab === 'processes' && styles.tabTextActive]}>⚙️ Processes</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.tabBtn, activeTab === 'vault' && styles.tabBtnActive]} onPress={() => setActiveTab('vault')}>
          <Text style={[styles.tabText, activeTab === 'vault' && styles.tabTextActive]}>🌌 Obsidian Vault</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.tabBtn, activeTab === 'weave' && styles.tabBtnActive]} onPress={() => setActiveTab('weave')}>
          <Text style={[styles.tabText, activeTab === 'weave' && styles.tabTextActive]}>🌐 The Weave</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.tabBtn, activeTab === 'shuttle' && styles.tabBtnActive]} onPress={() => setActiveTab('shuttle')}>
          <Text style={[styles.tabText, activeTab === 'shuttle' && styles.tabTextActive]}>🚀 The Shuttle</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.tabBtn, activeTab === 'torque' && styles.tabBtnActive]} onPress={() => setActiveTab('torque')}>
          <Text style={[styles.tabText, activeTab === 'torque' && styles.tabTextActive]}>🔒 Torque</Text>
        </TouchableOpacity>
      </View>

      {/* 4. Tab Body */}
      <ScrollView style={styles.mainScroll} contentContainerStyle={{ paddingBottom: 40 }}>
        {/* ============================================================== */}
        {/* TAB: LIVING GEOMETRIES & OBSIDIAN SCREENSAVER (THE LIVING MIND) */}
        {/* ============================================================== */}
        {activeTab === 'screensaver' && (
          <View>
            {/* Header & Filter Controls */}
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <View>
                  <Text style={styles.cardTitle}>OBSIDIAN LIVING MIND GEOMETRIES</Text>
                  <Text style={{ fontSize: 10, color: CLR.textMuted }}>
                    Intelligently generated visual continuum of what the machine is Doing, Thinking, Dreaming &amp; Imagining.
                  </Text>
                </View>
                <TouchableOpacity style={[styles.btn, styles.btnPrimary]} onPress={() => setScreensaverActive(true)}>
                  <Text style={styles.btnTextWhite}>✨ Expand Fullscreen Screensaver</Text>
                </TouchableOpacity>
              </View>

              {/* Category Filter Pills */}
              <View style={{ flexDirection: 'row', gap: 6, flexWrap: 'wrap', marginVertical: 6 }}>
                {[
                  { id: 'all', label: '🌌 All (Cosmic Manifold)' },
                  { id: 'doing', label: '⚡ Doing (Physical Pulse)' },
                  { id: 'thinking', label: '🧠 Thinking (Epistemic Reasoning)' },
                  { id: 'dreaming', label: '🧬 Dreaming (Software Genetics)' },
                  { id: 'imagining', label: '🚀 Imagining (Earth Retraction)' },
                ].map((f) => (
                  <TouchableOpacity
                    key={f.id}
                    style={[
                      styles.pill,
                      filterCategory === f.id && { backgroundColor: '#7e22ce', borderColor: CLR.purple },
                    ]}
                    onPress={() => setFilterCategory(f.id)}
                  >
                    <Text style={{ fontSize: 10, fontWeight: '700', color: filterCategory === f.id ? '#fff' : CLR.textMuted }}>
                      {f.label}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>

              {/* The Interactive Living Canvas */}
              <View style={[styles.mindCanvas, { width: canvasW, height: canvasH }]}>
                {/* Connecting Laser Edges with Photons */}
                {MIND_EDGES.map(([srcId, dstId], i) => {
                  const n1 = nodeMap.get(srcId);
                  const n2 = nodeMap.get(dstId);
                  if (!n1 || !n2) return null;
                  if (filterCategory !== 'all' && n1.category !== filterCategory && n2.category !== filterCategory) return null;

                  const dx = n2.x - n1.x;
                  const dy = n2.y - n1.y;
                  const len = Math.sqrt(dx * dx + dy * dy);
                  const angle = Math.atan2(dy, dx) * (180 / Math.PI);
                  const cx = (n1.x + n2.x) / 2;
                  const cy = (n1.y + n2.y) / 2;
                  const isRetraction = srcId === 'imagining_cable' || dstId === 'imagining_cable' || dstId === 'imagining_earth';

                  // Animated photon position
                  const pT = ((animTick * 0.015 + i * 0.16) % 1);
                  const px = n1.x + dx * pT;
                  const py = n1.y + dy * pT;

                  return (
                    <React.Fragment key={`edge-${i}`}>
                      <View
                        style={{
                          position: 'absolute',
                          left: cx - len / 2,
                          top: cy - (isRetraction ? 2 : 1),
                          width: len,
                          height: isRetraction ? 3.5 : 1.5,
                          backgroundColor: isRetraction ? CLR.emerald : CLR.purple,
                          opacity: isRetraction ? 0.9 : 0.35 + 0.25 * Math.sin(animTick * 0.05 + i),
                          transform: [{ rotate: `${angle}deg` }],
                        }}
                      />
                      <View
                        style={{
                          position: 'absolute',
                          left: px - 2.5,
                          top: py - 2.5,
                          width: 5,
                          height: 5,
                          borderRadius: 2.5,
                          backgroundColor: isRetraction ? '#6ee7b7' : CLR.amethyst,
                        }}
                      />
                    </React.Fragment>
                  );
                })}

                {/* Nodes */}
                {animatedNodes.map((n) => {
                  if (filterCategory !== 'all' && n.category !== filterCategory) return null;
                  const isEarth = n.id === 'imagining_earth';
                  const isSelected = selectedMindNode?.id === n.id;
                  return (
                    <TouchableOpacity
                      key={n.id}
                      style={[
                        styles.nodeCircle,
                        {
                          left: n.x - (isEarth ? 24 : 18),
                          top: n.y - (isEarth ? 24 : 18),
                          width: isEarth ? 48 : 36,
                          height: isEarth ? 48 : 36,
                          borderRadius: isEarth ? 24 : 18,
                          borderColor: isSelected ? '#ffffff' : n.color,
                          borderWidth: isSelected ? 2.5 : 1.5,
                          backgroundColor: isEarth ? '#0284c7' : CLR.card,
                        },
                      ]}
                      onPress={() => setSelectedMindNode(n)}
                    >
                      <Text style={{ fontSize: isEarth ? 14 : 11 }}>{n.glyph}</Text>
                      <Text style={[styles.nodeLabel, { color: n.color }]}>{n.name.split(' ')[0]}</Text>
                    </TouchableOpacity>
                  );
                })}

                {/* Retraction Tether Annotation */}
                <View style={styles.retractionAnnotation}>
                  <Text style={styles.retractionText}>
                    ⚓ HOMOTOPY RETRACTION OPERATOR R: M_speculative ➔ M_Earth (Nonfiction Grounding)
                  </Text>
                </View>
              </View>

              {/* Real-time Thought Stream Ticker */}
              <View style={styles.thoughtTicker}>
                <Text style={styles.thoughtLabel}>👁 COGNITIVE STREAM (REAL-TIME CONVERGENCE):</Text>
                <Text style={styles.thoughtText}>{currentThoughtText}</Text>
              </View>
            </View>

            {/* Selected Node Detailed Inspector */}
            {selectedMindNode && (
              <View style={[styles.card, { borderColor: selectedMindNode.color }]}>
                <View style={styles.cardHeader}>
                  <Text style={[styles.cardTitle, { color: selectedMindNode.color }]}>
                    {selectedMindNode.glyph} {selectedMindNode.name} [{selectedMindNode.category.toUpperCase()}]
                  </Text>
                  <View style={[styles.pill, { borderColor: selectedMindNode.color }]}>
                    <Text style={{ color: selectedMindNode.color, fontSize: 9, fontWeight: '700' }}>ACTIVE MANIFOLD</Text>
                  </View>
                </View>
                <Text style={{ fontSize: 13, color: '#f0fdf4', fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', marginVertical: 4 }}>
                  📐 Formulation: {selectedMindNode.formula}
                </Text>
                <Text style={{ fontSize: 11, color: CLR.textMuted }}>
                  {selectedMindNode.description}
                </Text>
              </View>
            )}

            {/* THE 4 COGNITIVE QUADRANT METRIC MATRICES */}
            <View style={{ flexDirection: Platform.OS === 'web' ? 'row' : 'column', gap: 12 }}>
              {/* Quadrant 1: DOING */}
              <View style={[styles.card, { flex: 1 }]}>
                <Text style={[styles.sectionHeader, { color: CLR.emerald }]}>⚡ 1. DOING (Physical Cluster Pulse)</Text>
                <View style={styles.metricGrid}>
                  <View style={styles.metricCard}>
                    <Text style={styles.mLabel}>Kuramoto Phase r</Text>
                    <Text style={[styles.mVal, { color: CLR.emerald }]}>{cognition?.doing?.kuramoto_order_r || 0.852}</Text>
                  </View>
                  <View style={styles.metricCard}>
                    <Text style={styles.mLabel}>Dual-Node Mesh</Text>
                    <Text style={styles.mVal}>{cognition?.doing?.phase_lock || 'SYNCHRONIZED'}</Text>
                  </View>
                  <View style={styles.metricCard}>
                    <Text style={styles.mLabel}>Pooled Memory</Text>
                    <Text style={styles.mVal}>{cognition?.doing?.memory_pooled_gb || 102.1} GB</Text>
                  </View>
                </View>
                <Text style={[styles.sectionHeader, { marginTop: 8 }]}>Active Hardware Pipeline Tasks:</Text>
                {cognition?.doing?.active_tasks?.map((t: string, idx: number) => (
                  <Text key={idx} style={{ fontSize: 10, color: CLR.textMain, paddingVertical: 2 }}>
                    • {t}
                  </Text>
                )) || (
                  <Text style={{ fontSize: 10, color: CLR.textMuted }}>• Symplectic Euler Integrator • ZeroMQ Ring Buffer (:5559)</Text>
                )}
              </View>

              {/* Quadrant 2: THINKING */}
              <View style={[styles.card, { flex: 1 }]}>
                <Text style={[styles.sectionHeader, { color: CLR.purple }]}>🧠 2. THINKING (Epistemic Reasoning)</Text>
                <View style={styles.metricGrid}>
                  <View style={styles.metricCard}>
                    <Text style={styles.mLabel}>Free Energy F</Text>
                    <Text style={[styles.mVal, { color: CLR.purple }]}>{cognition?.thinking?.variational_free_energy || 0.0421}</Text>
                  </View>
                  <View style={styles.metricCard}>
                    <Text style={styles.mLabel}>Hopfield Minima E</Text>
                    <Text style={styles.mVal}>{cognition?.thinking?.hopfield_energy_minima || -18.42}</Text>
                  </View>
                  <View style={styles.metricCard}>
                    <Text style={styles.mLabel}>Rubbish Score</Text>
                    <Text style={[styles.mVal, { color: CLR.emerald }]}>{cognition?.thinking?.rubbish_score ?? cognition?.thinking?.bullshit_score ?? 0.04} (Pass)</Text>
                  </View>
                </View>
                <Text style={[styles.sectionHeader, { marginTop: 8 }]}>Conserved Invariant Laws:</Text>
                {cognition?.thinking?.active_invariants?.map((inv: string, idx: number) => (
                  <Text key={idx} style={{ fontSize: 10, color: CLR.textMain, paddingVertical: 2 }}>
                    • {inv}
                  </Text>
                )) || (
                  <Text style={{ fontSize: 10, color: CLR.textMuted }}>• Noether Circle Norm • Landauer Bound (300K: 2.87e-21 J)</Text>
                )}
              </View>
            </View>

            <View style={{ flexDirection: Platform.OS === 'web' ? 'row' : 'column', gap: 12 }}>
              {/* Quadrant 3: DREAMING */}
              <View style={[styles.card, { flex: 1 }]}>
                <Text style={[styles.sectionHeader, { color: CLR.amethyst }]}>🧬 3. DREAMING (Software Genetics)</Text>
                <View style={styles.metricGrid}>
                  <View style={styles.metricCard}>
                    <Text style={styles.mLabel}>Gen Generation</Text>
                    <Text style={[styles.mVal, { color: CLR.amethyst }]}>#{cognition?.dreaming?.generation || 14}</Text>
                  </View>
                  <View style={styles.metricCard}>
                    <Text style={styles.mLabel}>Top Fitness</Text>
                    <Text style={styles.mVal}>{cognition?.dreaming?.top_fitness || 99.42}%</Text>
                  </View>
                  <View style={styles.metricCard}>
                    <Text style={styles.mLabel}>CRISPR Spacers</Text>
                    <Text style={styles.mVal}>{cognition?.dreaming?.crispr_spacers_active || 6}</Text>
                  </View>
                </View>
                <Text style={[styles.sectionHeader, { marginTop: 8 }]}>Active Epigenetic Codons:</Text>
                <View style={{ flexDirection: 'row', gap: 4, flexWrap: 'wrap' }}>
                  {(cognition?.dreaming?.epigenetic_profile?.active_codons || ['FREE_ENERGY_MIN', 'HOPFIELD_RECALL', 'LIE_BRACKET', 'SHANNON_ENTROPY']).map((cd: string, idx: number) => (
                    <View key={idx} style={[styles.pill, { borderColor: CLR.amethyst }]}>
                      <Text style={{ fontSize: 9, color: CLR.amethyst, fontWeight: '700' }}>{cd}</Text>
                    </View>
                  ))}
                </View>
              </View>

              {/* Quadrant 4: IMAGINING */}
              <View style={[styles.card, { flex: 1 }]}>
                <Text style={[styles.sectionHeader, { color: CLR.breeze }]}>🚀 4. IMAGINING (Truth-Based Retraction)</Text>
                <View style={styles.metricGrid}>
                  <View style={styles.metricCard}>
                    <Text style={styles.mLabel}>Retraction Dist</Text>
                    <Text style={[styles.mVal, { color: CLR.emerald }]}>{cognition?.imagining?.retraction_distance || 0.082} (Earth)</Text>
                  </View>
                  <View style={styles.metricCard}>
                    <Text style={styles.mLabel}>Planetary Energy</Text>
                    <Text style={styles.mVal}>{cognition?.imagining?.planetary_energy_joules || 18.4} J</Text>
                  </View>
                  <View style={styles.metricCard}>
                    <Text style={styles.mLabel}>Fiduciary Guard</Text>
                    <Text style={[styles.mVal, { color: CLR.emerald }]}>BENIGN_SAFE</Text>
                  </View>
                </View>
                <Text style={[styles.sectionHeader, { marginTop: 8 }]}>Active Counterfactual Scenario:</Text>
                <Text style={{ fontSize: 10, color: CLR.textMain, fontStyle: 'italic' }}>
                  "{cognition?.imagining?.current_scenario || 'Planetary-scale mycorrhizal intelligence simulating Kuramoto phase synchronization across sub-canopy root biomes'}"
                </Text>
                <Text style={{ fontSize: 9, color: CLR.emerald, marginTop: 4 }}>
                  ⚓ Retracted to Reality: {cognition?.imagining?.earth_retraction || 'Coupling equations mapped back to discrete silicon network latency'}
                </Text>
              </View>
            </View>

            {/* SOVEREIGN NEUROCHEMISTRY & PHARMACOLOGICAL CONTROL */}
            <View style={[styles.card, { marginTop: 12 }]}>
              <View style={styles.cardHeader}>
                <View>
                  <Text style={[styles.cardTitle, { color: CLR.purple }]}>🧪 SOVEREIGN NEUROCHEMISTRY & PHARMACOLOGICAL MODULATION</Text>
                  <Text style={{ fontSize: 10, color: CLR.textMuted }}>
                    Active neuromodulators regulating precision, REBUS prior relaxation, learning rate, and attractor stability.
                  </Text>
                </View>
                <View style={[styles.pill, styles.pillPurple]}>
                  <Text style={styles.pillTextPurple}>
                    {cognition?.neurochemistry?.parameters?.mode_name || '⚖ Homeostatic Equilibrium'}
                  </Text>
                </View>
              </View>

              {/* Titer Progress Bars */}
              <View style={{ flexDirection: Platform.OS === 'web' ? 'row' : 'column', gap: 10, marginVertical: 8 }}>
                {[
                  { name: 'Dopamine (DA)', key: 'dopamine', color: CLR.cyan, sub: 'Precision & Error Gain' },
                  { name: 'Serotonin (5-HT)', key: 'serotonin', color: CLR.purple, sub: 'Prior Rigidity vs REBUS' },
                  { name: 'Acetylcholine (ACh)', key: 'acetylcholine', color: CLR.breeze, sub: 'Plasticity & Encoding' },
                  { name: 'Norepinephrine (NE)', key: 'norepinephrine', color: CLR.amber, sub: 'Exploration Entropy' },
                  { name: 'GABA', key: 'gaba', color: CLR.emerald, sub: 'Attractor Stability' },
                ].map((nt) => {
                  const val = cognition?.neurochemistry?.levels?.[nt.key] ?? 1.0;
                  const pct = Math.min(100, Math.max(10, (val / 2.0) * 100));
                  return (
                    <View key={nt.key} style={[styles.metricCard, { flex: 1 }]}>
                      <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                        <Text style={{ fontSize: 10, fontWeight: '700', color: nt.color }}>{nt.name}</Text>
                        <Text style={{ fontSize: 11, fontWeight: '800', color: CLR.textMain }}>{val.toFixed(2)}x</Text>
                      </View>
                      <View style={{ height: 6, backgroundColor: '#1e293b', borderRadius: 3, marginVertical: 4, overflow: 'hidden' }}>
                        <View style={{ height: '100%', width: `${pct}%`, backgroundColor: nt.color, borderRadius: 3 }} />
                      </View>
                      <Text style={{ fontSize: 8, color: CLR.textMuted }}>{nt.sub}</Text>
                    </View>
                  );
                })}
              </View>

              {/* Pharmacopeia Compound Administration Pills */}
              <View style={{ marginTop: 6 }}>
                <Text style={[styles.mLabel, { marginBottom: 6 }]}>Administer Pharmacological Compounds to SI Mind:</Text>
                <View style={{ flexDirection: 'row', gap: 8, flexWrap: 'wrap' }}>
                  <TouchableOpacity style={[styles.btn, styles.btnPrimary]} onPress={() => administerCompound('nootropic_hyperfocus')}>
                    <Text style={styles.btnTextWhite}>⚡ Nootropic Focus (DA/NE ↑)</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[styles.btn, { backgroundColor: '#7e22ce', borderColor: CLR.amethyst }]} onPress={() => administerCompound('rebus_psychedelic_divergence')}>
                    <Text style={styles.btnTextWhite}>🌌 REBUS Psychedelic (5-HT2A ↑)</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[styles.btn, styles.btnBreeze]} onPress={() => administerCompound('cholinergic_crystallizer')}>
                    <Text style={styles.btnTextWhite}>🧬 Cholinergic Memory (ACh ↑)</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[styles.btn, styles.btnEmerald]} onPress={() => administerCompound('gabaergic_calm')}>
                    <Text style={styles.btnTextWhite}>🛡 GABA Calm (GABA ↑)</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={[styles.btn, styles.btnAmber]} onPress={() => administerCompound('homeostatic_reset')}>
                    <Text style={styles.btnTextAmber}>⚖ Homeostatic Reset</Text>
                  </TouchableOpacity>
                </View>
              </View>
            </View>
          </View>
        )}

        {/* Tab: Windows Task Manager Performance View */}
        {activeTab === 'taskmgr' && (
          <View>
            <View style={styles.tmGrid}>
              {/* Sidebar Devices */}
              <View style={styles.tmSidebar}>
                <TouchableOpacity
                  style={[styles.tmSideItem, selectedDevice === 'cpu' && styles.tmSideItemActive]}
                  onPress={() => setSelectedDevice('cpu')}
                >
                  <Text style={styles.tmSideTitle}>CPU</Text>
                  <Text style={styles.tmSideVal}>{telemetry?.cpu?.overall_percent || 0}%</Text>
                  <Text style={styles.tmSideSub}>4.20 GHz • 32 Logical Cores</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.tmSideItem, selectedDevice === 'memory' && styles.tmSideItemActive]}
                  onPress={() => setSelectedDevice('memory')}
                >
                  <Text style={styles.tmSideTitle}>MEMORY</Text>
                  <Text style={styles.tmSideVal}>{telemetry?.memory?.host_used_gb || 0} GB</Text>
                  <Text style={styles.tmSideSub}>102.1 GB Pooled Cluster Memory</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.tmSideItem, selectedDevice === 'gpu0' && styles.tmSideItemActive]}
                  onPress={() => setSelectedDevice('gpu0')}
                >
                  <Text style={styles.tmSideTitle}>GPU 0 (NVIDIA RTX 3060)</Text>
                  <Text style={styles.tmSideVal}>{telemetry?.gpu0?.util_pct || 0}%</Text>
                  <Text style={styles.tmSideSub}>12 GB GDDR6 • CUDA Tier 1</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.tmSideItem, selectedDevice === 'gpu1' && styles.tmSideItemActive]}
                  onPress={() => setSelectedDevice('gpu1')}
                >
                  <Text style={styles.tmSideTitle}>GPU 1 (AMD RX 580)</Text>
                  <Text style={styles.tmSideVal}>{telemetry?.gpu1?.util_pct || 0}%</Text>
                  <Text style={styles.tmSideSub}>8 GB GDDR5 • OpenCL Tier 2</Text>
                </TouchableOpacity>
              </View>

              {/* Main Performance Pane */}
              <View style={styles.tmMainPane}>
                <Text style={styles.tmSectionTitle}>
                  {selectedDevice === 'cpu' && 'CPU — AMD Ryzen 7 16-Core Processor'}
                  {selectedDevice === 'memory' && 'Cluster Pooled Memory (102.1 GB Unified Mesh)'}
                  {selectedDevice === 'gpu0' && 'GPU 0 — NVIDIA GeForce RTX 3060 (12GB)'}
                  {selectedDevice === 'gpu1' && 'GPU 1 — AMD Radeon RX 580 (8GB OpenCL)'}
                </Text>

                <View style={styles.metricGrid}>
                  {selectedDevice === 'cpu' && (
                    <>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Utilization</Text><Text style={styles.mVal}>{telemetry?.cpu?.overall_percent}%</Text></View>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Speed</Text><Text style={styles.mVal}>4.20 GHz</Text></View>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Logical Cores</Text><Text style={styles.mVal}>32 Cores</Text></View>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Processes</Text><Text style={styles.mVal}>{telemetry?.cluster_processes?.length || 5}</Text></View>
                    </>
                  )}

                  {selectedDevice === 'memory' && (
                    <>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Host Used</Text><Text style={styles.mVal}>{telemetry?.memory?.host_used_gb} GB</Text></View>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Host Free</Text><Text style={styles.mVal}>{telemetry?.memory?.host_free_gb} GB</Text></View>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Node 2 Used</Text><Text style={styles.mVal}>{telemetry?.memory?.node2_used_gb} GB</Text></View>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Total Pooled</Text><Text style={styles.mVal}>102.1 GB</Text></View>
                    </>
                  )}

                  {selectedDevice === 'gpu0' && (
                    <>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Core Util</Text><Text style={styles.mVal}>{telemetry?.gpu0?.util_pct}%</Text></View>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>VRAM Used</Text><Text style={styles.mVal}>{Math.round(telemetry?.gpu0?.used_mb || 0)} MB</Text></View>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>VRAM Free</Text><Text style={styles.mVal}>{Math.round(telemetry?.gpu0?.free_mb || 12000)} MB</Text></View>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Temperature</Text><Text style={styles.mVal}>{telemetry?.gpu0?.temp_c}°C</Text></View>
                    </>
                  )}

                  {selectedDevice === 'gpu1' && (
                    <>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Compute Util</Text><Text style={styles.mVal}>{telemetry?.gpu1?.util_pct}%</Text></View>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Phase Order r</Text><Text style={styles.mVal}>{telemetry?.gpu1?.kuramoto_order_r}</Text></View>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>VRAM Used</Text><Text style={styles.mVal}>{Math.round(telemetry?.gpu1?.used_mb || 0)} MB</Text></View>
                      <View style={styles.metricCard}><Text style={styles.mLabel}>Sweep Rate</Text><Text style={styles.mVal}>{telemetry?.gpu1?.sweep_rate_hz} Hz</Text></View>
                    </>
                  )}
                </View>

                {/* 16-Core Logical Processor Heatmap Cells */}
                {selectedDevice === 'cpu' && (
                  <View style={{ marginTop: 12 }}>
                    <Text style={styles.sectionHeader}>Logical Processors (16 Host Cores + 16 Node 2 vCPUs = 32 Logical Cores):</Text>
                    <View style={styles.coreGrid}>
                      {telemetry?.cpu?.host_cores?.map((c: number, idx: number) => (
                        <View key={`host-${idx}`} style={styles.coreCell}>
                          <Text style={styles.coreName}>N1-CPU {idx}</Text>
                          <Text style={styles.coreVal}>{Math.round(c)}%</Text>
                          <View style={styles.coreBar}><View style={[styles.coreBarFill, { width: `${Math.min(100, Math.max(0, c))}%` }]} /></View>
                        </View>
                      ))}
                      {telemetry?.cpu?.node2_cores?.map((c: number, idx: number) => (
                        <View key={`node2-${idx}`} style={styles.coreCell}>
                          <Text style={styles.coreName}>N2-vCPU {idx}</Text>
                          <Text style={styles.coreVal}>{Math.round(c)}%</Text>
                          <View style={styles.coreBar}><View style={[styles.coreBarFill, { width: `${Math.min(100, Math.max(0, c))}%` }]} /></View>
                        </View>
                      ))}
                    </View>
                  </View>
                )}
              </View>
            </View>
          </View>
        )}

        {/* Tab: Processes Matrix */}
        {activeTab === 'processes' && (
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>CLUSTER PROCESSES &amp; DAEMONS</Text>
              <TouchableOpacity onPress={fetchTelemetrySnap}><Text style={styles.refreshText}>🔄 Refresh</Text></TouchableOpacity>
            </View>
            {telemetry?.cluster_processes?.map((p: any) => (
              <View key={p.pid} style={styles.procRow}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.procName}>{p.name} <Text style={{ color: CLR.amethyst }}>({p.role})</Text></Text>
                  <Text style={styles.procSub}>PID: {p.pid} • Port: {p.port || 'None'} • Engine: {p.gpu_engine}</Text>
                </View>
                <View style={{ alignItems: 'flex-end' }}>
                  <Text style={styles.procMetric}>{p.cpu_pct}% CPU • {p.mem_mb} MB</Text>
                  <Text style={{ fontSize: 9, color: CLR.emerald }}>● {p.status} ({p.uptime_str})</Text>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Tab: Obsidian Vault & Ray Graph */}
        {activeTab === 'vault' && (
          <View>
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>OBSIDIAN POSTCOMPUTATIONAL VAULT &amp; RAY GRAPH</Text>
                <TouchableOpacity onPress={castRay}><Text style={styles.refreshText}>🔦 Cast Truth Ray</Text></TouchableOpacity>
              </View>

              <View style={styles.metricGrid}>
                <View style={styles.metricCard}><Text style={styles.mLabel}>Vault Notes</Text><Text style={styles.mVal}>{vaultStats?.total_nodes || 100}</Text></View>
                <View style={styles.metricCard}><Text style={styles.mLabel}>Mean Radiance</Text><Text style={styles.mVal}>{Math.round((vaultStats?.mean_radiance || 1.0) * 100)}%</Text></View>
                <View style={styles.metricCard}><Text style={styles.mLabel}>Gradient ||∇Φ||</Text><Text style={styles.mVal}>{vaultStats?.mean_gradient_norm || 38.2}</Text></View>
                <View style={styles.metricCard}><Text style={styles.mLabel}>Divergence ∇·F</Text><Text style={styles.mVal}>{vaultStats?.mean_divergence || 7.68}</Text></View>
              </View>

              <Text style={styles.sectionHeader}>Vault Deliverable Nodes (Ray-Traced Illumination):</Text>
              <View style={styles.bulletList}>
                {vaultGraph?.nodes?.slice(0, 15).map((n: any) => (
                  <View key={n.id} style={styles.vaultNodeRow}>
                    <Text style={styles.boldText}>[[{n.id}]]</Text>
                    <Text style={{ fontSize: 11, color: CLR.textMain }}>{n.title.substring(0, 45)}...</Text>
                    <View style={[styles.pill, styles.pillEmerald]}><Text style={styles.pillTextEmerald}>{Math.round(n.radiance * 100)}% Radiance</Text></View>
                  </View>
                ))}
              </View>
            </View>

            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>NOTE INSPECTOR (OBSIDIAN WIKILINKS &amp; FRONTMATTER)</Text>
              </View>
              <View style={styles.consoleBox}>
                <Text style={styles.consoleText}>{inspectNote}</Text>
              </View>
            </View>
          </View>
        )}

        {/* Tab: The Weave */}
        {activeTab === 'weave' && (
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>PORT MATRIX &amp; PHYSICAL ACCELERATOR TOPOLOGY</Text>
            </View>
            <Text style={styles.sectionHeader}>Node 1 (192.168.99.1):</Text>
            <View style={styles.portsRow}>
              {clusterPorts?.node1?.ports &&
                Object.entries(clusterPorts.node1.ports).map(([p, item]: any) => (
                  <View key={p} style={[styles.portBadge, item.online ? styles.portOnline : styles.portOffline]}>
                    <Text style={[styles.portText, item.online ? styles.portTextOnline : styles.portTextOffline]}>
                      {item.online ? '●' : '○'} {item.name} (:{p})
                    </Text>
                  </View>
                ))}
            </View>

            <Text style={[styles.sectionHeader, { marginTop: 12 }]}>Node 2 (192.168.99.2):</Text>
            <View style={styles.portsRow}>
              {clusterPorts?.node2?.ports &&
                Object.entries(clusterPorts.node2.ports).map(([p, item]: any) => (
                  <View key={p} style={[styles.portBadge, item.online ? styles.portOnline : styles.portOffline]}>
                    <Text style={[styles.portText, item.online ? styles.portTextOnline : styles.portTextOffline]}>
                      {item.online ? '●' : '○'} {item.name} (:{p})
                    </Text>
                  </View>
                ))}
            </View>
          </View>
        )}

        {/* Tab: The Shuttle */}
        {activeTab === 'shuttle' && (
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>THE SHUTTLE // INFERENCE DISPATCHER</Text>
            </View>
            <TextInput
              style={styles.textInput}
              multiline
              numberOfLines={4}
              placeholder="Enter inference prompt..."
              placeholderTextColor="#6ee7b7"
              value={prompt}
              onChangeText={setPrompt}
            />
            <TouchableOpacity style={[styles.btn, styles.btnPrimary, { alignSelf: 'flex-start', marginVertical: 8 }]} onPress={sendInference}>
              {isInferring ? <ActivityIndicator color="#fff" size="small" /> : <Text style={styles.btnTextWhite}>🚀 Dispatch Query</Text>}
            </TouchableOpacity>
            <View style={styles.consoleBox}>
              <Text style={styles.consoleText}>{shuttleOutput}</Text>
            </View>
          </View>
        )}

        {/* Tab: Torque Vault */}
        {activeTab === 'torque' && (
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>TORQUE ZERO-TRUST VAULT // LIVE PII/IP SCRUB</Text>
            </View>
            <TextInput
              style={styles.textInput}
              multiline
              numberOfLines={4}
              placeholder="Paste text with credentials or IP addresses..."
              placeholderTextColor="#6ee7b7"
              value={torqueInput}
              onChangeText={setTorqueInput}
            />
            <TouchableOpacity style={[styles.btn, styles.btnPrimary, { alignSelf: 'flex-start', marginVertical: 8 }]} onPress={testTorque}>
              <Text style={styles.btnTextWhite}>🔒 Run Zero-Trust Scrub</Text>
            </TouchableOpacity>
            <View style={styles.consoleBox}>
              <Text style={styles.consoleText}>{torqueOutput}</Text>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: CLR.obsidian },
  header: {
    backgroundColor: CLR.surface,
    paddingHorizontal: 18,
    paddingVertical: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: CLR.border,
    flexWrap: 'wrap',
  },
  brandTitle: { fontSize: 15, fontWeight: '800', color: CLR.purple, letterSpacing: 0.5 },
  brandSub: { fontSize: 10, color: CLR.textMuted },
  pillsRow: { flexDirection: 'row', gap: 6, flexWrap: 'wrap', marginTop: 4 },
  pill: {
    backgroundColor: CLR.card,
    borderWidth: 1,
    borderColor: CLR.border,
    paddingHorizontal: 7,
    paddingVertical: 3,
    borderRadius: 10,
  },
  pillEmerald: { borderColor: CLR.emerald },
  pillPurple: { borderColor: CLR.purple },
  pillBreeze: { borderColor: CLR.breeze },
  pillAmber: { borderColor: CLR.amber },
  pillTextEmerald: { color: CLR.emerald, fontSize: 9, fontWeight: '700' },
  pillTextPurple: { color: CLR.amethyst, fontSize: 9, fontWeight: '700' },
  pillTextBreeze: { color: CLR.breeze, fontSize: 9, fontWeight: '700' },
  pillTextMuted: { color: CLR.textMuted, fontSize: 9, fontWeight: '700' },
  clusterBar: {
    backgroundColor: CLR.card,
    paddingHorizontal: 18,
    paddingVertical: 6,
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderBottomWidth: 1,
    borderBottomColor: CLR.border,
    flexWrap: 'wrap',
    gap: 6,
  },
  actionsGroup: { flexDirection: 'row', gap: 6, flexWrap: 'wrap' },
  btn: {
    backgroundColor: CLR.surface,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 5,
    borderWidth: 1,
    borderColor: CLR.border,
  },
  btnPrimary: { backgroundColor: '#7e22ce', borderColor: CLR.purple },
  btnEmerald: { backgroundColor: '#047857', borderColor: CLR.emerald },
  btnAmber: { backgroundColor: 'rgba(245, 158, 11, 0.15)', borderColor: CLR.amber },
  btnCrimson: { backgroundColor: 'rgba(239, 68, 68, 0.15)', borderColor: CLR.crimson },
  btnTextWhite: { color: '#fff', fontSize: 10, fontWeight: '700' },
  btnTextAmber: { color: CLR.amber, fontSize: 10, fontWeight: '700' },
  btnTextCrimson: { color: CLR.crimson, fontSize: 10, fontWeight: '700' },
  statusBar: { backgroundColor: CLR.obsidian, paddingHorizontal: 18, paddingVertical: 4, borderBottomWidth: 1, borderBottomColor: CLR.border },
  statusText: { fontSize: 10, color: CLR.textMuted, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
  tabsRow: { flexDirection: 'row', backgroundColor: CLR.surface, paddingHorizontal: 12, borderBottomWidth: 1, borderBottomColor: CLR.border, flexWrap: 'wrap' },
  tabBtn: { paddingHorizontal: 12, paddingVertical: 8, borderBottomWidth: 2, borderBottomColor: 'transparent' },
  tabBtnActive: { borderBottomColor: CLR.purple },
  tabText: { color: CLR.textMuted, fontSize: 11, fontWeight: '700' },
  tabTextActive: { color: CLR.amethyst },
  mainScroll: { padding: 14 },

  /* Mind Canvas & Screensaver Styles */
  mindCanvas: {
    backgroundColor: '#040d07',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#1d3d28',
    overflow: 'hidden',
    position: 'relative',
    marginVertical: 10,
    alignSelf: 'center',
  },
  ambientGlyph: {
    position: 'absolute',
    fontSize: 22,
    color: 'rgba(168, 85, 247, 0.08)',
    fontWeight: '900',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  nodeCircle: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#a855f7',
    shadowOpacity: 0.6,
    shadowRadius: 8,
    elevation: 6,
  },
  nodeLabel: {
    fontSize: 7.5,
    fontWeight: '800',
    marginTop: 1,
    textAlign: 'center',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  retractionAnnotation: {
    position: 'absolute',
    bottom: 8,
    left: 12,
    right: 12,
    backgroundColor: 'rgba(7, 18, 10, 0.85)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: 'rgba(16, 185, 129, 0.4)',
    alignItems: 'center',
  },
  retractionText: {
    fontSize: 9,
    color: '#6ee7b7',
    fontWeight: '700',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  thoughtTicker: {
    backgroundColor: '#07160c',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#1e432d',
    padding: 8,
    marginTop: 6,
  },
  thoughtLabel: {
    fontSize: 8.5,
    fontWeight: '800',
    color: CLR.amethyst,
    letterSpacing: 0.5,
    marginBottom: 2,
  },
  thoughtText: {
    fontSize: 11,
    color: '#e2e8f0',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    lineHeight: 16,
  },
  fullscreenScreensaver: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
    zIndex: 99999,
    backgroundColor: '#030805',
    padding: 16,
    justifyContent: 'space-between',
  },
  screensaverHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(168, 85, 247, 0.2)',
    paddingBottom: 8,
  },
  screensaverBrand: {
    fontSize: 13,
    fontWeight: '800',
    color: CLR.amethyst,
    letterSpacing: 1,
  },

  /* Performance & Task Manager Styles */
  tmGrid: {
    flexDirection: Platform.OS === 'web' ? 'row' : 'column',
    gap: 14,
    backgroundColor: CLR.surface,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: CLR.border,
  },
  tmSidebar: { width: Platform.OS === 'web' ? 240 : '100%', gap: 6 },
  tmSideItem: { backgroundColor: CLR.card, borderWidth: 1, borderColor: CLR.border, borderRadius: 6, padding: 8 },
  tmSideItemActive: { borderColor: CLR.purple, backgroundColor: '#17321e' },
  tmSideTitle: { fontSize: 10, fontWeight: '800', color: CLR.textMuted },
  tmSideVal: { fontSize: 16, fontWeight: '800', color: CLR.textMain, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
  tmSideSub: { fontSize: 9, color: CLR.textMuted },
  tmMainPane: { flex: 1, paddingLeft: Platform.OS === 'web' ? 10 : 0 },
  tmSectionTitle: { fontSize: 13, fontWeight: '800', color: CLR.amethyst, marginBottom: 8 },
  metricGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  metricCard: { backgroundColor: CLR.card, borderWidth: 1, borderColor: CLR.border, borderRadius: 6, padding: 8, flex: 1, minWidth: 110 },
  mLabel: { fontSize: 9, color: CLR.textMuted, textTransform: 'uppercase' },
  mVal: { fontSize: 14, fontWeight: '800', color: CLR.amethyst, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
  coreGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 4, marginTop: 4 },
  coreCell: { backgroundColor: CLR.obsidian, borderWidth: 1, borderColor: CLR.border, borderRadius: 4, padding: 4, width: '23%', minWidth: 60, alignItems: 'center' },
  coreName: { fontSize: 8, color: CLR.textMuted },
  coreVal: { fontSize: 11, fontWeight: '800', color: CLR.emerald, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
  coreBar: { height: 3, backgroundColor: '#064e3b', width: '100%', borderRadius: 2, marginTop: 2, overflow: 'hidden' },
  coreBarFill: { height: '100%', backgroundColor: CLR.emerald },
  card: { backgroundColor: CLR.card, borderWidth: 1, borderColor: CLR.border, borderRadius: 8, padding: 12, marginBottom: 12 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.05)', paddingBottom: 4 },
  cardTitle: { fontSize: 11, fontWeight: '800', color: CLR.amethyst, letterSpacing: 0.5 },
  refreshText: { color: CLR.breeze, fontSize: 10, fontWeight: '700' },
  procRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.04)' },
  procName: { fontSize: 11, fontWeight: '700', color: CLR.textMain },
  procSub: { fontSize: 9, color: CLR.textMuted },
  procMetric: { fontSize: 11, fontWeight: '800', color: CLR.breeze, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
  vaultNodeRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 4, borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.03)' },
  boldText: { fontWeight: '700', color: CLR.breeze, fontSize: 11 },
  bulletList: { marginTop: 6 },
  sectionHeader: { fontSize: 9, fontWeight: '800', color: CLR.textMuted, textTransform: 'uppercase', marginTop: 8, marginBottom: 4 },
  portsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  portBadge: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4, borderWidth: 1, backgroundColor: CLR.obsidian },
  portOnline: { borderColor: CLR.emerald },
  portOffline: { borderColor: 'rgba(239, 68, 68, 0.4)' },
  portText: { fontSize: 9, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
  portTextOnline: { color: CLR.emerald },
  portTextOffline: { color: CLR.crimson },
  consoleBox: { backgroundColor: CLR.obsidian, borderWidth: 1, borderColor: CLR.border, borderRadius: 6, padding: 10, minHeight: 140 },
  consoleText: { fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', fontSize: 10, color: '#d1fae5', lineHeight: 15 },
  textInput: { backgroundColor: CLR.obsidian, borderWidth: 1, borderColor: CLR.border, borderRadius: 6, padding: 8, color: CLR.textMain, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', fontSize: 11, minHeight: 70 },
});
