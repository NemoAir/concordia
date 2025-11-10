架构模块地图（初版）

> 本页按目录分组梳理核心模块、职责与关键类/函数，便于自顶向下理解。

## 1. typing（基础抽象）

- `typing/entity.py`
  - 核心：`Entity`（`name/act/observe`）、`ActionSpec`、`OutputType`。
  - 作用：统一“行动的规格”和“输出的类型”，GM 专属输出类型也在此定义。
- `typing/entity_component.py`
  - 核心：`EntityWithComponents`、`ContextComponent`、`ActingComponent`、`ContextProcessorComponent`、`Phase`。
  - 作用：定义组件化 Agent 的生命周期钩子与状态流转。

## 2. agents（组件化 Agent 实现）

- `agents/entity_agent.py`
  - `EntityAgent`：承载组件集合，串联 `pre_act → act → post_act → update` 与 `observe` 链路；并行调用组件（`_parallel_call_`）。
  - 关键点：
    - 每个 Agent 必须有一个 `ActingComponent`。
    - 可选 `ContextProcessorComponent` 用于汇总或副作用处理。

## 3. components（可插拔组件）

- `components/agent/*`
  - 示例：`plan.py`（规划）、`memory.py`（记忆）、`observation.py`（观察上下文）、`instructions.py`（系统/角色提示）等。
  - 设计：组件各自实现 `pre_act/post_act/pre_observe/post_observe/update`，在 `pre_act` 产生上下文，供 `ActingComponent` 决策。
- `components/game_master/*`
  - GM 侧分解：`make_observation / next_acting / next_game_master / event_resolution` 等组件化决策能力。

## 4. environment（引擎与回合制）

- `environment/engine.py`
  - `Engine` 抽象 & 工具：`action_spec_parser / action_spec_to_string`。
- `environment/engines/sequential.py`
  - `Sequential`：顺序（回合制）引擎；核心循环 `run_loop`：
    1) `terminate?` → 2) `next_game_master` → 3) 全体实体并行 `make_observation` → 4) `next_acting` + `next_action_spec` → 5) 实体 `act` → 6) GM `resolve` → loop
  - 日志：按阶段采集、压缩后附加到 `log`（易于分析/可视化）。
- 其他制式：`parallel_questionnaire.py / simultaneous.py` 等。

## 5. language_model（模型后端抽象）

- `language_model/language_model.py`
  - 接口：`sample_text(prompt, ...)` 与 `sample_choice(prompt, responses, ...)`。
  - 目的：屏蔽具体 API，不同后端（OpenAI/Azure/Vertex/Together/Mock）可替换。
- 具体实现：`base_gpt_model.py`、`azure_gpt_model.py`、`cloud_vertex_model.py`、`together_ai.py`、`testing/mock_model.py`。

## 6. associative_memory（联想记忆）

- `associative_memory/basic_associative_memory.py` 等
  - 通过嵌入向量做相似度检索；外部配置“句向量器”。
  - 典型使用：在 `pre_act` 汇总“相关记忆片段”给 LLM 决策。

## 7. prefabs（预制件）

- `prefabs/entity/*`：可直接使用的 Agent 组合（basic/basic_with_plan/conversational/scripted 等）。
- `prefabs/game_master/*`：可直接使用的 GM 组合（marketplace/dialogic/psychology_experiment/...）。
- `prefabs/simulation/*`：仿真脚手架（questionnaire_simulation/generic 等）。

## 8. document & thought_chains（提示组织与思维链）

- `document/interactive_document.py`：声明式构建提示、封装 open/yes_no/choice 等问法，保留“推理链”用于可观测性。
- `thought_chains/thought_chains.py`：通用“思维链”工具与模式。

## 9. clocks（时间与调度）

- `clocks/game_clock.py`：游戏内时间推进与时间标签，常用于 `ActionSpec` 的 `{timedelta}` 格式化。

## 10. utils / contrib / deprecated

- `utils/*`：并发、抽样、文本等通用工具。
- `contrib/*`：示范性的扩展组件与 GM 场景（含部分 deprecated 子目录）。
- `deprecated/*`：历史实现，仅供参考。

## 依赖与交互（速记）

- Agent ←(组件)→ LLM / Memory / Clock
- GM ←(组件)→ LLM（观测、行动选择、解析）
- Engine：组织 GM 与 Agents 的时序；串行/并行可替换
- Prefabs：面向任务的可复用组合
