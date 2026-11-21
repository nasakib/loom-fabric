/**
 * ClothOS // Antigravity 3D STEM CAD Engine
 * Pure vanilla 60fps Software Rasterizer & Parametric Manifold Generator.
 * Zero external libraries. Hardware-accelerated canvas 2D projection.
 */

class CadEngine {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        
        // Geometry state
        this.vertices = [];
        this.faces = [];
        this.currentShape = 'torus_knot';
        this.renderMode = 'solid'; // 'solid' | 'wireframe' | 'quantum'
        
        // Camera / Transform state
        this.rotX = 0.6;
        this.rotY = 0.8;
        this.rotZ = 0.0;
        this.zoom = 140;
        this.autoRotate = true;
        this.isDragging = false;
        this.lastMouseX = 0;
        this.lastMouseY = 0;
        
        // Animation loop
        this.lastFrameTime = performance.now();
        this.fps = 60;
        this.frameTimeMs = 1.2;

        this.initEvents();
        this.generateGeometry(this.currentShape);
        this.startLoop();
    }

    initEvents() {
        window.addEventListener('resize', () => this.resize());
        this.resize();

        this.canvas.addEventListener('mousedown', (e) => {
            this.isDragging = true;
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
            this.autoRotate = false;
        });

        window.addEventListener('mouseup', () => {
            this.isDragging = false;
        });

        window.addEventListener('mousemove', (e) => {
            if (!this.isDragging) return;
            const dx = e.clientX - this.lastMouseX;
            const dy = e.clientY - this.lastMouseY;
            this.rotY += dx * 0.01;
            this.rotX += dy * 0.01;
            this.lastMouseX = e.clientX;
            this.lastMouseY = e.clientY;
        });

        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            this.zoom = Math.max(50, Math.min(350, this.zoom - e.deltaY * 0.1));
        }, { passive: false });
    }

    resize() {
        const rect = this.canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = (rect.width || 600) * dpr;
        this.canvas.height = (rect.height || 460) * dpr;
        this.ctx.scale(dpr, dpr);
        this.displayWidth = rect.width || 600;
        this.displayHeight = rect.height || 460;
    }

    setShape(shape) {
        this.currentShape = shape;
        this.generateGeometry(shape);
    }

    setRenderMode(mode) {
        this.renderMode = mode;
    }

    toggleAutoRotate() {
        this.autoRotate = !this.autoRotate;
        return this.autoRotate;
    }

    generateGeometry(shape) {
        this.vertices = [];
        this.faces = [];

        if (shape === 'torus_knot') {
            this.generateTorusKnot(2, 3, 120, 24, 1.2, 0.4);
        } else if (shape === 'calabi_yau') {
            this.generateCalabiYauCrossSection(5, 36, 36);
        } else if (shape === 'dyson_lattice') {
            this.generateOctahedralLattice(4);
        } else {
            // Gyroid Minimal Surface proxy
            this.generateGyroidSurface(24, 24);
        }
    }

    generateTorusKnot(p, q, uSteps, vSteps, R, r) {
        const grid = [];
        for (let i = 0; i < uSteps; i++) {
            grid[i] = [];
            const phi = (i / uSteps) * Math.PI * 2;
            const rKnot = R + 0.6 * Math.cos(q * phi);
            const cx = rKnot * Math.cos(p * phi);
            const cy = rKnot * Math.sin(p * phi);
            const cz = 0.7 * Math.sin(q * phi);

            // Compute curve tangent
            const delta = 0.001;
            const phi2 = phi + delta;
            const rKnot2 = R + 0.6 * Math.cos(q * phi2);
            const tx = (rKnot2 * Math.cos(p * phi2) - cx) / delta;
            const ty = (rKnot2 * Math.sin(p * phi2) - cy) / delta;
            const tz = (0.7 * Math.sin(q * phi2) - cz) / delta;
            const tLen = Math.sqrt(tx*tx + ty*ty + tz*tz) || 1;
            const T = [tx/tLen, ty/tLen, tz/tLen];

            // Normal and binormal
            const N = [-T[1], T[0], 0];
            const nLen = Math.sqrt(N[0]*N[0] + N[1]*N[1]) || 1;
            N[0] /= nLen; N[1] /= nLen;
            const B = [T[1]*N[2] - T[2]*N[1], T[2]*N[0] - T[0]*N[2], T[0]*N[1] - T[1]*N[0]];

            for (let j = 0; j < vSteps; j++) {
                const theta = (j / vSteps) * Math.PI * 2;
                const cosT = Math.cos(theta) * r;
                const sinT = Math.sin(theta) * r;

                const vx = cx + cosT * N[0] + sinT * B[0];
                const vy = cy + cosT * N[1] + sinT * B[1];
                const vz = cz + cosT * N[2] + sinT * B[2];

                this.vertices.push([vx, vy, vz]);
                grid[i][j] = this.vertices.length - 1;
            }
        }

        // Connect faces
        for (let i = 0; i < uSteps; i++) {
            const nextI = (i + 1) % uSteps;
            for (let j = 0; j < vSteps; j++) {
                const nextJ = (j + 1) % vSteps;
                const v1 = grid[i][j];
                const v2 = grid[nextI][j];
                const v3 = grid[nextI][nextJ];
                const v4 = grid[i][nextJ];
                this.faces.push([v1, v2, v3, v4]);
            }
        }
    }

    generateCalabiYauCrossSection(n, uSteps, vSteps) {
        for (let i = 0; i <= uSteps; i++) {
            const u = (i / uSteps) * Math.PI * 2;
            for (let j = 0; j <= vSteps; j++) {
                const v = (j / vSteps) * Math.PI * 2;
                const r = 1.0 + 0.3 * Math.cos(n * u) * Math.sin(n * v);
                const x = r * Math.sin(u) * Math.cos(v);
                const y = r * Math.cos(u) * Math.cos(v);
                const z = r * Math.sin(v) + 0.2 * Math.sin(3 * u);
                this.vertices.push([x * 1.3, y * 1.3, z * 1.3]);
            }
        }

        const stride = vSteps + 1;
        for (let i = 0; i < uSteps; i++) {
            for (let j = 0; j < vSteps; j++) {
                const a = i * stride + j;
                const b = (i + 1) * stride + j;
                const c = (i + 1) * stride + (j + 1);
                const d = i * stride + (j + 1);
                this.faces.push([a, b, c, d]);
            }
        }
    }

    generateOctahedralLattice(layers) {
        const step = 0.6;
        for (let x = -layers; x <= layers; x++) {
            for (let y = -layers; y <= layers; y++) {
                for (let z = -layers; z <= layers; z++) {
                    if (Math.abs(x) + Math.abs(y) + Math.abs(z) <= layers) {
                        this.vertices.push([x * step, y * step, z * step]);
                    }
                }
            }
        }
        // Connect nearby neighbor nodes
        const count = this.vertices.length;
        for (let i = 0; i < count; i++) {
            for (let j = i + 1; j < count; j++) {
                const dx = this.vertices[i][0] - this.vertices[j][0];
                const dy = this.vertices[i][1] - this.vertices[j][1];
                const dz = this.vertices[i][2] - this.vertices[j][2];
                const distSq = dx*dx + dy*dy + dz*dz;
                if (Math.abs(distSq - step*step) < 0.05) {
                    this.faces.push([i, j, j, i]); // wireframe edge
                }
            }
        }
    }

    generateGyroidSurface(uSteps, vSteps) {
        for (let i = 0; i < uSteps; i++) {
            const u = (i / uSteps) * Math.PI * 2 - Math.PI;
            for (let j = 0; j < vSteps; j++) {
                const v = (j / vSteps) * Math.PI * 2 - Math.PI;
                const x = u * 0.45;
                const y = v * 0.45;
                const z = 0.5 * (Math.sin(u) * Math.cos(v) + Math.sin(v) * Math.cos(u));
                this.vertices.push([x * 1.5, y * 1.5, z * 1.5]);
            }
        }

        for (let i = 0; i < uSteps - 1; i++) {
            for (let j = 0; j < vSteps - 1; j++) {
                const v1 = i * vSteps + j;
                const v2 = (i + 1) * vSteps + j;
                const v3 = (i + 1) * vSteps + (j + 1);
                const v4 = i * vSteps + (j + 1);
                this.faces.push([v1, v2, v3, v4]);
            }
        }
    }

    startLoop() {
        const loop = (now) => {
            this.frameTimeMs = now - this.lastFrameTime;
            this.lastFrameTime = now;
            this.fps = Math.round(1000 / (this.frameTimeMs || 16.6));

            if (this.autoRotate) {
                this.rotY += 0.008;
                this.rotX += 0.004;
            }

            this.render();
            requestAnimationFrame(loop);
        };
        requestAnimationFrame(loop);
    }

    render() {
        const ctx = this.ctx;
        const w = this.displayWidth;
        const h = this.displayHeight;
        const cx = w / 2;
        const cy = h / 2;

        ctx.clearRect(0, 0, w, h);

        // Subtle background grid
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let x = 0; x < w; x += 40) {
            ctx.moveTo(x, 0); ctx.lineTo(x, h);
        }
        for (let y = 0; y < h; y += 40) {
            ctx.moveTo(0, y); ctx.lineTo(w, y);
        }
        ctx.stroke();

        // Rotation matrix components
        const cosX = Math.cos(this.rotX), sinX = Math.sin(this.rotX);
        const cosY = Math.cos(this.rotY), sinY = Math.sin(this.rotY);
        const cosZ = Math.cos(this.rotZ), sinZ = Math.sin(this.rotZ);

        // Project vertices
        const projected = [];
        const transformed = [];

        for (let i = 0; i < this.vertices.length; i++) {
            let [x, y, z] = this.vertices[i];

            // Rotate Y
            let x1 = cosY * x + sinY * z;
            let z1 = -sinY * x + cosY * z;
            let y1 = y;

            // Rotate X
            let y2 = cosX * y1 - sinX * z1;
            let z2 = sinX * y1 + cosX * z1;
            let x2 = x1;

            // Rotate Z
            let x3 = cosZ * x2 - sinZ * y2;
            let y3 = sinZ * x2 + cosZ * y2;
            let z3 = z2;

            transformed.push([x3, y3, z3]);

            const cameraDist = 4.5;
            const persFactor = cameraDist / (cameraDist + z3);
            const px = cx + x3 * this.zoom * persFactor;
            const py = cy + y3 * this.zoom * persFactor;

            projected.push([px, py, z3, persFactor]);
        }

        // Quantum particle glow mode
        if (this.renderMode === 'quantum') {
            for (let i = 0; i < projected.length; i += 2) {
                const [px, py, z, f] = projected[i];
                const alpha = Math.max(0.15, Math.min(0.9, (z + 2) / 4));
                const radius = Math.max(1.2, 2.5 * f);
                ctx.fillStyle = `rgba(0, 229, 255, ${alpha})`;
                ctx.beginPath();
                ctx.arc(px, py, radius, 0, Math.PI * 2);
                ctx.fill();
            }
            return;
        }

        // Sort faces by average depth for painter's algorithm
        const sortedFaces = [];
        for (let i = 0; i < this.faces.length; i++) {
            const face = this.faces[i];
            const zAvg = (transformed[face[0]][2] + transformed[face[1]][2] + transformed[face[2]][2] + transformed[face[3]][2]) / 4;
            sortedFaces.push({ face, zAvg });
        }
        sortedFaces.sort((a, b) => a.zAvg - b.zAvg);

        // Render faces
        for (const item of sortedFaces) {
            const [i1, i2, i3, i4] = item.face;
            const p1 = projected[i1];
            const p2 = projected[i2];
            const p3 = projected[i3];
            const p4 = projected[i4];

            ctx.beginPath();
            ctx.moveTo(p1[0], p1[1]);
            ctx.lineTo(p2[0], p2[1]);
            ctx.lineTo(p3[0], p3[1]);
            ctx.lineTo(p4[0], p4[1]);
            ctx.closePath();

            if (this.renderMode === 'solid') {
                // Directional lighting from top-left front
                const t1 = transformed[i1], t2 = transformed[i2], t3 = transformed[i3];
                const ax = t2[0] - t1[0], ay = t2[1] - t1[1], az = t2[2] - t1[2];
                const bx = t3[0] - t1[0], by = t3[1] - t1[1], bz = t3[2] - t1[2];
                let nx = ay * bz - az * by;
                let ny = az * bx - ax * bz;
                let nz = ax * by - ay * bx;
                const nLen = Math.sqrt(nx*nx + ny*ny + nz*nz) || 1;
                nx /= nLen; ny /= nLen; nz /= nLen;

                // Light vector: [0.577, -0.577, 0.577]
                const dot = Math.max(0, nx * 0.5 - ny * 0.5 + nz * 0.7);
                const lightness = Math.floor(18 + dot * 45);
                const hue = 192; // Thinker Cyan/Teal
                
                ctx.fillStyle = `hsl(${hue}, 85%, ${lightness}%)`;
                ctx.fill();

                ctx.strokeStyle = 'rgba(0, 229, 255, 0.25)';
                ctx.lineWidth = 0.7;
                ctx.stroke();
            } else {
                // Wireframe mode
                ctx.strokeStyle = 'rgba(0, 229, 255, 0.65)';
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        }
    }

    getStats() {
        return {
            vertices: this.vertices.length,
            faces: this.faces.length,
            fps: this.fps,
            frameTime: this.frameTimeMs.toFixed(1),
            zoom: Math.round(this.zoom),
            rotX: this.rotX.toFixed(2),
            rotY: this.rotY.toFixed(2)
        };
    }
}

if (typeof window !== 'undefined') {
    window.CadEngine = CadEngine;
}
