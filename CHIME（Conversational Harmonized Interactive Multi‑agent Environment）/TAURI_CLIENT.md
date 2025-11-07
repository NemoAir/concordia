# 客户端（Tauri）实现要点

## 形态（与聊天室结论同步）
- 首选 Java 网关内建 WS 聊天；Tauri 前端复用成熟聊天组件库，做最小 UI 壳。
- 聊天室为主的 UI（消息时间线、角色/分数面板、输入框），支持轻游戏化表现（打字机、进度条、头像/地图）。
- 与 Java Gateway 建立 WebSocket；接收每步事件；发送玩家消息/命令到网关（转发到 Orchestrator）。

## WebSocket 订阅
- 连接：`wss://gateway/ws/rooms/{roomId}`（携带 JWT）。
- 消息：`{type: 'tick'|'observation'|'summary'|'score'|..., tick_id, state_version, ...}`。
- 自动重连：指数退避；按 `state_version` 校验并拉取 `/state` 对齐。

## 发送消息
- `POST https://gateway/rooms/{roomId}/message`；body 为玩家文本/选择等；
- 网关将消息转为 Orchestrator 的 `external-event` 注入 GM。

## UI 分层
- Data 层：WS 客户端、HTTP 客户端（拉快照/历史）；
- Store：本地状态（房间、实体、分数、最近 N 条消息）；
- View：聊天时间线组件（可用 ChatUI/react-chat-elements 等组件库）、角色/分数面板、输入组件、加载/错误组件；
- 本地缓存：SQLite（断网重连）；
- 动画：打字机/过场/进度条填补 LLM 延迟（2–5s）。

## 代码骨架（示意）
```ts
// src/ws.ts
export function connectWS(url: string, onMsg: (data:any)=>void) {
  let ws = new WebSocket(url);
  ws.onmessage = (e) => onMsg(JSON.parse(e.data));
  ws.onclose = () => setTimeout(() => connectWS(url, onMsg), 1000);
  return ws;
}
```

```ts
// src/main.tsx
import { connectWS } from './ws';
const roomId = '...';
connectWS(`${WS_URL}/ws/rooms/${roomId}`, (msg) => {
  // 渲染：append timeline / update score / state_version 校验
});
```

## 安全
- 登录后由网关签发 JWT；WS/HTTP 均带 Authorization；
- CORS 白名单；防止跨站注入（渲染端过滤/转义）。

## 与 Matrix 的关系（可选）
- 若采用 Matrix+Element，则 Tauri 仅嵌入 Element 网页（或嵌 Widget 网页），前述 WS/REST 逻辑由 Bot 与 Orchestrator 完成；MVP 不推荐，作为后续可选。
