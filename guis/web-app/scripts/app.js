/**
 * ClothOS // Antigravity Command Center SPA Controller
 * Integrates BicameralClient, 3D CAD Engine, Live Telemetry Canvas,
 * Tribunal Deliberation Board, and Web Audio Synesthesia.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Clients and Engines
    const client = new BicameralClient();
    const cadEngine = new CadEngine('cadCanvas');
    
    // Audio Context for Micro-Harmonics
    let audioCtx = null;
    let audioMuted = false;

    function playTone(freq, type = 'sine', duration = 0.12) {
        if (audioMuted) return;
        try {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        } catch (e) {}
    }

    // 2. DOM Elements Selection
    const planeButtons = document.querySelectorAll('.plane-btn');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = {
        cad: document.getElementById('viewCad'),
        tribunal: document.getElementById('viewTribunal'),
        telemetry: document.getElementById('viewTelemetry')
    };

    const coherenceValEl = document.getElementById('valCoherence');
    const resonanceValEl = document.getElementById('valResonance');
    const cycleCountEl = document.getElementById('valCycle');
    const latencyValEl = document.getElementById('valLatency');

    // Node 1 & 2 Elements
    const node1LoadEl = document.getElementById('node1Load');
    const node1BarEl = document.getElementById('node1Bar');
    const node1HypoEl = document.getElementById('node1Hypothesis');
    const node2LoadEl = document.getElementById('node2Load');
    const node2BarEl = document.getElementById('node2Bar');
    const node2VerdictsEl = document.getElementById('node2Verdicts');
    const node2Ad017El = document.getElementById('node2Ad017');

    // Stream and Form
    const streamListEl = document.getElementById('streamList');
    const formEl = document.getElementById('hypothesisForm');
    const cadStatsBadge = document.getElementById('cadStatsBadge');

    // 3. Bind Plane Switcher
    planeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            planeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const plane = btn.dataset.plane;
            client.setPlane(plane);
            playTone(plane === 'THINKER' ? 520 : plane === 'DECIDER' ? 390 : 440, 'triangle', 0.15);
            applyPlaneView(plane);
        });
    });

    function applyPlaneView(plane) {
        const leftNodeThinker = document.getElementById('cardNodeThinker');
        const leftNodeDecider = document.getElementById('cardNodeDecider');

        if (plane === 'THINKER') {
            leftNodeThinker.style.opacity = '1';
            leftNodeThinker.style.transform = 'scale(1.02)';
            leftNodeDecider.style.opacity = '0.45';
            leftNodeDecider.style.transform = 'scale(0.98)';
            switchTab('cad');
        } else if (plane === 'DECIDER') {
            leftNodeThinker.style.opacity = '0.45';
            leftNodeThinker.style.transform = 'scale(0.98)';
            leftNodeDecider.style.opacity = '1';
            leftNodeDecider.style.transform = 'scale(1.02)';
            switchTab('tribunal');
        } else {
            leftNodeThinker.style.opacity = '1';
            leftNodeThinker.style.transform = 'scale(1)';
            leftNodeDecider.style.opacity = '1';
            leftNodeDecider.style.transform = 'scale(1)';
        }
    }

    // 4. Bind Center Stage Tabs
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;
            switchTab(targetTab);
            playTone(480, 'sine', 0.08);
        });
    });

    function switchTab(targetTab) {
        tabButtons.forEach(b => b.classList.toggle('active', b.dataset.tab === targetTab));
        Object.entries(tabContents).forEach(([name, el]) => {
            if (el) el.style.display = (name === targetTab) ? 'block' : 'none';
        });
        if (targetTab === 'cad') cadEngine.resize();
        if (targetTab === 'telemetry') drawTelemetryCores();
    }

    // 5. Bind CAD Controls
    document.querySelectorAll('.cad-shape-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.cad-shape-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            cadEngine.setShape(btn.dataset.shape);
            playTone(600, 'sine', 0.1);
        });
    });

    document.querySelectorAll('.cad-mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.cad-mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            cadEngine.setRenderMode(btn.dataset.mode);
            playTone(640, 'sine', 0.1);
        });
    });

    const autoRotBtn = document.getElementById('btnToggleAutoRotate');
    if (autoRotBtn) {
        autoRotBtn.addEventListener('click', () => {
            const running = cadEngine.toggleAutoRotate();
            autoRotBtn.classList.toggle('active', running);
            playTone(400, 'triangle', 0.08);
        });
    }

    // 6. Action Buttons
    const btnStepDyad = document.getElementById('btnStepDyad');
    if (btnStepDyad) {
        btnStepDyad.addEventListener('click', () => {
            client.stepDyad();
            playTone(880, 'sine', 0.2);
        });
    }

    const btnAudioToggle = document.getElementById('btnAudioToggle');
    if (btnAudioToggle) {
        btnAudioToggle.addEventListener('click', () => {
            audioMuted = !audioMuted;
            btnAudioToggle.textContent = audioMuted ? '🔇 MUTED' : '🔊 HARMONICS';
            if (!audioMuted) playTone(440, 'sine', 0.1);
        });
    }

    // 7. Hypothesis Submission
    if (formEl) {
        formEl.addEventListener('submit', async (e) => {
            e.preventDefault();
            const titleInput = document.getElementById('hypoTitle');
            const domainSelect = document.getElementById('hypoDomain');
            const descInput = document.getElementById('hypoDesc');

            if (!titleInput.value.trim()) return;

            const title = titleInput.value.trim();
            const domain = domainSelect.value;
            const desc = descInput.value.trim() || 'Coherence optimization vector';

            playTone(720, 'square', 0.15);
            await client.projectHypothesis(title, domain, desc);

            titleInput.value = '';
            descInput.value = '';
        });
    }

    // 8. Telemetry 32-Core Matrix Canvas
    const telemetryCanvas = document.getElementById('telemetryCanvas');
    function drawTelemetryCores() {
        if (!telemetryCanvas) return;
        const ctx = telemetryCanvas.getContext('2d');
        const w = telemetryCanvas.width = telemetryCanvas.parentElement.clientWidth || 700;
        const h = telemetryCanvas.height = 360;

        ctx.clearRect(0, 0, w, h);

        // Draw 32 Cores Grid (skyTech-Worker)
        ctx.fillStyle = '#94a3b8';
        ctx.font = '11px JetBrains Mono';
        ctx.fillText('skyTech-Worker (Local Thinker) — 32 Virtual Threads', 16, 24);

        const cols = 8;
        const rows = 4;
        const cellW = (w - 32 - (cols - 1) * 8) / cols;
        const cellH = 34;

        for (let i = 0; i < 32; i++) {
            const c = i % cols;
            const r = Math.floor(i / cols);
            const x = 16 + c * (cellW + 8);
            const y = 36 + r * (cellH + 8);

            const load = Math.min(99, Math.max(12, Math.floor(25 + Math.sin(Date.now() * 0.002 + i) * 20 + Math.random() * 10)));
            ctx.fillStyle = 'rgba(0, 229, 255, 0.08)';
            ctx.fillRect(x, y, cellW, cellH);
            ctx.strokeStyle = 'rgba(0, 229, 255, 0.25)';
            ctx.strokeRect(x, y, cellW, cellH);

            // Fill meter
            const fillH = (load / 100) * cellH;
            ctx.fillStyle = 'rgba(0, 229, 255, 0.4)';
            ctx.fillRect(x, y + cellH - fillH, cellW, fillH);

            ctx.fillStyle = '#ffffff';
            ctx.fillText(`T${i + 1}: ${load}%`, x + 6, y + 20);
        }

        // Draw 16 Cores (Ryzen7-Head)
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('Ryzen7-Head (100.74.98.21 Decider) — 16 Hardware Threads', 16, 210);

        for (let i = 0; i < 16; i++) {
            const c = i % cols;
            const r = Math.floor(i / cols);
            const x = 16 + c * (cellW + 8);
            const y = 222 + r * (cellH + 8);

            const load = Math.min(99, Math.max(15, Math.floor(32 + Math.cos(Date.now() * 0.002 + i) * 18 + Math.random() * 8)));
            ctx.fillStyle = 'rgba(16, 185, 129, 0.08)';
            ctx.fillRect(x, y, cellW, cellH);
            ctx.strokeStyle = 'rgba(16, 185, 129, 0.25)';
            ctx.strokeRect(x, y, cellW, cellH);

            const fillH = (load / 100) * cellH;
            ctx.fillStyle = 'rgba(16, 185, 129, 0.4)';
            ctx.fillRect(x, y + cellH - fillH, cellW, fillH);

            ctx.fillStyle = '#ffffff';
            ctx.fillText(`C${i + 1}: ${load}%`, x + 6, y + 20);
        }
    }

    setInterval(() => {
        if (tabContents.telemetry && tabContents.telemetry.style.display !== 'none') {
            drawTelemetryCores();
        }
    }, 1200);

    // 9. Subscribe to Bicameral Client State
    client.subscribe((state) => {
        // Top metrics
        if (coherenceValEl) coherenceValEl.textContent = state.coherence.toFixed(3);
        if (resonanceValEl) resonanceValEl.textContent = (state.resonance * 100).toFixed(1) + '%';
        if (cycleCountEl) cycleCountEl.textContent = state.cycleCount;
        if (latencyValEl) latencyValEl.textContent = `${state.lastStepMs} ms`;

        // Left node metrics
        if (node1LoadEl) node1LoadEl.textContent = `${state.node1.load}%`;
        if (node1BarEl) node1BarEl.style.width = `${state.node1.load}%`;
        if (node1HypoEl) node1HypoEl.textContent = state.node1.currentHypothesis;

        if (node2LoadEl) node2LoadEl.textContent = `${state.node2.load}%`;
        if (node2BarEl) node2BarEl.style.width = `${state.node2.load}%`;
        if (node2VerdictsEl) node2VerdictsEl.textContent = `${state.node2.verdictsDelivered} Ratified`;
        if (node2Ad017El) node2Ad017El.textContent = state.node2.ad017Status;

        // CAD Stats
        if (cadStatsBadge) {
            const stats = cadEngine.getStats();
            cadStatsBadge.textContent = `${stats.vertices} verts | ${stats.faces} faces | ${stats.fps} FPS | ${stats.frameTime}ms`;
        }

        // Render Deliberations
        renderTribunalTable(state.proposals);

        // Render Stream Logs
        renderStream(state.logs);
    });

    function renderTribunalTable(proposals) {
        const tbody = document.getElementById('tribunalTableBody');
        if (!tbody) return;
        tbody.innerHTML = proposals.map(p => `
            <tr>
                <td style="font-family: var(--font-mono); font-weight: 700; color: var(--color-thinker-cyan);">${p.id}</td>
                <td style="font-weight: 600;">${p.title}</td>
                <td><span style="font-family: var(--font-mono); font-size: 10px; color: var(--color-text-secondary);">${p.domain}</span></td>
                <td>
                    <span class="${p.status === 'RATIFIED' ? 'badge-ratified' : 'badge-pending'}">
                        ${p.verdict}
                    </span>
                </td>
                <td style="font-family: var(--font-mono); font-size: 10px;">
                    J:${p.votes.the_judge} | AD17:${p.votes.grief_ad017} | L:${p.votes.landauer}
                </td>
                <td style="color: var(--color-text-muted); font-size: 10px;">${p.timestamp}</td>
            </tr>
        `).join('');
    }

    function renderStream(logs) {
        if (!streamListEl) return;
        streamListEl.innerHTML = logs.map(item => `
            <div class="stream-item ${item.tag.toLowerCase()}">
                <div class="stream-meta">
                    <span>${item.sender} [${item.tag}]</span>
                    <span>${item.time}</span>
                </div>
                <div>${item.text}</div>
            </div>
        `).join('');
    }
});
