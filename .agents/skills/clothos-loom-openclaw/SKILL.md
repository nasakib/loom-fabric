---
name: clothos-loom-openclaw
description: Comprehensive operational guide and playbook for managing, configuring, and executing distributed workloads across ClothOS, Loom Fabric, and OpenClaw systems.
---

# ClothOS, Loom Fabric & OpenClaw Systems Skill

Use this skill whenever:
- Executing distributed compute tasks across heterogeneous local (RTX 3060) and remote (Ray cluster `WIN-7CMAQLVP8MV`) hardware.
- Configuring or debugging OpenClaw AI providers, models, or MSIX Gateway configs.
- Sanitizing and formatting function tool definitions (`properties`, `id`, `tool_call_id`).
- Monitoring cluster state via `loom-smi` or synchronizing nodes via `sync_cluster_nodes.py`.

## 1. Tool Schema Requirements ("Valid Properties ID")
Whenever declaring or proxying function calling tools:
- The parameters schema MUST specify `"type": "object"` and `"properties": {...}`.
- Every property inside `"properties"` must have an explicit type (e.g. `{"type": "string"}`).
- Tool invocations must have non-empty `"id": "call_..."` strings.
- Tool result returns must include `"role": "tool"` and `"tool_call_id"`.

## 2. OpenClaw MSIX Gateway Interaction
- Running gateway path: `C:\Users\P7-X4\.openclaw\openclaw.json` (MSIX Sandbox user `P7-X4`).
- Staging path for patches: `C:\Users\P7-X4\Shared\`.
- Apply patch command:
  ```powershell
  openclaw config patch --file "C:\Users\P7-X4\Shared\patch.json"
  ```
- Companion Tray App session cache:
  `C:\Users\natsa\AppData\Local\Packages\OpenClawFoundation.OpenClaw_rfcbke2p71se2\LocalCache\Local\OpenClawTray\last-chat-state.json`.

## 3. Distributed Compute & Grid-Aware Arbitrage
- Local Silicon: NVIDIA GeForce RTX 3060 12GB (Device 0).
- Remote Cluster Head: `192.168.99.2:6379` (Device 1).
- P2P Energy Arbitrage: Night scientific workloads; Day CSP/CSC compute broker.
- Subprocess hygiene: Strip `PYTHONHOME`, `PYTHONPATH`, and `VIRTUAL_ENV` when switching between Python 3.12 and 3.14.
