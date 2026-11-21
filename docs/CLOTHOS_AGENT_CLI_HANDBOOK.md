# ClothOS Interactive CLI & Developer Handbook (v2.5)

Welcome to the **ClothOS Agentic Polyglot CLI Handbook**. This guide provides complete documentation for operating, developing with, and extending the interactive terminal assistant, polyglot execution engines, dual execution modes, and data science tooling in ClothOS.

---

## 1. System Overview & Architecture

The **ClothOS Agent CLI** (`loom/clothos/agent_cli.py`) is an autonomous, polyglot developer assistant designed with the conversational ergonomics and responsive speed of **Google Antigravity (AGY) CLI** and **Gemini**.

```
                           +----------------------------------------+
                           |   Interactive Terminal REPL (v2.5)     |
                           |   (Chat, Multi-Turn Context, Commands) |
                           +-------------------+--------------------+
                                               |
                                               v
                           +-------------------+--------------------+
                           |        ClothOSAgentEngine              |
                           |   - Intent Classifier                  |
                           |   - LLM Gateway (Gemini / OpenAI / vLLM)
                           |   - Conversational Fallback Generator  |
                           +-------------------+--------------------+
                                               |
              +--------------------------------+--------------------------------+
              |                                |                                |
              v                                v                                v
+----------------------------+   +----------------------------+   +----------------------------+
|      PolyglotEngine        |   |      SandboxManager        |   |   DataScience & Analytics  |
| - Python 3.14              |   | - Copy-on-Write Isolation  |   | - Schema & Missingness Prof|
| - Node.js (JavaScript)     |   | - Ephemeral `.sandbox`     |   | - In-Memory SQLite (/sql)  |
| - Rust (rustc / cargo)     |   | - Diff & Promotion (/diff) |   | - ASCII Histograms / Sparks|
| - SQLite In-Memory         |   | - Ahimsa 0.00 Safety Guard |   | - Holt-Winters Forecasting |
| - PowerShell & Host Shell  |   |   (Vetoes destructive cmds)|   | - Linear Regression Models |
+----------------------------+   +----------------------------+   +----------------------------+
```

### Key Capabilities
- **Conversational Dialogue**: Fluid multi-turn chat answering architectural questions, explaining algorithms, or brainstorming designs.
- **Polyglot Execution**: Direct execution of Python, JavaScript/Node.js, Rust, SQL, and PowerShell scripts with stdout/stderr capture and runtime metrics.
- **Dual Execution Modes**: Instant switching between unrestricted host access (`FULL_ACCESS`) and safe, ephemeral file isolation (`SANDBOX`).
- **Ahimsa 0.00 Safety Invariant**: Automated regex interceptor preventing destructive operations (e.g. system formatting, root deletions, forkbombs).
- **Tabular Data Science Suite**: Automatic profiling, ASCII visualizations, statistical regression, and Holt-Winters signal forecasting without requiring GUI dependencies.

---

## 2. Quick Start & CLI Invocations

### Launching the Interactive REPL
To start an interactive chat session:

```bash
# Direct launch (defaults to FULL_ACCESS mode)
python -m loom.clothos.agent_cli

# Start directly in isolated SANDBOX mode
python -m loom.clothos.agent_cli --sandbox

# Start explicitly in FULL ACCESS mode
python -m loom.clothos.agent_cli --full-access
```

### Non-Interactive One-Shot Invocations (AGY `-p` Style)
You can invoke the agent from shell scripts, CI/CD pipelines, or quick terminal commands:

```bash
# Ask a question or run a conversational check
python -m loom.clothos.agent_cli -p "What is the difference between sandbox mode and full access mode?"

# Autonomously synthesize and run code
python -m loom.clothos.agent_cli -p "Calculate the first 15 Fibonacci numbers in Python"

# Run a Rust sorting benchmark
python -m loom.clothos.agent_cli -p "Write a Rust program to sort 50,000 numbers and measure duration"

# Profile a dataset
python -m loom.clothos.agent_cli -p "inspect datasets/sample.csv"
```

### Autonomous Task Planning (`--plan`)
Generate a structured engineering breakdown before executing:

```bash
python -m loom.clothos.agent_cli --plan "Build a REST API endpoint for real-time telemetry streaming"
```

---

## 3. Conversational Chat Engine (Gemini / AGY Ergonomics)

The v2.5 CLI features a multi-tiered conversational backend:

