# Orchestrator API（REST/WS）

## 概述
- 职责：承载 Concordia 世界；按 tick 推进；路由 Agent 行动到其 LLM 服务；广播房间事件。
- 技术栈：FastAPI + Uvicorn；结构化日志；容器化部署。

## 认证
- 推荐：由 Java Gateway 前置鉴权（JWT），Orchestrator 只接受来自网关的内部 mTLS 流量。

## 资源模型
- Room（世界）：`room_id` 对应一个 `Simulation` 实例（独立状态）。
- Agent 绑定：`agent_id -> llm_host`。

## REST
- POST `/v1/rooms`
  - 描述：创建世界（房间）。
  - 请求体：
    ```json
    {
      "engine": "sequential|simultaneous",
      "default_premise": "清晨，小镇苏醒。",
      "default_max_steps": 100,
      "prefabs": {"basic__Entity": {}, "generic__GameMaster": {}},
      "instances": [
        {"prefab":"remote_ollama__Entity","role":"entity",
         "params":{"name":"Alice","llm_host":"http://10.0.0.7:11434","model_name":"llama3.1:8b"}},
        {"prefab":"generic__GameMaster","role":"game_master",
         "params":{"acting_order":"game_master_choice"}}
      ],
      "embedder": "ones(3)"
    }
    ```
  - 响应：`{ "room_id": "...", "state_version": 1 }`

- POST `/v1/rooms/{room_id}/tick`
  - 描述：推进 1 步（锁步）。
  - 请求：`{ "deadline_ms": 3000 }`（可选）
  - 响应：`{ "tick_id": 12, "state_version": 13, "summary": "..." }`

- POST `/v1/rooms/{room_id}/external-event`
  - 描述：注入外部事件/玩家发言（写入 GM 观察）。
  - 请求：`{ "user_id":"@alice", "text":"在咖啡馆点单" }`
  - 响应：`{ "ok": true }`

- GET `/v1/rooms/{room_id}/state`
  - 描述：只读快照（最近状态、实体列表、分数、最近 N 条日志摘要）。

- GET `/health`

## WebSocket
- WS `/v1/rooms/{room_id}/events`
- 事件载荷（示例）：
  ```json
  {
    "type": "tick",
    "room_id": "...",
    "tick_id": 12,
    "state_version": 13,
    "observations": [{"entity":"Alice","text":"//08:00//走进咖啡馆"}],
    "summary": "Alice 与 Bob 对话...",
    "scores": {"Alice": 3, "Bob": 2},
    "warnings": []
  }
  ```

## 向玩家 LLM 发起调用（内部）
- HTTP/JSON（MVP 推荐）：
  - `POST http://<llm_host>/llm/text`
    - 请求：`{ "prompt": "...", "terminators": [], "temperature": 0.7, "top_p": 0.95, "seed": 42 }`
    - 响应：`{ "text": "..." }`
  - `POST http://<llm_host>/llm/choice`
    - 请求：`{ "prompt": "...", "choices": ["A","B","C"], "seed": 42 }`
    - 响应：`{ "index": 1, "text": "B", "meta": {} }`
- gRPC（可选演进）：与 HTTP/JSON 完全等价的语义；可在高并发/低延迟场景替换，不影响上层。

## 一致性与幂等
- 所有向 LLM 的请求包含：`tick_id`、`context_hash`；响应带回同值校验；过期/不符丢弃。
- `action_id` 防重；Orchestrator 内部去重。

## 超时与降级
- 默认 `deadline_ms`：2–5s（可配置，建议与世界节拍 5–10s 匹配）；
- 降级顺序：默认动作 → 兜底模型 → 跳过；事件中 `warnings` 体现。

## 启动与运行
- Dev：`uvicorn app:api --host 0.0.0.0 --port 8080 --reload`
- Docker：基础镜像 `python:3.12-slim`，安装 `.[dev]` 依赖；健康检查 `/health`。
