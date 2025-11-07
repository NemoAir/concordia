# 架构方案设计（总体）

## 目标与原则
- 目标：构建“权威服务端 + 分布式本地 LLM 大脑 + 聊天室呈现”的软实时多人仿真平台。
- 原则：服务端为单一事实来源；离散 tick 锁步推进；玩家本地 LLM 按需调用；掉线/超时可降级；可回放、可水平扩展。

## 角色与组件
- Orchestrator（Python/FastAPI，容器）：
  - 承载 Concordia `Simulation`；管理房间（世界）、tick 推进、日志与检查点；路由 Agent 行动到该玩家的 LLM 服务；提供 REST/WS。
- Java Gateway（Spring Boot/Quarkus）：
  - 鉴权、房间/用户管理、WS 广播；Consul 服务发现（`agent-<id>-llm`）；转发 Orchestrator API。
- 玩家 LLM 服务（Nomad 客户端）：
  - 本地 Ollama/vLLM + 轻量 HTTP API（`/llm/text`、`/llm/choice`）；注册 Consul；健康检查与限流。
- 客户端（Tauri）：
  - 聊天室 + 轻游戏化 UI；WebSocket 订阅网关；发送玩家输入。
- 聊天室（Matrix + Bot，可选）：
  - 现成聊天 UI（Element）+ Bot 桥接 Orchestrator，或直接采用网关 WS 实现聊天室。
- 基础设施：Nomad（调度）、Consul（发现/可选 mTLS 网格）、Traefik/NGINX（Ingress）、对象存储/DB（日志与检查点）。

## 数据流（每个 tick）
1) 观察：Orchestrator 为各实体生成观察（并发），写入实体记忆；可广播到客户端。
2) 行动：选择当步行动实体（`sequential`）或多实体（`simultaneous`）；对每个待行动 Agent 调用其 LLM 服务（HTTP，带 deadline）。
3) 解析：GM 解析合成事件；更新状态/记忆/日志；生成 `tick_id/state_version/summary`。
4) 广播：通过网关 WebSocket 推送给房间所有客户端；客户端渲染聊天与状态面板。

## 聊天室实现路径选择与结论（重要）
- 结论：首期采用“Java 网关内建 WebSocket 聊天”作为默认路径；Matrix 作为可选集成（见 MATRIX_INTEGRATION.md）。
- 原因：
  - 简单：无需额外部署 Synapse/Element/Bot 与 E2EE 管理，降低运维复杂度。
  - 可靠：鉴权/限流/熔断/幂等在网关统一实现；协议与 CHIME 事件模型完全贴合。
  - 可扩展：按房间做分区，配合 Redis/Kafka 做 Fanout 即可水平扩容。
  - UI 轻量：Tauri 复用现成聊天组件库（如 ChatUI、Mantine、Chakra 示例等），只做消息映射与少量状态面板。
- 何时选 Matrix：需要现成产品级聊天体验（多端、搜索、权限、E2EE、联邦）并接受额外运维时。

## 同步与一致性
- 锁步推进：服务端按固定/自适应节拍推进 1 步；并发收集行动；超时走降级（默认/兜底/跳过）。
- 消息契约：
  - 请求/响应均带 `tick_id`、`state_version`、`context_hash`（防过期/串扰）。
  - `action_id` 幂等去重。
- 可回放：`raw_log` 与检查点（`save_checkpoint`/`load_from_checkpoint`）。

## Concordia 映射
- 房间=一个 `Simulation` 实例；
- GM（世界规则）= 选择 GM prefab + 参数（如 `acting_order`、事件解析链等）；
- Agent（角色）= 选择实体 prefab + 参数（昵称、目标、个性），并为每个 Agent 绑定其 `llm_host`；
- 引擎= `sequential`（回合制）或 `simultaneous`（同时制）。

## 关键改造点（最小）
- `OllamaLanguageModel(host)`：支持每 Agent 指定不同主机（玩家本机 LLM 服务）。
- `remote_ollama__Entity` Prefab：在 `build()` 内用实体参数 `llm_host/model_name` 创建专属 LLM；其他组件沿用 `minimal__Entity` 布局。
- 可选 Deadline 封装：对 `entity.act()` 增加超时逻辑，逾时使用默认/兜底策略。

## 伸缩与容错
- 多房间=多 `Simulation`；按房间分片/多进程/多节点水平扩展。
- LLM 时延与稳定性：限制 tick 频率与每步并发；失败/超时降级；队列与背压。
- 掉线恢复：Consul 健康检查摘除离线 LLM 服务；客户端重连拉取快照/增量。

## 安全与运维
- 安全：mTLS（Consul Connect/Ingress）、JWT、CORS 白名单、限流、日志脱敏。
- 可观测：Prometheus 指标、Grafana 可视化、Loki 日志、OpenTelemetry Trace。
