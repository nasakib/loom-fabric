import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  Dimensions
} from 'react-native';

// Antigravity Design System Constants
const TOKENS = {
  bgBase: '#05080e',
  bgSurface: '#0a0f18',
  bgCard: 'rgba(13, 20, 32, 0.85)',
  thinkerCyan: '#00e5ff',
  deciderEmerald: '#10b981',
  coherencePurple: '#a855f7',
  textPrimary: '#f8fafc',
  textSecondary: '#94a3b8',
  textMuted: '#64748b',
  borderSubtle: 'rgba(255, 255, 255, 0.08)',
  borderAccent: 'rgba(0, 229, 255, 0.3)',
};

export default function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'thinker' | 'decider' | 'telemetry'>('overview');
  const [coherence, setCoherence] = useState(0.992);
  const [resonance, setResonance] = useState(0.984);
  const [cycle, setCycle] = useState(1420);
  const [node1Load, setNode1Load] = useState(28.4);
  const [node2Load, setNode2Load] = useState(34.2);

  // Micro-telemetry tick simulation
  useEffect(() => {
    const timer = setInterval(() => {
      setCycle(c => c + 1);
      setCoherence(c => Math.min(0.999, Math.max(0.970, c + (Math.random() - 0.49) * 0.003)));
      setResonance(r => Math.min(0.999, Math.max(0.950, r + (Math.random() - 0.49) * 0.004)));
      setNode1Load(+(24 + Math.random() * 12).toFixed(1));
      setNode2Load(+(30 + Math.random() * 10).toFixed(1));
    }, 2400);
    return () => clearInterval(timer);
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={TOKENS.bgBase} />

      {/* Top Header */}
      <View style={styles.header}>
        <View style={styles.brandRow}>
          <View style={styles.orb} />
          <View>
            <Text style={styles.brandTitle}>
              ClothOS <Text style={{ color: TOKENS.thinkerCyan }}>Dyad</Text>
            </Text>
            <Text style={styles.brandSub}>Tailscale Mesh &bull; Node 1 &amp; Node 2</Text>
          </View>
        </View>
        <View style={styles.cycleBadge}>
          <Text style={styles.cycleBadgeText}>CYCLE #{cycle}</Text>
        </View>
      </View>

      {/* Main Content Area */}
      <ScrollView style={styles.content} contentContainerStyle={{ paddingBottom: 100 }}>
        {activeTab === 'overview' && (
          <OverviewScreen
            coherence={coherence}
            resonance={resonance}
            node1Load={node1Load}
            node2Load={node2Load}
            onStep={() => setCycle(c => c + 1)}
          />
        )}
        {activeTab === 'thinker' && <ThinkerScreen node1Load={node1Load} />}
        {activeTab === 'decider' && <DeciderScreen node2Load={node2Load} />}
        {activeTab === 'telemetry' && <TelemetryScreen />}
      </ScrollView>

      {/* Glassmorphic Bottom Tab Bar */}
      <View style={styles.tabBar}>
        <TabButton
          label="Dyad"
          icon="🌐"
          active={activeTab === 'overview'}
          onPress={() => setActiveTab('overview')}
        />
        <TabButton
          label="Thinker"
          icon="🌌"
          active={activeTab === 'thinker'}
          onPress={() => setActiveTab('thinker')}
        />
        <TabButton
          label="Decider"
          icon="⚖️"
          active={activeTab === 'decider'}
          onPress={() => setActiveTab('decider')}
        />
        <TabButton
          label="Cores"
          icon="📊"
          active={activeTab === 'telemetry'}
          onPress={() => setActiveTab('telemetry')}
        />
      </View>
    </SafeAreaView>
  );
}

