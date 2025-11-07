# 聊天室（Matrix + Bot）对接方案（可选）

## 何时选择 Matrix
- 现成聊天室 UI（Element Web/桌面/移动端），房间/历史/权限即开即用；
- Bot/SDK 成熟（matrix-nio、matrix-bot-sdk），易与 Orchestrator 桥接；
- 可在房间内嵌 Widget 网页，便捷实现轻量“游戏化”可视化。

注意：CHIME 首期默认采用“Java 网关内建 WS 聊天”（见 ARCHITECTURE.md 结论）。Matrix 适用于对产品级聊天功能与 E2EE/联邦有强需求且可接受额外运维成本的场景。

## 部署
- Synapse（Matrix 服务器）：
  - 依赖 Postgres；暴露 `/_matrix/client/versions`；生产建议置于 HTTPS 反代之后。
  - 关闭公开注册；创建管理员与 Bot 账号。
- Element Web：静态站点；`config.json` 指向你的 homeserver。
- Nomad 作业：将 Synapse/Element 容器化部署；Consul 健康检查；可选 Connect mTLS。

## Bot 桥接职责
- 监听房间消息（玩家发言/命令）→ 调用 Orchestrator `POST /v1/rooms/{id}/external-event` 注入 GM；
- 订阅 Orchestrator WS（或回调）→ 将 `tick` 结果（观察/行动/总结/分数）发送到对应房间；
- 维护 `room_id ↔ simulation_id` 映射；重连/限速/幂等。

## 最小 Bot 示例（Python，matrix-nio）
```python
import asyncio, aiohttp
from nio import AsyncClient, AsyncClientConfig, RoomMessageText

MATRIX_HS = "https://matrix.example.com"
BOT_USER = "@gm-bot:example.com"
BOT_PASS = "****"
ORCH_URL = "https://orch.example.com"

client = AsyncClient(MATRIX_HS, BOT_USER, config=AsyncClientConfig(store_sync_tokens=True))
session = aiohttp.ClientSession()

async def on_message(room, event):
    if isinstance(event, RoomMessageText) and event.sender != BOT_USER:
        payload = {"room_id": room.room_id, "user_id": event.sender, "text": event.body}
        async with session.post(f"{ORCH_URL}/v1/rooms/{room.room_id}/external-event", json=payload, timeout=5):
            pass

async def send_tick(room_id, text):
    await client.room_send(room_id, message_type="m.room.message",
                           content={"msgtype": "m.text", "body": text})

async def main():
    await client.login(BOT_PASS)
    client.add_event_callback(on_message, RoomMessageText)
    # 订阅 Orchestrator 房间事件
    async with session.ws_connect(f"wss://orch.example.com/v1/rooms/events") as ws:
        async def tick_loop():
            async for msg in ws:  # 服务端需携带 room_id
                data = msg.json()
                await send_tick(data["room_id"], f"[Tick {data['tick_id']}]\n{data['summary']}")
        await asyncio.gather(client.sync_forever(30000), tick_loop())

asyncio.run(main())
```

> 生产化要点：持久化设备/同步令牌；错误重试与退避；必要时开启 E2EE 并妥善管理密钥。

## Widget（可选轻量游戏化）
- 在房间“添加 Widget”一个网页（`https://ui.example.com/widget?room_id=...`），显示：时间线、分数、角色卡、地图。
- 小网页直接调用 Orchestrator 只读接口（`GET /v1/rooms/{id}/state`）或使用 Matrix Widget API 互动。

## 与 Nomad 的关系
- 将 Synapse、Element、Bot 桥接均以 Nomad 作业运行；
- 不直接暴露 Orchestrator，对外统一从网关或 Element 入口；
- Consul 用作健康/服务发现；Connect 提供 mTLS（可选）。
