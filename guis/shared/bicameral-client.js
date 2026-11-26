/**
 * ClothOS // Loom Fabric — Universal Bicameral Client
 * Antigravity High-Coherence Client connecting to Node 1 (skyTech-Worker, Thinker)
 * and Node 2 (Ryzen7-Head, Decider) daemons.
 */

class BicameralClient {
    constructor(options = {}) {
        const origin = (typeof window !== 'undefined' && window.location && window.location.origin && window.location.origin.startsWith('http'))
            ? window.location.origin
            : 'http://localhost:8087';
        this.node1Url = options.node1Url || origin;
        this.node2Url = options.node2Url || 'http://100.74.98.21:8087';
        this.activePlane = options.activePlane || 'UNIFIED'; // 'UNIFIED' | 'THINKER' | 'DECIDER'
        this.listeners = new Set();
        this.streamEventSource = null;
        this.pollIntervalMs = options.pollIntervalMs || 2000;
        this.pollTimer = null;

        // Live state populated from /api/bicameral/status and /api/telemetry/snapshot
        this.state = {
            dyadStatus: 'CONNECTING',
            resonance: 0.0,
            coherence: 0.0,
            cycleCount: 0,
            lastStepMs: 0.0,
            node1: {
                name: 'skyTech-Worker',
                role: 'PROJECTOR_THINKER',
                endpoint: this.node1Url,
                status: 'CONNECTING',
                coreCount: 16,
                load: 0.0,
                hostCores: [],
                memoryUsedMb: 0,
                memoryTotalMb: 0,
                currentHypothesis: 'Awaiting live telemetry from Master Hub...',
                activeProjects: 0,
                entropyDeltaS: 0.0,
                belforgeFormulas: 0
            },
            node2: {
                name: 'Ryzen7-Head',
                role: 'DECIDER',
                endpoint: this.node2Url,
                status: 'CHECKING',
                coreCount: 16,
                load: 0.0,
                node2Cores: [],
                memoryUsedMb: 0,
                memoryTotalMb: 0,
                ad017Status: 'ARMED_PROTECTIVE',
                fiduciaryFealty: 1.0,
                pendingDeliberations: 0,
                tribunalQuorum: '4/4 UNANIMOUS',
                verdictsDelivered: 0
            },
            proposals: [],
            logs: []
        };

        this.init();
    }

    init() {
        this.fetchStatus();
        this.pollTimer = setInterval(() => this.fetchStatus(), this.pollIntervalMs);
        this.initSSE();
    }

    subscribe(callback) {
        this.listeners.add(callback);
        // Dispatch current state immediately
        callback(this.state);
        return () => this.listeners.delete(callback);
    }

    notify() {
        for (const listener of this.listeners) {
            try {
                listener(this.state);
            } catch (err) {
                console.error('[BicameralClient] Listener error:', err);
            }
        }
    }

    setPlane(plane) {
        if (['UNIFIED', 'THINKER', 'DECIDER'].includes(plane)) {
            this.activePlane = plane;
            this.notify();
        }
    }

    async fetchStatus() {
        const t0 = (typeof performance !== 'undefined') ? performance.now() : Date.now();
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2500);

            const [bicamRes, snapRes] = await Promise.allSettled([
                fetch(`${this.node1Url}/api/bicameral/status`, { signal: controller.signal }),
                fetch(`${this.node1Url}/api/taskmgr/snapshot`, { signal: controller.signal }),
            ]);
            clearTimeout(timeoutId);
            const t1 = (typeof performance !== 'undefined') ? performance.now() : Date.now();
            this.state.lastStepMs = +(t1 - t0).toFixed(2);