// ---------------- Screen 1: Dyad Overview ----------------
function OverviewScreen({ coherence, resonance, node1Load, node2Load, onStep }: any) {
  return (
    <View style={styles.screenWrapper}>
      {/* Coherence & Resonance Gauge Card */}
      <View style={[styles.card, { borderColor: 'rgba(168, 85, 247, 0.4)' }]}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>DYAD COHERENCE MANIFOLD</Text>
          <Text style={{ color: TOKENS.coherencePurple, fontWeight: '700' }}>C = {coherence.toFixed(3)}</Text>
        </View>
        <View style={styles.gaugeRow}>
          <View style={styles.gaugeCol}>
            <Text style={styles.gaugeBigText}>{(resonance * 100).toFixed(1)}%</Text>
            <Text style={styles.gaugeLabel}>Harmonic Resonance (&Omega;)</Text>
          </View>
          <View style={styles.gaugeDivider} />
          <View style={styles.gaugeCol}>
            <Text style={[styles.gaugeBigText, { color: TOKENS.deciderEmerald }]}>1.24 ms</Text>
            <Text style={styles.gaugeLabel}>Tailscale Mesh Latency</Text>
          </View>
        </View>
        <TouchableOpacity style={styles.stepBtn} onPress={onStep}>
          <Text style={styles.stepBtnText}>⚡ STEP BICAMERAL DYAD</Text>
        </TouchableOpacity>
      </View>

      {/* Node 1: skyTech-Worker Card */}
      <View style={[styles.card, { borderLeftColor: TOKENS.thinkerCyan, borderLeftWidth: 4 }]}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>NODE 1 &bull; SKYTECH-WORKER</Text>
          <Text style={{ color: TOKENS.thinkerCyan, fontSize: 11, fontWeight: '700' }}>PROJECTOR</Text>
        </View>
        <Text style={styles.cardBodyText}>Role: Generative Thinker &bull; Port 8087 (Local Primary)</Text>
        <View style={styles.metricRow}>
          <Text style={styles.metricLabel}>32-Core Load: {node1Load}%</Text>
          <Text style={styles.metricLabel}>&Delta;S: 412.5 J</Text>
        </View>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${node1Load}%`, backgroundColor: TOKENS.thinkerCyan }]} />
        </View>
      </View>

      {/* Node 2: Ryzen7-Head Card */}
      <View style={[styles.card, { borderLeftColor: TOKENS.deciderEmerald, borderLeftWidth: 4 }]}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>NODE 2 &bull; RYZEN7-HEAD</Text>
          <Text style={{ color: TOKENS.deciderEmerald, fontSize: 11, fontWeight: '700' }}>DECIDER</Text>
        </View>
        <Text style={styles.cardBodyText}>Role: Governance Decider &bull; 100.74.98.21:8087 (Mesh)</Text>
        <View style={styles.metricRow}>
          <Text style={styles.metricLabel}>16-Thread Load: {node2Load}%</Text>
          <Text style={[styles.metricLabel, { color: TOKENS.deciderEmerald }]}>Grief AD-017: ARMED</Text>
        </View>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${node2Load}%`, backgroundColor: TOKENS.deciderEmerald }]} />
        </View>
      </View>
    </View>
  );
}

// ---------------- Screen 2: Thinker Lens ----------------
function ThinkerScreen({ node1Load }: any) {
  return (
    <View style={styles.screenWrapper}>
      <View style={styles.card}>
        <Text style={[styles.cardTitle, { color: TOKENS.thinkerCyan }]}>ACTIVE GENERATIVE MANIFOLDS</Text>
        <Text style={styles.cardBodyText}>
          Parametric CAD and BabelForge Peptide Synthesis Vectors currently undergoing synthesis.
        </Text>
        <View style={styles.itemBox}>
          <Text style={styles.itemTitle}>1. Torus Knot Vacuum Cavity (p=2, q=3)</Text>
          <Text style={styles.itemSub}>Tensile Modulus: 420 GPa &bull; &Delta;S = 340 J</Text>
        </View>
        <View style={styles.itemBox}>
          <Text style={styles.itemTitle}>2. Calabi-Yau 6D Spatial Projection</Text>
          <Text style={styles.itemSub}>K&auml;hler Form Symmetry &bull; Non-perturbative ratcheting</Text>
        </View>
        <View style={styles.itemBox}>
          <Text style={styles.itemTitle}>3. BabelForge Peptide α-Helical Lattice</Text>
          <Text style={styles.itemSub}>Sovereign formulation #89 &bull; Zero external cloud call</Text>
        </View>
      </View>
    </View>
  );
}

// ---------------- Screen 3: Decider Lens ----------------
function DeciderScreen({ node2Load }: any) {
  return (
    <View style={styles.screenWrapper}>
      <View style={styles.card}>
        <Text style={[styles.cardTitle, { color: TOKENS.deciderEmerald }]}>TRIBUNAL QUORUM RATIFICATION</Text>
        <Text style={styles.cardBodyText}>
          Four independent judicial arbiters evaluate all projected hypotheses from skyTech-Worker.
        </Text>
        <View style={styles.arbiterRow}>
          <Text style={styles.arbiterName}>⚖️ The Judge</Text>
          <Text style={styles.arbiterStatus}>PASS (0.994)</Text>
        </View>
        <View style={styles.arbiterRow}>
          <Text style={styles.arbiterName}>🛡️ Grief AD-017 Safeguard</Text>
          <Text style={[styles.arbiterStatus, { color: TOKENS.deciderEmerald }]}>SAFE_ZERO_RISK</Text>
        </View>
        <View style={styles.arbiterRow}>
          <Text style={styles.arbiterName}>💎 Fiduciary Fealty</Text>
          <Text style={styles.arbiterStatus}>1.000 FEALTY</Text>
        </View>
        <View style={styles.arbiterRow}>
          <Text style={styles.arbiterName}>🔥 Landauer Limit (&le;1000J)</Text>
          <Text style={[styles.arbiterStatus, { color: TOKENS.thinkerCyan }]}>PASS_412J</Text>
        </View>
      </View>
    </View>
  );
}

