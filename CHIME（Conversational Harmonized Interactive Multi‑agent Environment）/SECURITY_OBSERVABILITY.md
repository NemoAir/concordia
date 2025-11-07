# 安全与可观测性

## 安全基线
- 身份与鉴权：
  - 客户端登录 → 网关签发 JWT；WS/REST 均带 Authorization；
  - Orchestrator 仅接受来自网关的内部流量（mTLS/网络策略）。
- 传输安全：
  - 对外入口 TLS（Traefik/NGINX）；服务间可用 Consul Connect mTLS；
  - 限制 Agent-LLM 服务仅允许 Orchestrator/网关访问（意图/ACL）。
- 速率与配额：
  - 网关限流（IP/账号/房间），LLM 服务并发/队列上限；
  - 超时与熔断，防止级联故障。
- 数据与隐私：
  - 日志脱敏（用户/密钥/个人信息），按需采样；
  - 对象存储的 `raw_log` 与检查点加密保存；
  - Matrix 生产环境建议启用 E2EE 并妥善管理 Bot 密钥。

## 可观测性
- 指标（Prometheus）：
  - Orchestrator：`tick_duration_ms`, `tick_timeout_total`, `tick_broadcast_delay_ms`；
  - LLM：`llm_requests_total`, `llm_latency_ms{agent=model}`, `llm_timeout_total`；
  - 网关：`ws_connections`, `msg_in_flight`；
- 日志（Loki/ELK）：
  - 统一 JSON，字段包含 `room_id/tick_id/agent_id/state_version/trace_id`；
  - 关键路径异常打标，便于检索与告警。
- Trace（OpenTelemetry）：
  - 前后端贯穿 traceId；
  - 采样策略按 QPS 与成本控制。

## 灰度与回滚
- 蓝绿/滚动发布；健康检查门禁；
- 镜像 tag 与配置分版本；失败自动回滚；
- 检查点可用于回放与恢复。

