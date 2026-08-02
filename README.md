# OrchX — Enterprise Multi-Agent AI Orchestration Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16%20App%20Router-black)](https://nextjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-06B6D4)](https://tailwindcss.com/)
[![Groq LPU](https://img.shields.io/badge/Groq-LPU%20Instant-purple)](https://groq.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-330%2B%20Models-orange)](https://openrouter.ai/)

**OrchX** is a production-grade, open-source AI Agent Orchestration platform designed for fault-tolerant multi-provider LLM routing, AES-256-GCM zero-trust credential isolation, layered memory persistence, interactive multi-agent node pipelines, and sandbox-safe plugin execution.

---

## 🚀 Quick Start Guide (Open Source Developers)

### 1. Prerequisites
* **Node.js**: v18.17+ or v20+
* **Python**: 3.10+
* **Git**: Installed
* **SQLite**: 3.x (Built into Python)

---

### 2. Full Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/rishgotrizz/OrchX.git
cd OrchX

# 2. Set up Python Runtime & Virtual Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e packages/orchx-core
pip install -e packages/orchx-runtime

# 3. Configure Master Encryption Key for SecretVault
export ORCHX_MASTER_KEY=$(python3 -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode('utf-8'))")
export ORCHX_DB_PATH="runtime.db"

# 4. Set up Frontend Web Application
cd frontend
npm install
npm run dev
```

Visit **`http://localhost:3000`** in your browser to access OrchX!

---

## 🔑 Managing API Keys in SecretVault CLI

OrchX features a zero-trust credential vault (`SecretVault`). Raw API keys are **never stored in plaintext** or committed to source control.

```bash
# Add Groq API Key
python3 packages/orchx-runtime/bin/orchx_vault.py add groq gsk_YOUR_GROQ_API_KEY

# Add OpenRouter API Key
python3 packages/orchx-runtime/bin/orchx_vault.py add openrouter sk-or-v1-YOUR_OPENROUTER_KEY

# Add OpenAI API Key
python3 packages/orchx-runtime/bin/orchx_vault.py add openai sk-proj-YOUR_OPENAI_KEY

# Test Live Provider Connections & Health
python3 packages/orchx-runtime/bin/orchx_vault.py test groq
python3 packages/orchx-runtime/bin/orchx_vault.py test openrouter

# List Managed Providers (Keys are masked)
python3 packages/orchx-runtime/bin/orchx_vault.py list
```

---

## 🏛️ System Architecture

```mermaid
graph TD
    A[Web Studio UI / CLI] --> B[OrchX Runtime Kernel]
    B --> C[Planner & Task Decomposition Engine]
    B --> D[Multi-Agent Scheduler]
    C --> E[Worker Runtime Pool]
    D --> E
    E --> F[Circuit-Breaker Provider Router]
    E --> G[Subprocess Sandbox Plugins]
    E --> H[Layered Memory Engine]
    F --> I[SecretVault - AES-256-GCM]
    F --> J[Live Providers: Groq, OpenRouter, Gemini, OpenAI]
```

### Core Architecture Components

| Component | Directory | Description |
| :--- | :--- | :--- |
| **`orchx-core`** | `packages/orchx-core` | Core protocols, Pydantic contracts, domain interfaces, and event primitives. |
| **`orchx-runtime`** | `packages/orchx-runtime` | Subsystem implementations: `SecretVault`, `BaseRealProvider`, `LayeredMemory`, and `TransportLayer`. |
| **`Frontend App`** | `frontend` | Next.js 16 App Router interface featuring Mission Control, Workflow Forge, Runtime Observatory, Documents Studio, and Settings Studio. |
| **`Plugin Sandbox`** | `packages/orchx-runtime/builtin_plugins.py` | Subprocess isolation for Git, Filesystem, Terminal, Python, Docker, and Browser automation. |

---

## 🛠️ Main Feature Studios

1. **Mission Control (`/mission-control`)**:
   * Type any agentic goal (e.g. *"Build Calculator App"*, *"Build CRM Platform"*).
   * Automatically breaks goals down into **Autonomous Action Plans** and logs **Autonomous Decision Ledgers**.

2. **Workflow Forge (`/workflow-forge`)**:
   * Interactive `@xyflow/react` multi-agent node pipeline editor.
   * Dynamically renders nodes based on active Mission Control goals.
   * Real-time latency inspection and execution log streaming.

3. **Runtime Observatory (`/runtime-observatory`)**:
   * Live telemetry monitoring for kernel heartbeat, CPU load, and memory utilization.
   * Live API probe buttons for **Groq (255ms)** and **OpenRouter (1970ms, 337 models)**.
   * Active worker pool management (`groq-agent-01`, `openrouter-agent-01`, `gemini-agent-01`).

4. **Documents Studio (`/documents-studio`)**:
   * Categorized document vault spanning Product, Engineering, Research, AI Intelligence, and Output contracts.

5. **Settings Studio (`/settings-studio`)**:
   * Full provider API key management, model selection, temperature/max token tuning, circuit-breaker failover policies, security sandboxing, and UI appearance controls.

---

## 🌐 Deploying to Production (Vercel)

OrchX is fully configured for zero-configuration Vercel deployment:

1. Push your repository to GitHub:
   ```bash
   git push origin main
   ```
2. Connect your repository in the [Vercel Dashboard](https://vercel.com).
3. Set Root Directory to `frontend`.
4. Deploy! Live demo: **[https://orch-x.vercel.app/](https://orch-x.vercel.app/)**

---

## 🤝 Contributing & License

We welcome open-source contributions! Feel free to open issues or submit pull requests.

* **License**: MIT License — free for personal and commercial usage.
