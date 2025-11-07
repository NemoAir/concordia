# 落地实施文档索引

本目录包含“CHIME: Conversational Harmonized Interactive Multi‑agent Environment（Concordia + Nomad + 聊天室）”从架构到部署的完整落地说明。

- 架构总览: `ARCHITECTURE.md`
- Concordia 改造方案: `CONCORDIA_MODS.md`
- Orchestrator API（REST/WS）: `ORCHESTRATOR_API.md`
- 聊天室路径结论：首选“Java 网关内建 WebSocket 聊天”，Matrix 作为可选方案。
- 聊天室(Matrix + Bot)对接（可选）: `MATRIX_INTEGRATION.md`
- 客户端(Tauri)实现要点: `TAURI_CLIENT.md`
- 部署与运维(Nomad/Consul/HCL 模板): `DEPLOYMENT.md`
- 安全与可观测性: `SECURITY_OBSERVABILITY.md`
- 交付计划与团队分工: `DELIVERY_PLAN.md`

补充:
- Nomad 作业模板: `../nomad/`
- 本仓库贡献/规范: `AGENTS.md`
