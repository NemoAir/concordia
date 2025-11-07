# Concordia 改造方案

## 目标
- 为每个 Agent 绑定其专属远端 LLM（玩家本机/节点上的 Ollama/vLLM），不影响世界一致性。
- 维持 Concordia 组件化与日志/记忆机制；仅做“模型路由”与可选“超时降级”扩展。

## 变更清单（最小）
1) `concordia/language_model/ollama_model.py`
- 新增构造参数：`host: str | None = None`
- 初始化客户端：`self._client = ollama.Client(host=host) if host else ollama.Client()`
- 行为保持不变；默认兼容 `OLLAMA_HOST` 环境变量。

2) 新增 `concordia/prefabs/entity/remote_ollama.py`
- 描述：基于 `minimal__Entity` 组件布局，在 `build()` 内部忽略共享 `model`，改为使用实体参数创建专属 `OllamaLanguageModel`。
- 建议参数：
  - `name: str`
  - `llm_host: str`（示例：`http://10.0.0.7:11434`）
  - `model_name: str`（示例：`llama3.1:8b-instruct`）
  - `randomize_choices: bool = True`
  - 可选：`custom_instructions/goal/extra_components`

3) 可选：超时/降级封装
- 在 Orchestrator 侧为 `entity.act()` 调用加超时（线程池/asyncio）；逾时 fallback 策略：
  - 默认动作（空/等待/维持现状）
  - 兜底模型（服务端公共模型一次性代答）
  - 跳过该步

4) 记忆一致性（MVP 决策）
- 统一在 DGM/Orchestrator 侧维护记忆与嵌入（embedder）；远端 LLM 服务不持久化记忆，只返回行动文本/选择。
- 如需远端“反思/成长”，通过返回“记忆增量/情感结晶（Memento）”到 DGM 合并；避免分叉与嵌入漂移。

## 使用示例（装配）
```python
from concordia.prefabs.simulation import generic as simulation
from concordia.utils import helper_functions
import concordia.prefabs.entity as entity_prefabs
import concordia.prefabs.game_master as gm_prefabs
from concordia.typing import prefab as prefab_lib
import numpy as np

prefabs = {**helper_functions.get_package_classes(entity_prefabs),
           **helper_functions.get_package_classes(gm_prefabs)}
# 假设新增 remote_ollama 模块已暴露到 entity_prefabs 下

instances = [
  prefab_lib.InstanceConfig('remote_ollama__Entity', prefab_lib.Role.ENTITY,
                            {'name': 'Alice', 'llm_host': 'http://10.0.0.7:11434',
                             'model_name': 'llama3.1:8b-instruct'}),
  prefab_lib.InstanceConfig('generic__GameMaster', prefab_lib.Role.GAME_MASTER,
                            {'acting_order': 'game_master_choice'})
]

config = prefab_lib.Config(prefabs=prefabs, instances=instances,
                           default_premise='清晨，Alice 醒来。', default_max_steps=100)

sim = simulation.Simulation(config=config,
                            model=None,              # 将被实体 prefab 内部覆盖
                            embedder=lambda _: np.ones(3))
```

## 一致性说明
- 上下文由组件与记忆系统在服务端构造与保存，LLM 仅做“无状态”采样；不同 Agent 使用不同 LLM 不会破坏世界一致性。
- 记忆检索由统一 `embedder` 实现，独立于各 Agent 的 LLM。

## 测试与验证
- 单元：跑 `./bin/test.sh`；重点关注 `*_test.py`（components/engines/prefabs）。
- 集成：
  - 使用 `MockModel`/`NoLanguageModel` 跑最小流程（离线）。
  - 手动替换为远端 Ollama（设置 `llm_host`），验证生成一致。
- 性能：评估同时制 `simultaneous` 的并发表现与超时降级路径。