// ---------------- Screen 4: Telemetry ----------------
function TelemetryScreen() {
  return (
    <View style={styles.screenWrapper}>
      <View style={styles.card}>
        <Text style={styles.cardTitle}>48-CORE MESH DISTRIBUTION</Text>
        <Text style={styles.cardBodyText}>Concurrent dual-node resource matrix</Text>
        <View style={styles.coresContainer}>
          {Array.from({ length: 48 }).map((_, i) => (
            <View
              key={i}
              style={[
                styles.coreBlock,
                { backgroundColor: i < 32 ? 'rgba(0, 229, 255, 0.25)' : 'rgba(16, 185, 129, 0.25)' }
              ]}
            >
              <Text style={styles.coreText}>{i + 1}</Text>
            </View>
          ))}
        </View>
        <View style={{ marginTop: 12 }}>
          <Text style={styles.itemSub}>• Cores 1-32: skyTech-Worker (Local Thinker)</Text>
          <Text style={styles.itemSub}>• Cores 33-48: Ryzen7-Head (Remote Decider)</Text>
        </View>
      </View>
    </View>
  );
}

// ---------------- Tab Button Component ----------------
function TabButton({ label, icon, active, onPress }: any) {
  return (
    <TouchableOpacity
      style={[styles.tabItem, active && styles.tabItemActive]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <Text style={styles.tabIcon}>{icon}</Text>
      <Text style={[styles.tabLabel, active && styles.tabLabelActive]}>{label}</Text>
    </TouchableOpacity>
  );
}

// ---------------- Styles ----------------
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: TOKENS.bgBase,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: TOKENS.borderSubtle,
    backgroundColor: TOKENS.bgSurface,
  },
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  orb: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: TOKENS.thinkerCyan,
  },
  brandTitle: {
    color: TOKENS.textPrimary,
    fontSize: 16,
    fontWeight: '800',
  },
  brandSub: {
    color: TOKENS.textMuted,
    fontSize: 10,
    fontFamily: 'monospace',
  },
  cycleBadge: {
    backgroundColor: 'rgba(255, 255, 255, 0.06)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: TOKENS.borderSubtle,
  },
  cycleBadgeText: {
    color: TOKENS.textSecondary,
    fontSize: 10,
    fontWeight: '700',
    fontFamily: 'monospace',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  screenWrapper: {
    gap: 14,
  },
  card: {
    backgroundColor: TOKENS.bgCard,
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: TOKENS.borderSubtle,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  cardTitle: {
    color: TOKENS.textPrimary,
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  cardBodyText: {
    color: TOKENS.textSecondary,
    fontSize: 12,
    marginBottom: 8,
  },
  gaugeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingVertical: 12,
  },
  gaugeCol: {
    alignItems: 'center',
  },
  gaugeBigText: {
    color: TOKENS.thinkerCyan,
    fontSize: 24,
    fontWeight: '800',
    fontFamily: 'monospace',
  },
  gaugeLabel: {
    color: TOKENS.textMuted,
    fontSize: 10,
    marginTop: 2,
  },
  gaugeDivider: {
    width: 1,
    height: 36,
    backgroundColor: TOKENS.borderSubtle,
  },
  stepBtn: {
    backgroundColor: 'rgba(0, 229, 255, 0.15)',
    borderWidth: 1,
    borderColor: TOKENS.thinkerCyan,
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  stepBtnText: {
    color: TOKENS.thinkerCyan,
    fontWeight: '700',
    fontSize: 12,
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  metricLabel: {
    color: TOKENS.textSecondary,
    fontSize: 11,
    fontFamily: 'monospace',
  },
  progressBar: {
    height: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 2,
    marginTop: 6,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
  },
  itemBox: {
    backgroundColor: 'rgba(0,0,0,0.3)',
    padding: 10,
    borderRadius: 8,
    marginTop: 8,
    borderWidth: 1,
    borderColor: TOKENS.borderSubtle,
  },
  itemTitle: {
    color: TOKENS.textPrimary,
    fontSize: 12,
    fontWeight: '600',
  },
  itemSub: {
    color: TOKENS.textMuted,
    fontSize: 10,
    fontFamily: 'monospace',
    marginTop: 2,
  },
  arbiterRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: TOKENS.borderSubtle,
  },
  arbiterName: {
    color: TOKENS.textPrimary,
    fontSize: 12,
  },
  arbiterStatus: {
    color: TOKENS.thinkerCyan,
    fontSize: 11,
    fontFamily: 'monospace',
    fontWeight: '700',
  },
  coresContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 10,
  },
  coreBlock: {
    width: 32,
    height: 32,
    borderRadius: 6,
    justifyContent: 'center',
    alignItems: 'center',
  },
  coreText: {
    color: '#fff',
    fontSize: 10,
    fontFamily: 'monospace',
    fontWeight: '600',
  },
  tabBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 64,
    flexDirection: 'row',
    backgroundColor: 'rgba(10, 15, 24, 0.95)',
    borderTopWidth: 1,
    borderTopColor: TOKENS.borderSubtle,
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingBottom: 6,
  },
  tabItem: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 8,
  },
  tabItemActive: {
    backgroundColor: 'rgba(255, 255, 255, 0.06)',
  },
  tabIcon: {
    fontSize: 18,
  },
  tabLabel: {
    color: TOKENS.textMuted,
    fontSize: 10,
    fontWeight: '600',
    marginTop: 2,
  },
  tabLabelActive: {
    color: TOKENS.thinkerCyan,
  },
});