            let anyLive = false;
            if (bicamRes.status === 'fulfilled' && bicamRes.value.ok) {
                const data = await bicamRes.value.json();
                anyLive = true;
                this.state.dyadStatus = data.peer_online ? 'SYNCHRONIZED' : 'LOCAL_PRIMARY';
                this.state.cycleCount = data.active_ratchet_index ?? this.state.cycleCount;
                this.state.resonance = data.kuramoto_synchrony ?? 0.0;
                this.state.coherence = data.kuramoto_synchrony ?? 0.0;
                this.state.node1.status = 'ONLINE';
                this.state.node2.verdictsDelivered = data.total_approved_verdicts ?? 0;

                if (Array.isArray(data.recent_dialogue) && data.recent_dialogue.length > 0) {
                    const recent = [...data.recent_dialogue].reverse();
                    this.state.proposals = recent.slice(0, 12).map((item) => {
                        const th = item.thought || {};
                        const vd = item.verdict || {};
                        const approved = vd.decision === 'APPROVED';
                        return {
                            id: th.thought_id || vd.verdict_id || 'THOUGHT',
                            title: th.title || 'Bicameral Deliberation',
                            domain: th.category || 'HYPOTHESIS',
                            status: approved ? 'RATIFIED' : (vd.decision || 'PENDING'),
                            projectorHypothesis: (th.details && th.details.hypothesis) || (th.details && th.details.description) || vd.rationale || '',
                            verdict: vd.decision || 'DELIBERATING',
                            votes: {
                                the_judge: approved ? 'PASS' : 'VETO',
                                grief_ad017: vd.grief_boundary_status || 'PASS',
                                fiduciary: `FEALTY_${vd.fiduciary_score ?? 1.0}`,
                                landauer: `${vd.landauer_dissipation_joules ?? 0}J`
                            },
                            timestamp: vd.timestamp ? new Date(vd.timestamp * 1000).toLocaleTimeString() : ''
                        };
                    });
                    if (this.state.logs.length === 0) {
                        this.state.logs = recent.slice(0, 20).map((item, idx) => {
                            const th = item.thought || {};
                            const vd = item.verdict || {};
                            return {
                                id: idx + 1,
                                time: vd.timestamp ? new Date(vd.timestamp * 1000).toLocaleTimeString() : '',
                                sender: vd.decider_node || th.origin_node || 'Dyad',
                                tag: vd.decision === 'APPROVED' ? 'DECIDER' : 'THINKER',
                                text: `${th.title || th.thought_id} -> ${vd.decision} (Ratchet #${vd.ratchet_index ?? '?'})`
                            };
                        });
                    }
                }
            }

            if (snapRes.status === 'fulfilled' && snapRes.value.ok) {
                const snap = await snapRes.value.json();
                anyLive = true;
                const cpu = snap.cpu || {};
                const mem = snap.memory || {};
                this.state.node1.status = 'ONLINE';
                this.state.node1.load = +(cpu.overall_percent || 0).toFixed(1);
                this.state.node1.hostCores = Array.isArray(cpu.host_cores) ? cpu.host_cores : [];
                this.state.node1.coreCount = this.state.node1.hostCores.length || 16;
                this.state.node1.memoryUsedMb = Math.round((mem.host_used_gb || 0) * 1024);
                this.state.node1.memoryTotalMb = Math.round((mem.host_total_gb || 0) * 1024);
                this.state.node1.currentHypothesis = snap.cadence_label
                    ? `Active Host Sampling @ ${snap.cadence_label} (${cpu.processes_count || 0} OS procs)`
                    : this.state.node1.currentHypothesis;

                this.state.node2.status = snap.node2_live ? 'ONLINE' : 'OFFLINE';
                this.state.node2.load = snap.node2_live ? +(cpu.node2_cpu_pct || 0).toFixed(1) : 0.0;
                this.state.node2.node2Cores = Array.isArray(cpu.node2_cores) ? cpu.node2_cores : [];
                this.state.node2.memoryUsedMb = snap.node2_live ? Math.round((mem.node2_used_gb || 0) * 1024) : 0;
                this.state.node2.memoryTotalMb = snap.node2_live ? Math.round((mem.node2_total_gb || 0) * 1024) : 0;
            }

