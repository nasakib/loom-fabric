import React, { useEffect, useState } from 'react';
import {
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
 * LOOM FABRIC COMMANDER — Universal React Native Application
 * Runs natively on:
 *   - iOS & Android (Expo / React Native Mobile)
 *   - Windows & macOS (React Native Desktop)
 *   - Web / PWA (React Native Web)
 *   - Remote Controller for ClothOS RISC-V (RV64GC + RVV 1.0) Nodes
 *
 * Workflow (agy-style):
 *   1. Open App -> 2. Press [▶ START FABRIC] -> 3. Type Prompt & Hit Send
 */

type PlatformProfile = {
  id: string;
  label: string;
  arch: string;
  enclaveMode: string;
};

const PLATFORM_PROFILES: PlatformProfile[] = [
  {
    id: 'windows-x64',
    label: 'Windows 11 (skyTech + Ryzen 7)',
    arch: 'x86_64 // CUDA 12 + Vulkan 1.3',
    enclaveMode: 'Win32 Job Object + Torque Vault',
  },
  {
    id: 'clothos-riscv64',
    label: 'ClothOS Special Edition (RISC-V)',
    arch: 'riscv64gc // RVV 1.0 (512-bit Vector)',
    enclaveMode: 'Hardware PMP CSR (pmpcfg0=0x9B NAPOT)',
  },
  {
    id: 'macos-arm64',
    label: 'macOS Apple Silicon',
    arch: 'arm64 // Metal Unified Memory',
    enclaveMode: 'Darwin Sandbox + Torque Vault',
  },
  {
    id: 'linux-x64',
    label: 'Linux / WSL2 Sovereign Node',
    arch: 'x86_64 / aarch64 // CUDA + ROCm',
    enclaveMode: 'cgroups v2 + Torque Vault',
  },
  {
    id: 'react-native-mobile',
    label: 'React Native Universal (iOS / Android)',
    arch: `${Platform.OS} // Remote Mesh Client`,
    enclaveMode: 'Zero-Trust TLS / LAN Wire Bridge',
  },
];

const MODELS = ['auto', 'qwen2.5:32b', 'deepseek-r1:14b', 'qwen2.5:7b', 'qwen2.5:3b'];

export default function App() {
  const [gatewayHost, setGatewayHost] = useState<string>('http://192.168.99.1:8002');
  const [selectedPlatform, setSelectedPlatform] = useState<PlatformProfile>(PLATFORM_PROFILES[1]); // Default highlight ClothOS RISC-V & Windows
  const [selectedModel, setSelectedModel] = useState<string>('auto');
  const [prompt, setPrompt] = useState<string>('');
  const [output, setOutput] = useState<string>(
    '⚡ LOOM FABRIC COMMANDER (React Native Universal + ClothOS RISC-V Edition)\n' +
      '• Press [▶ START FABRIC] above or type your prompt below and press Send.\n' +
      '• Zero external terminal windows — background watchdog self-heals all ports.'
  );
  const [statusMsg, setStatusMsg] = useState<string>('🛡 Auto-Heal Active • Zero Terminals');
  const [routeBadge, setRouteBadge] = useState<string>('Standby');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [clusterPorts, setClusterPorts] = useState<Record<string, Record<string, boolean>>>({});

  const refreshClusterStatus = async () => {
    try {
      const res = await fetch(`${gatewayHost}/api/cluster/status`);
      if (res.ok) {
        const data = await res.json();
        setClusterPorts(data);
      }
    } catch (_) {
      // Fallback to localhost if running on same machine
      if (gatewayHost.includes('192.168.99.1')) {
        try {
          const res2 = await fetch('http://127.0.0.1:8002/api/cluster/status');
          if (res2.ok) {
            setGatewayHost('http://127.0.0.1:8002');
            setClusterPorts(await res2.json());
          }
        } catch (_) {}
      }
    }
  };

  useEffect(() => {
    refreshClusterStatus();
    const timer = setInterval(refreshClusterStatus, 5000);
    return () => clearInterval(timer);
  }, [gatewayHost]);

  const triggerClusterAction = async (action: 'start' | 'restart_both' | 'stop') => {
    setStatusMsg(`⚡ Dispatching '${action}' silently in background...`);
    try {
      const res = await fetch(`${gatewayHost}/api/cluster/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      });
      const data = await res.json();
      setStatusMsg(`✔ ${data.message || 'Cluster action completed'}`);
      setTimeout(refreshClusterStatus, 1000);
    } catch (err: any) {
      setStatusMsg(`⚠ Gateway unreachable (${err.message})`);
    }
  };

  const sendPrompt = async () => {
    const trimmed = prompt.trim();
    if (!trimmed || isLoading) return;
    setIsLoading(true);
    setPrompt('');
    setRouteBadge('Triaging Compute...');
    setOutput((prev) => `${prev}\n\nUser (${selectedPlatform.id}) ❯ ${trimmed}\nLoom (${selectedModel}) ❯ `);

    try {
      const res = await fetch(`${gatewayHost}/v1/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: selectedModel,
          messages: [{ role: 'user', content: trimmed }],
          stream: false,
        }),
      });
      const route = res.headers.get('X-Torque-Route') || 'Tier 1 Local';
      const chosen = res.headers.get('X-Torque-Model-Selected') || selectedModel;
      const scrubbed = res.headers.get('X-Torque-Scrubbed') || 'false';
      setRouteBadge(`${route} | ${chosen} | Scrubbed: ${scrubbed}`);

      const data = await res.json();
      const reply = data?.choices?.[0]?.message?.content || JSON.stringify(data);
      setOutput((prev) => `${prev}${reply}`);
    } catch (err: any) {
      setOutput((prev) => `${prev}\n[Error: ${err.message}]`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* 1. Top Masthead & Zero-Terminal Start Bar */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>LOOM FABRIC COMMANDER</Text>
          <Text style={styles.subtitle}>
            Universal React Native App • Windows • macOS • Linux • iOS/Android • ClothOS RISC-V
          </Text>
        </View>
        <View style={styles.controlRow}>
          <TouchableOpacity
            style={[styles.btn, styles.btnStart]}
            onPress={() => triggerClusterAction('start')}
          >
            <Text style={styles.btnStartText}>▶ START FABRIC</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.btn, styles.btnPurple]}
            onPress={() => triggerClusterAction('restart_both')}
          >
            <Text style={styles.btnText}>⚡ Restart BOTH Nodes</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.btn, styles.btnStop]}
            onPress={() => triggerClusterAction('stop')}
          >
            <Text style={styles.btnText}>■ Stop Local</Text>
          </TouchableOpacity>
        </View>
        <Text style={styles.statusText}>{statusMsg}</Text>
      </View>

      <ScrollView style={styles.scrollArea} contentContainerStyle={{ paddingBottom: 32 }}>
        {/* 2. Platform & ClothOS RISC-V Architecture Selector */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>
            PLATFORM &amp; ARCHITECTURE EDITION (INCLUDING CLOTHOS RISC-V RV64GC)
          </Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.pillRow}>
            {PLATFORM_PROFILES.map((p) => {
              const active = p.id === selectedPlatform.id;
              return (
                <TouchableOpacity
                  key={p.id}
                  style={[styles.platformPill, active && styles.platformPillActive]}
                  onPress={() => setSelectedPlatform(p)}
                >
                  <Text style={[styles.platformPillText, active && styles.platformPillTextActive]}>
                    {p.label}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>
          <View style={styles.archMetaBox}>
            <Text style={styles.archMetaText}>ISA / Silicon : {selectedPlatform.arch}</Text>
            <Text style={styles.archMetaText}>Enclave Ring  : {selectedPlatform.enclaveMode}</Text>
          </View>
        </View>

        {/* 3. Immediate Prompt & Inference Console (agy-style) */}
        <View style={[styles.card, styles.shuttleCard]}>
          <View style={styles.rowBetween}>
            <Text style={styles.cardTitle}>THE SHUTTLE // PROMPT &amp; INFERENCE CONSOLE</Text>
            <Text style={styles.routeBadge}>{routeBadge}</Text>
          </View>

          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.pillRow}>
            {MODELS.map((m) => (
              <TouchableOpacity
                key={m}
                style={[styles.modelPill, selectedModel === m && styles.modelPillActive]}
                onPress={() => setSelectedModel(m)}
              >
                <Text style={styles.modelPillText}>{m}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          <View style={styles.promptRow}>
            <TextInput
              style={styles.promptInput}
              value={prompt}
              onChangeText={setPrompt}
              placeholder="Type your prompt here (just like agy) and press Send..."
              placeholderTextColor="#6ee7b788"
              onSubmitEditing={sendPrompt}
              autoFocus
            />
            <TouchableOpacity style={styles.sendBtn} onPress={sendPrompt}>
              <Text style={styles.sendBtnText}>{isLoading ? '...' : 'Send ❯'}</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.consoleBox}>
            <Text style={styles.consoleText}>{output}</Text>
          </ScrollView>
        </View>

        {/* 4. Dual-Node Live Port Matrix */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>THE WEAVE // LIVE DUAL-NODE PORT MATRIX</Text>
          {(['192.168.99.1', '192.168.99.2'] as const).map((ip) => (
            <View key={ip} style={styles.nodeRow}>
              <Text style={styles.nodeLabel}>
                {ip === '192.168.99.1' ? 'skyTech Worker (192.168.99.1)' : 'Ryzen 7 Head (192.168.99.2)'}
              </Text>
              <View style={styles.portWrap}>
                {Object.entries(clusterPorts[ip] || { '8002': true, '5555': true, '11434': true }).map(
                  ([port, isUp]) => (
                    <Text
                      key={port}
                      style={[styles.portBadge, { color: isUp ? '#10b981' : '#ef4444' }]}
                    >
                      ● :{port}
                    </Text>
                  )
                )}
              </View>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#07120a' },
  header: {
    backgroundColor: '#0d1e12',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1d3d28',
  },
  title: { color: '#34d399', fontSize: 20, fontWeight: '800', letterSpacing: 0.8 },
  subtitle: { color: '#c084fc', fontSize: 12, marginTop: 2 },
  controlRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 12 },
  btn: { paddingVertical: 8, paddingHorizontal: 14, borderRadius: 8 },
  btnStart: { backgroundColor: '#10b981' },
  btnStartText: { color: '#07120a', fontWeight: '800', fontSize: 13 },
  btnPurple: { backgroundColor: '#a855f7' },
  btnStop: { backgroundColor: '#991b1b' },
  btnText: { color: '#f0fdf4', fontWeight: '700', fontSize: 13 },
  statusText: { color: '#6ee7b7', fontSize: 12, marginTop: 8, fontFamily: 'monospace' },
  scrollArea: { flex: 1, padding: 14 },
  card: {
    backgroundColor: '#122818',
    borderColor: '#1d3d28',
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    marginBottom: 14,
  },
  shuttleCard: { borderColor: '#a855f7' },
  cardTitle: { color: '#c084fc', fontSize: 13, fontWeight: '700', marginBottom: 8 },
  rowBetween: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  routeBadge: { color: '#34d399', fontSize: 11, fontFamily: 'monospace' },
  pillRow: { flexDirection: 'row', marginBottom: 10 },
  platformPill: {
    backgroundColor: '#07120a',
    borderColor: '#1d3d28',
    borderWidth: 1,
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 999,
    marginRight: 8,
  },
  platformPillActive: { backgroundColor: '#7e22ce', borderColor: '#c084fc' },
  platformPillText: { color: '#bbf7d0', fontSize: 12, fontWeight: '600' },
  platformPillTextActive: { color: '#ffffff' },
  archMetaBox: {
    backgroundColor: '#07120a',
    padding: 10,
    borderRadius: 8,
    borderColor: '#1d3d28',
    borderWidth: 1,
  },
  archMetaText: { color: '#6ee7b7', fontSize: 12, fontFamily: 'monospace', marginBottom: 2 },
  modelPill: {
    backgroundColor: '#07120a',
    borderColor: '#1d3d28',
    borderWidth: 1,
    paddingVertical: 5,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginRight: 8,
  },
  modelPillActive: { backgroundColor: '#a855f7', borderColor: '#e9d5ff' },
  modelPillText: { color: '#f0fdf4', fontSize: 12, fontWeight: '700' },
  promptRow: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  promptInput: {
    flex: 1,
    backgroundColor: '#07120a',
    color: '#f0fdf4',
    borderColor: '#a855f7',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
  },
  sendBtn: {
    backgroundColor: '#a855f7',
    justifyContent: 'center',
    paddingHorizontal: 18,
    borderRadius: 8,
  },
  sendBtnText: { color: '#ffffff', fontWeight: '800', fontSize: 14 },
  consoleBox: {
    backgroundColor: '#07120a',
    borderRadius: 8,
    padding: 12,
    minHeight: 160,
    maxHeight: 280,
    borderColor: '#1d3d28',
    borderWidth: 1,
  },
  consoleText: { color: '#f0fdf4', fontFamily: 'monospace', fontSize: 13, lineHeight: 19 },
  nodeRow: {
    paddingVertical: 8,
    borderBottomColor: '#1d3d28',
    borderBottomWidth: 1,
  },
  nodeLabel: { color: '#f0fdf4', fontWeight: '700', fontSize: 13, marginBottom: 4 },
  portWrap: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  portBadge: { fontFamily: 'monospace', fontSize: 12, fontWeight: '700' },
});
