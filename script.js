class FalconSystem {
    constructor() {
        this.mode = 'peace'; // peace, war, caution
        this.throughput = 0;
        this.canvas = document.getElementById('topology-graph');
        this.ctx = this.canvas.getContext('2d');
        this.nodes = [];

        this.init();
    }

    init() {
        console.log("Falcon Eye 2026 Core Systems Loading...");
        this.setupClock();
        this.setupEventListeners();
        this.resizeCanvas();
        this.initNodes();
        this.animate();
        this.startSimulation();
        this.log("SYSTEM INITIALIZED. ZERO TRUST ARCHITECTURE ACTIVE.", "SYSTEM");
    }

    setupClock() {
        const updateTime = () => {
            const now = new Date();
            document.getElementById('clock').innerText = now.toLocaleTimeString('en-GB');
        };
        setInterval(updateTime, 1000);
        updateTime();
    }

    setupEventListeners() {
        document.getElementById('btn-peace').addEventListener('click', () => this.setMode('peace'));
        document.getElementById('btn-caution').addEventListener('click', () => this.setMode('caution'));
        document.getElementById('btn-war').addEventListener('click', () => this.setMode('war'));

        window.addEventListener('resize', () => this.resizeCanvas());
    }

    setMode(newMode) {
        if (this.mode === newMode) return;

        // Simulating "Rust Backend" call via promise delay
        this.log(`INITIATING MODE SHIFT: ${this.mode.toUpperCase()} -> ${newMode.toUpperCase()}`, "AUTH_GATE");

        setTimeout(() => {
            this.mode = newMode;
            document.body.className = `mode-${newMode}`;

            // Update Active Dock Item
            document.querySelectorAll('.dock-item').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[data-mode="${newMode}"]`).classList.add('active');

            // Update Security Status Text
            const statusText = document.querySelector('.status-text');
            if (newMode === 'peace') statusText.innerText = "SYSTEM: ONLINE";
            if (newMode === 'caution') statusText.innerText = "SYSTEM: MONITORING";
            if (newMode === 'war') statusText.innerText = "SYSTEM: ENGAGED";

            this.log(`MODE SHIFT CONFIRMED: ${newMode.toUpperCase()}`, "KERNEL");
        }, 100);
    }

    log(message, source = "NET") {
        const timestamp = new Date().toISOString().split('T')[1].slice(0, 12);
        const logContainer = document.getElementById('log-container');

        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.innerHTML = `
            <span class="log-timestamp">[${timestamp}]</span>
            <span class="log-source" style="color: #666; margin-right: 5px;">${source}::</span>
            <span class="log-action">>> ${message}</span>
        `;

        logContainer.prepend(entry);

        // Keep log size manageable
        if (logContainer.children.length > 50) {
            logContainer.lastChild.remove();
        }
    }

    startSimulation() {
        // Update Throughput
        setInterval(() => {
            let base = 90;
            if (this.mode === 'war') base = 400;
            if (this.mode === 'caution') base = 150;

            const variation = Math.random() * 20 - 10;
            this.throughput = (base + variation).toFixed(1);
            document.querySelector('.throughput-value').innerText = `${this.throughput} TB/s`;

            // Randomly log something
            if (Math.random() > 0.90) {
                const actions = ["PACKET_INSPECT", "SIG_VERIFY_SUCCESS", "NODE_HANDSHAKE", "KEY_ROTATION", "APT_SCAN"];
                const randomAction = actions[Math.floor(Math.random() * actions.length)];
                this.log(`${randomAction} :: HASH_${Math.floor(Math.random() * 9999)}`, "RING_BUFFER");
            }
        }, 500);

        // Update Uncertainty
        setInterval(() => {
            let baseScore = 0.02;
            if (this.mode === 'caution') baseScore = 12.5;
            if (this.mode === 'war') baseScore = 45.0;

            const score = (baseScore + Math.random() * 2).toFixed(2);
            document.getElementById('uncertainty-score').innerText = `${score}%`;

            // Update Holographic Noise Intensity
            const opacity = 0.15 + (parseFloat(score) / 100) * 0.5;
            const noiseEl = document.querySelector('.holographic-noise');
            if (noiseEl) noiseEl.style.opacity = opacity;
        }, 2000);
    }

    /* Canvas Logic */
    resizeCanvas() {
        if (!this.canvas.parentElement) return;
        this.canvas.width = this.canvas.parentElement.offsetWidth;
        this.canvas.height = this.canvas.parentElement.offsetHeight;
        this.initNodes();
    }

    initNodes() {
        this.nodes = [];
        // Dynamic node count based on screen size
        const count = Math.min(100, Math.floor((this.canvas.width * this.canvas.height) / 8000));

        for (let i = 0; i < count; i++) {
            this.nodes.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 1,
                vy: (Math.random() - 0.5) * 1,
                size: Math.random() * 2 + 1
            });
        }
        document.getElementById('node-count').innerText = count;
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        const color = this.getColor();
        this.ctx.fillStyle = color;
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 0.5;

        // Update and Draw Nodes
        this.nodes.forEach(node => {
            // Speed factor
            let speed = 0.5;
            if (this.mode === 'caution') speed = 1;
            if (this.mode === 'war') speed = 3;

            node.x += node.vx * speed;
            node.y += node.vy * speed;

            if (node.x < 0 || node.x > this.canvas.width) node.vx *= -1;
            if (node.y < 0 || node.y > this.canvas.height) node.vy *= -1;

            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, node.size, 0, Math.PI * 2);
            this.ctx.fill();
        });

        // Draw Connections
        for (let i = 0; i < this.nodes.length; i++) {
            for (let j = i + 1; j < this.nodes.length; j++) {
                const dx = this.nodes[i].x - this.nodes[j].x;
                const dy = this.nodes[i].y - this.nodes[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                let connectDistance = 100;
                if (this.mode === 'war') connectDistance = 150;

                if (dist < connectDistance) {
                    this.ctx.globalAlpha = (1 - (dist / connectDistance)) * 0.5;
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.nodes[i].x, this.nodes[i].y);
                    this.ctx.lineTo(this.nodes[j].x, this.nodes[j].y);
                    this.ctx.stroke();
                }
            }
        }
        this.ctx.globalAlpha = 1;

        requestAnimationFrame(() => this.animate());
    }

    getColor() {
        if (this.mode === 'peace') return '#00F2FF'; // Cyan
        if (this.mode === 'war') return '#FF4B4B';   // Coral
        if (this.mode === 'caution') return '#FFB800'; // Amber
        return '#00F2FF';
    }
}

// Start System
window.addEventListener('DOMContentLoaded', () => {
    window.falconSystem = new FalconSystem();
});