            if (!anyLive) {
                this.markOffline();
            }
        } catch (e) {
            this.markOffline();
        }
        this.notify();
    }

    markOffline() {
        this.state.dyadStatus = 'OFFLINE';
        this.state.node1.status = 'OFFLINE';
        this.state.node2.status = 'OFFLINE';
        this.state.node1.load = 0.0;
        this.state.node2.load = 0.0;
    }

    initSSE() {
        if (typeof window === 'undefined' || !window.EventSource) return;
        try {
            this.streamEventSource = new EventSource(`${this.node1Url}/api/telemetry/sse?interval=1.0`);
            this.streamEventSource.onmessage = (event) => {
                try {
                    const snap = JSON.parse(event.data);
                    if (snap && snap.cpu) {
                        this.state.node1.status = 'ONLINE';
                        this.state.node1.load = +(snap.cpu.overall_percent || 0).toFixed(1);
                        this.state.node1.hostCores = Array.isArray(snap.cpu.host_cores) ? snap.cpu.host_cores : this.state.node1.hostCores;
                        this.state.node2.status = snap.node2_live ? 'ONLINE' : 'OFFLINE';
                        this.state.node2.load = snap.node2_live ? +(snap.cpu.node2_cpu_pct || 0).toFixed(1) : 0.0;
                        this.state.node2.node2Cores = Array.isArray(snap.cpu.node2_cores) ? snap.cpu.node2_cores : this.state.node2.node2Cores;
                        this.notify();
                    }
                } catch (e) {
                    console.warn('[BicameralClient] SSE parse error:', e);
                }
            };
            this.streamEventSource.onerror = () => {
                this.streamEventSource.close();
            };
        } catch (e) {}
    }

    async projectHypothesis(title, domain, hypothesis) {
        const id = 'PROP-' + String(Date.now()).slice(-6);
        const proposal = {
            id,
            title,
            domain: domain || 'cad_geometry',
            hypothesis,
            status: 'PENDING_VERDICT',
            projectorHypothesis: hypothesis,
            verdict: 'SUBMITTED',
            votes: {
                the_judge: 'EVALUATING',
                grief_ad017: 'CHECKING',
                fiduciary: 'EVALUATING',
                landauer: 'MEASURING'
            },
            timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19)
        };

        this.state.proposals.unshift(proposal);
        this.state.logs.unshift({
            id: Date.now(),
            time: new Date().toLocaleTimeString(),
            sender: 'skyTech-Worker',
            tag: 'THINKER',
            text: `Dispatched hypothesis "${title}" (${id}) to Decider tribunal.`
        });
        this.notify();

        try {
            const cat = domain && domain.toUpperCase().includes('CAD') ? 'CAD_SOLID' : 'HYPOTHESIS';
            const res = await fetch(`${this.node1Url}/api/bicameral/step`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    category: cat,
                    title,
                    details: { domain, hypothesis }
                })
            });
            if (res.ok) {
                const data = await res.json();
                const vd = data.verdict || {};
                const th = data.thought || {};
                proposal.id = th.thought_id || proposal.id;
                proposal.status = vd.decision === 'APPROVED' ? 'RATIFIED' : (vd.decision || 'RATIFIED');
                proposal.verdict = vd.decision === 'APPROVED' ? 'APPROVED_UNANIMOUS' : (vd.decision || 'LOGGED');
                proposal.votes = {
                    the_judge: vd.decision === 'APPROVED' ? 'PASS' : 'VETO',
                    grief_ad017: vd.grief_boundary_status || 'INVIOLABLE_PASS',
                    fiduciary: `FEALTY_${vd.fiduciary_score ?? 1.0}`,
                    landauer: `${vd.landauer_dissipation_joules ?? 120}J`
                };
                this.state.logs.unshift({
                    id: Date.now() + 1,
                    time: new Date().toLocaleTimeString(),
                    sender: vd.decider_node || 'Ryzen7-Head',
                    tag: 'DECIDER',
                    text: `Proposal ${proposal.id} evaluated -> ${proposal.verdict} (Ratchet #${data.ratchet_index || '?'})`
                });
                await this.fetchStatus();
                return proposal;
            } else {
                proposal.status = 'ERROR';
                proposal.verdict = `HTTP_${res.status}`;
            }
        } catch (e) {
            proposal.status = 'OFFLINE';
            proposal.verdict = 'NODE_UNREACHABLE';
        }
        this.notify();
        return proposal;
    }

    async stepDyad() {
        const t0 = (typeof performance !== 'undefined') ? performance.now() : Date.now();
        try {
            const res = await fetch(`${this.node1Url}/api/bicameral/step`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category: 'HYPOTHESIS' })
            });
            const t1 = (typeof performance !== 'undefined') ? performance.now() : Date.now();
            this.state.lastStepMs = +(t1 - t0).toFixed(2);
            if (res.ok) {
                const data = await res.json();
                this.state.cycleCount++;
                this.state.logs.unshift({
                    id: Date.now(),
                    time: new Date().toLocaleTimeString(),
                    sender: 'Dyad Core',
                    tag: 'HARMONY',
                    text: `Live bicameral step executed in ${this.state.lastStepMs}ms (Ratchet #${data.ratchet_index || this.state.cycleCount}).`
                });
                await this.fetchStatus();
                return;
            }
        } catch (e) {}
        this.state.logs.unshift({
            id: Date.now(),
            time: new Date().toLocaleTimeString(),
            sender: 'Dyad Core',
            tag: 'OFFLINE',
            text: `Bicameral step aborted: Master Hub unreachable at ${this.node1Url}.`
        });
        this.notify();
    }
}

// Universal export
if (typeof window !== 'undefined') {
    window.BicameralClient = BicameralClient;
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BicameralClient;
}