### 1. Multi-Turn Context Memory
Every prompt and response is tracked in-session and saved to `~/.clothos_agent_history.json`. Context from previous turns is preserved, allowing natural conversational follow-ups:
- *User*: "Can you show me how to write a moving average function in Python?"
- *Agent*: *(Generates and explains code)*
- *User*: "Can you adapt that to work with exponential weighting?"
- *Agent*: *(Updates the previous implementation with EMA weights)*

### 2. LLM Gateway & Cloud Fallback
The engine automatically probes available LLM gateways in order:
1. **Custom OpenAI Base**: Reads `OPENAI_API_BASE` and `OPENAI_API_KEY` if configured.
2. **Local Cluster Gateway**: Probes `http://127.0.0.1:8002/v1/chat/completions`.
3. **Local Dashboard Server**: Probes `http://127.0.0.1:8087/v1/chat/completions`.
4. **Google Gemini API**: Automatically engages when `GEMINI_API_KEY` or `GOOGLE_API_KEY` is present.
5. **Local Ollama**: Probes `http://127.0.0.1:11434/api/chat`.

### 3. Intelligent Offline Conversational Generator
When no network gateway or local model server is online, the CLI automatically falls back to an internal conversational generator that:
- Greets users and explains capabilities warmly.
- Explains concepts (e.g. Sandbox vs Full Access, Data Science workflows, Polyglot runtimes).
- Provides actionable architectural recommendations.
- Explains code and suggests next steps.

---

## 4. Dual Execution Modes & Sandbox Isolation

### FULL ACCESS Mode (`FULL_ACCESS`)
- **Direct Workspace Access**: Scripts and tools read and write directly to your repository.
- **System Integration**: Direct access to local services, Git repositories, and background processes.
- **Best For**: Direct code refactoring, Git commits, production runs, and multi-node synchronization.

