# 交付计划与团队分工（MVP）

## 团队与栈
- 平台：Nomad/Consul 专家（Go/DevOps）
- 后端：Java（Spring/Quarkus，WebFlux/WS，Consul 客户端）
- Python：少量（Orchestrator/FastAPI、Concordia 改造）— 可大量由 AI 产出初稿
- 客户端：Tauri（Rust+前端），资深前端负责 UI/动效

## 里程碑与时间预估（2.5–3 周，聊天室路径：网关内建 WS）
 - 第 1 周：
  - 网关脚手架 + Consul 集成 + 房间/用户 REST/WS（Java，3 天）— 实现极薄的 WS 聊天（广播 tick + 玩家发言），无需引入 Matrix。
  - Orchestrator 初版（FastAPI，REST/WS，容器化）（AI+Python，2 天）
  - Nomad 作业模板（orchestrator/gateway/agent-llm）（平台，2 天）
 - 第 2 周：
  - Concordia 改造（host 参数、remote_ollama Prefab、可选 deadline）（AI+Python，1 天）
  - 三端联调：网关↔Orch↔LLM（2 天）
  - Tauri 聊天室 MVP（使用聊天组件库拼装时间线/输入/状态）（前端，3 天）
 - 第 3 周：
  - 观测/降级/恢复（2 天）
  - 安全/回放/持久化（2–3 天）
  - 试运行与缓冲（1–2 天）

## 分工
- Java 后端：
  - 房间/会话/鉴权（JWT）、WS 广播；Consul 服务发现；Orchestrator 代理；Resilience4j；OpenTelemetry。
- Python（AI 协作）：
  - Orchestrator API/WS、tick 调度、LLM 调用；Concordia 改造/集成；集成测试；Dockerfile。
- 平台：
  - Nomad HCL 作业、Consul 注册与 Connect、Ingress、证书；对象存储/DB；Prom/Grafana/Loki。
- 客户端：
  - Tauri 聊天室、状态面板、动画与缓存；打包与自动更新（可选）。

## AI 可完成的部分（与聊天室决策一致）
- Concordia 改造补丁（`ollama_model(host)`、`remote_ollama__Entity`、deadline 示例）
- Orchestrator（FastAPI）全量脚手架、OpenAPI、容器化与测试
- Nomad HCL 模板（orchestrator/gateway/agent-llm/synapse/element）
- Java 网关脚手架（WebFlux/WS/Consul/JWT，内建最小 WS 聊天）
- Tauri 客户端模板（WS 客户端、时间线/面板组件）

## 验收标准（MVP）
- 单房间、2–4 名玩家：
  - 玩家 LLM 可被调用；超时降级生效；
  - 客户端实时接收 tick，展示消息与分数；
  - 检查点/历史可回放；
  - 指标与日志齐全；
- 端到端安全链路（TLS/JWT/mTLS）。

## 备选：Matrix（可选后续推进）
- 仅当需要现成 IM 能力（E2EE/联邦/搜索/权限）时再引入；
- 届时通过 Bot 桥接 Orchestrator，不改变 CHIME 事件与世界状态模型。