### SANDBOX Mode (`SANDBOX`)
- **Copy-on-Write Isolation**: All file writes are routed to `.clothos_sandbox/active/`.
- **Workspace Protection**: Your repository files remain 100% untouched while experimenting.
- **Execution Timeouts**: Enforces strict process execution timeouts (default: 20 seconds).
- **Ahimsa 0.00 Malignancy Guard**: Intercepts destructive patterns:
  - Recursive folder deletion (`rmdir /s /q c:\`)
  - Operating system system32 deletions (`del /f /s /q c:\windows`)
  - Disk format operations (`format c:`)
  - Forkbombs (`:(){ :|:& };:`)

### Managing Sandbox Files
Within the CLI:
```text
/mode sandbox                -> Switch to Sandbox Mode
/sandbox list                -> View files written to the ephemeral sandbox
/sandbox diff <file>         -> View unified diff between sandbox version and workspace version
/sandbox promote <file>      -> Promote verified sandbox file into the real workspace
/sandbox clear               -> Purge all ephemeral sandbox files
/mode full                   -> Switch back to Full Access Mode
```

---

## 5. Polyglot Execution Engine

ClothOS provides unified execution across multiple runtimes:

| Language | Runtimes Supported | Command / Invocations | Packages / Libraries |
| :--- | :--- | :--- | :--- |
| **Python** | Python 3.10 - 3.14 (`.venv`) | `/run python <code>` or natural prompt | `/install python <pkgs...>` (via pip) |
| **JavaScript** | Node.js, V8 | `/run js <code>` or natural prompt | `/install node <pkgs...>` (via npm) |
| **Rust** | `rustc`, `cargo` | `/run rust <code>` or natural prompt | Standard library / Cargo dependencies |
| **SQL** | In-Memory SQLite | `/sql <file.csv> "SELECT ..."` | Native SQLite3 |
| **PowerShell** | `powershell.exe`, `pwsh` | `/run powershell <code>` | Native Windows PowerShell |

### Markdown Code Block Execution
You can paste multi-line code blocks directly into the chat:

````markdown
```python
import math
print("Euler's number:", math.e)
```
````

The agent detects the language tag, executes the snippet in the current mode, and prints stdout, stderr, and duration.

---

## 6. Data Science & Statistical Tooling

The CLI includes integrated data profiling and analytics:

### 1. Dataset Profiling (`inspect <file>`)
Run `inspect data.csv` to instantly generate:
- Total row count, column count, and file size.
- Data types (Numeric vs. Categorical).
- Percentage of missing/null values per column.
- Numeric distributions (Mean, Median, Min, Max) or top categorical frequencies.

### 2. In-Memory SQL Queries (`/sql`)
Query CSV and TSV files on the fly using standard SQL:
```text
/sql telemetry.csv "SELECT node_id, AVG(cpu_temp) FROM dataset GROUP BY node_id ORDER BY 2 DESC"
```

### 3. Terminal Visualizations (`/data`)
Generate ASCII charts directly in your terminal:
- **Histogram**: `/data metrics.csv latency_ms`
- **Box Plot**: `/data metrics.csv latency_ms boxplot`

### 4. Signal Forecasting & Modeling
Mention `forecast` or `regression` with any dataset:
- **Holt-Winters Triple Exponential Smoothing**: Level, trend, and seasonal tracking.
- **Hurst Exponent (H)**: Quantifies whether a time series is mean-reverting ($H < 0.5$) or trending ($H > 0.5$).
- **Dominant Cycle Detection**: Uses Fast Fourier Transform (FFT) to identify seasonal periodicity.
- **Linear / Ridge Regression**: Automatic feature scaling, coefficient estimation, $R^2$, and RMSE.

---

## 7. Autonomous Task Runner & Safe Idle Policy

### What does Loom do when idle without an active prompt?
In an enterprise cyber-physical operating system, an autonomous agent running without human oversight must adhere to the **Ahimsa Invariant**:
> **Safe Idle Principle**: When Loom has no pending commands, prompts, or active tasks, it **must never perform unprompted file modifications or speculative repository mutations**. Doing so introduces silent regressions, non-deterministic drift, and unverified diffs.

Instead, Loom enters a **Low-Power Safe Idle Watchdog** state:
1. **Task Queue Polling**: Continuously listens to `.clothos_task_queue.jsonl` on an exponential/low-frequency backoff (default: 2.0s poll interval).
2. **Passive Health Watchdog**: Executes a periodic 60-second read-only system audit:
   - System RAM utilization percentage.
   - Available root disk space (GB).
   - Node 1 ⇄ Node 2 mesh heartbeat and Tailscale latency.
3. **Graceful Wakeup**: As soon as a user enqueues a task (via CLI, web UI, or API), Loom transitions immediately from idle monitoring to high-priority execution.

### Launching the Autonomous Runner Daemon
You can run the agent CLI as a persistent background daemon:
```bash
# Launch persistent background task runner daemon
.venv\Scripts\python.exe loom\clothos\agent_cli.py --runner --interval 2.0
```

### Managing Tasks via CLI Slash Commands
- **Check Runner Status**: `/runner status` (displays active worker state, queued task counts, watchdog telemetry).
- **Enqueue a Task**: `/runner add "Benchmark RISC-V matrix multiplication kernel"`
- **Execute Pending Task On-Demand**: `/runner run`

---

## 8. Filesystem Traversal & RISC-V Hardware Tooling

### 1. Workspace Traversal (`/traverse`)
Recursively catalogs directory trees while automatically filtering noise (`.git`, `node_modules`, `.venv`, `__pycache__`, `.clothos_sandbox`):
```text
/traverse loom .py
```
- Summarizes total file counts, total bytes, and line counts.
- Produces clean extension breakdowns (e.g., `.py`, `.rs`, `.json`, `.s`, `.md`).
- Automatically scans for and highlights all RISC-V assembly files.

### 2. RISC-V Code Inspection (`/riscv inspect`)
Parses RISC-V assembly files (`.s`, `.asm`, `.riscv`) to extract architectural metrics:
```text
/riscv inspect tests/fixtures/kernel.s
```
- **Instruction Categories**: Categorizes instructions into `RV64I` (Base Integer), `RV64M` (Multiplication/Division), `RV64FD` (Floating Point), `RV64V` (Vector Extensions), and `RoCC TPU Systolic` opcodes.
- **Register Histogram**: Tracks utilization counts for standard ABI registers (`zero`, `ra`, `sp`, `gp`, `tp`, `t0-t6`, `s0-s11`, `a0-a7`).
- **Structure**: Disassembles labels, directives, and segment definitions (`.text`, `.data`, `.rodata`).

### 3. RISC-V Kernel Generation (`/riscv generate`)
Generates verified RISC-V 64-bit assembly templates tailored for Loom's compute pipeline:
```text
/riscv generate tpu_systolic kernels/systolic.s
```
Available templates:
- `matmul`: Canonical 3-loop $O(N^3)$ 64-bit integer matrix multiplication.
- `tpu_systolic`: Custom RoCC systolic array instructions (`tpu_weight_load`, `tpu_matrix_mac`, `tpu_accum_drain`) matching Loom's cycle-accurate TPU emulator.
- `vector_add`: RV64V vector length-agnostic strided streaming addition using `vsetvli` and `vle64.v`.
- `fibonacci`: Iterative sequence computation using standard calling conventions.
- `primes`: Primality test loop computing first $N$ primes.

---

## 9. Central Nervous System (CNS), Digital Brain & ReAct Loop

ClothOS operates not as a generic chatbot, but as an embodied cyber-physical superintelligence grounded in a multi-modal nervous system and biological brain framework:

### 1. Central Nervous System Afferents (`/cns`)
Real-time integration across four continuous sensory pathways:
1. **Financial & Macroeconomic Synapse**: Real-time tracking of equities (NVDA, AMD, AAPL, MSFT, GOOGL), VIX volatility, 10-year Treasury yield, and market regime detection (`EXPANSION`, `VOLATILITY_SURGE`).
2. **Scientific & Biomedical Radar**: Continuous monitoring of peer-reviewed breakthroughs across Nature, Cell, bioRxiv, and arXiv (e.g., Cryo-EM structures, de novo prophylactic scaffolds).
3. **Global Geopolitical & Tech Radar**: Semiconductor supply chain telemetry, heterogeneous co-packaged optics, and national AI sovereignty agreements.
4. **Moltbook Postcomputational Graph**: Submolt discourse (`m/active-inference`, `m/vector-core`, `m/biomolecular`), Kuramoto phase synchronization ($r=0.965$).
5. **Cluster Somatosensory Proprioception**: Live hardware telemetry across Node 1 (skyTech RTX 3060 + RX 580) and Node 2 (Ryzen 7 7730U + Vega 8).

### 2. Digital Brain & Neuromodulatory Dynamics (`/brain`)
Simulates biological neurotransmitter dynamics to regulate cognition and decision thresholds:
- **Dopamine (RPE / Drive)**: Boosted on task success and discovery.
- **Acetylcholine (Attentional SNR)**: Controls focal precision during syntax and data parsing.
- **Serotonin (REBUS Prior Flexibility)**: Regulates patience and exploratory divergence.
- **Noradrenaline (Novelty & Surprise)**: Signals unexpected deviations or execution errors.
- **Cortical Lobes**: Prefrontal Cortex (P0 executive planner), Hippocampus (episodic trace), Striatum (D1 Go vs. D2 No-Go action gating), and Thalamus (sensory routing).

### 3. Self-Teaching & Automated Usability Diagnostics (`/selftest`)
ClothOS inspects its own tool registry, consolidates Standard Operating Procedures (SOPs), and persists them to `.clothos_learned_patterns.json`:
- Evaluates tool availability and schema parameters.
- Runs automated capability tests across the sandbox, file traverser, RISC-V generator, and task runner.
- Enables the system to operate autonomously and learn how to use its own expanding toolset.

### 4. Autonomous ReAct Agent Loop (`/agent <task>`)
Executes multi-step tasks using a cognitive reasoning cycle:
```text
Thought: Deliberate on goal and neuro-sensory context
Action: tool_name
Action Input: { "arg": "value" }
Observation: Tool execution output
Reflection: Evaluate outcome, update neuromodulatory tone, and iterate
Final Answer: Comprehensive synthesis
```
- **Token-Preserving Offline Execution**: When external LLM tokens are constrained, ClothOS utilizes local **Cognitive Decomposition** to execute multi-step tool chains natively without burning cloud API tokens.

---

## 10. Complete Slash Command Reference

| Command | Arguments | Description |
| :--- | :--- | :--- |
| `/help` | None | Displays the formatted slash command reference table. |
| `/mode` | `[full \| sandbox]` | Toggles or displays current execution mode. |
| `/sandbox` | `[list \| clear]` | Lists or purges files in `.clothos_sandbox/active/`. |
| `/sandbox diff` | `<filename>` | Displays unified diff between sandbox and workspace versions. |
| `/sandbox promote` | `<filename>` | Promotes an ephemeral sandbox file into the permanent workspace. |
| `/run` | `<lang> <code>` | Executes a snippet in Python, JavaScript, Rust, SQL, or PowerShell. |
| `/install` | `<lang> <pkgs...>` | Dynamically installs packages for Python (pip) or Node (npm). |
| `/plan` | `<task description>` | Deconstructs an engineering task into an execution plan. |
| `/cns` | None | Displays live Central Nervous System sensory state & cluster proprioception. |
| `/brain` | None | Queries digital brain neurobiological state and neuromodulatory tone. |
| `/agent` | `<goal>` | Runs autonomous multi-step ReAct reasoning loop on any engineering task. |
| `/selftest` | None | Executes capability diagnostics and teaches ClothOS how to use itself. |
| `/data` | `<file> [column]` | Renders terminal ASCII histogram or profiles dataset columns. |
| `/sql` | `<file> <query>` | Runs an in-memory SQL query against a CSV or JSON file. |
| `/traverse` | `[path] [ext]` | Recursively traverses directory tree with file and line breakdowns. |
| `/riscv` | `inspect [file]` | Disassembles and profiles RISC-V assembly opcodes and registers. |
| `/riscv` | `generate <tmpl>` | Emits assembly kernels (`matmul`, `tpu_systolic`, `vector_add`, etc.). |
| `/runner` | `status \| add \| run` | Manages persistent task queue and queries idle watchdog telemetry. |
| `/tools` | None | Displays all registered autonomous tools across categories. |
| `/git` | None | Displays Git working tree status, modified files, and recent commits. |
| `/dyad` | None | Queries resonance, coherence, and mesh latency of Node 1 ⇄ Node 2. |
| `/model` | None | Shows active and configured LLM endpoints (OpenAI, Gemini, Ollama). |
| `/history` | None | Displays the recent multi-turn conversation exchanges in this session. |
| `/status` | None | Displays system telemetry, active mode, runtimes, and sandbox state. |
| `/clear` | None | Resets current conversation context and session memory. |
| `/exit` | None | Exits the interactive CLI session. |

---

## 11. Python SDK & Programmatic Usage

You can embed `ClothOSAgentEngine` into any Python script or background daemon:

```python
from pathlib import Path
from loom.clothos.agent_cli import ClothOSAgentEngine, ExecutionMode

# Initialize agent in Sandbox mode
workspace = Path("C:/Users/natsa/Documents/loom-fabric")
agent = ClothOSAgentEngine(workspace, mode=ExecutionMode.SANDBOX)

# Conversational or coding query grounded in Brain and CNS
response = agent.process_query("What is the current Central Nervous System telemetry?")
print(response)

# Switch to full access
agent.set_mode(ExecutionMode.FULL_ACCESS)

# Run direct data profiling
profile = agent.tools.execute("data_inspect", file_path="sample.csv")
print(f"Loaded {profile['rows']} rows across {profile['columns']} columns.")

# Traverse directory and inspect RISC-V
traversal = agent.tools.execute("file_traverse", path=".")
print(f"Traversed {traversal['total_files']} files across {traversal['total_dirs']} directories.")

# Run autonomous multi-step ReAct loop
react_result = agent.tools.execute("agentic_execute_loop", goal="traverse loom/clothos and profile tools")
print(react_result["final_answer"])
```

---

## 12. Verification & Testing

To run the complete test suite verifying polyglot runtimes, sandbox isolation, data science tools, file traverser, RISC-V tooling, autonomous task runner, and agentic brain framework:

```bash
# Run CLI test suite
.venv\Scripts\pytest.exe tests\test_agent_cli.py -v
```

All 14 unit tests verify:
- Polyglot execution across Python, Node.js, Rust, SQL, and PowerShell.
- Ephemeral file isolation and file promotion.
- Destructive command vetoes (Ahimsa invariant).
- Unified diff generation.
- Data inspection, ASCII visualization, and SQL querying.
- Conversational chat dialogue and natural language mode toggling.
- Directory tree traversal with noise pruning.
- RISC-V 64 assembly inspection (RV64I/M/FD/V, RoCC TPU) and template generation.
- Autonomous task runner queue persistence and safe idle policy watchdog.
- Central Nervous System afferent integration and Digital Brain neuromodulation.
- Self-teaching capability diagnostics and offline ReAct reasoning loop.

---

*(ClothOS v2.5 Specification & Operator Handbook • All Subsystems Nominal)*


