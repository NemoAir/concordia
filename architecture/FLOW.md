运行时流程与数据流（初版）

> 本页描述 Sequential 引擎为例的观察-行动-解析循环、关键对象交互与日志要点。

## 1. 关键对象

- Engine：`environment/engines/sequential.py::Sequential`
- Game Master（GM）：`prefabs/game_master/*`（或自定义），本质也是 `Entity`
- Agent（组件化）：`agents/entity_agent.py::EntityAgent`
- LanguageModel：`language_model/*`（抽象 + 具体实现）
- ActionSpec：`typing/entity.py::ActionSpec`（规定实体输出格式/约束）

## 2. 主循环（Sequential::run_loop）

循环变量：`steps < max_steps` 且 `not terminate()`

1) 终止判定（GM 决策）
   - `Engine.terminate(game_master)` → `ActionSpec(OutputType.TERMINATE, options=Yes/No)`
   - LLM 选择 Yes/No → 返回布尔值

2) 选择下一个 Game Master（可选，多 GM 场景）
   - `Engine.next_game_master(game_master, game_masters)`
   - 当仅有一个 GM 时直接复用

3) 并行生成观察并分发给每个 Entity
   - 对每个 `entity`：`Engine.make_observation(game_master, entity)`
   - `ActionSpec(OutputType.MAKE_OBSERVATION)` → GM 基于上下文生成该实体应观察到的文本
   - 若非空白则 `entity.observe(observation)`

4) 选择下一个行动实体与其 ActionSpec
   - `Engine.next_acting(game_master, entities)`：
     - `ActionSpec(OutputType.NEXT_ACTING, options=实体名)` 选人
     - `ActionSpec(OutputType.NEXT_ACTION_SPEC)` 产出“下一步要求的行动规格”（FREE/CHOICE/FLOAT/或 SKIP_THIS_STEP）
   - `engine.action_spec_parser(...)` 将字符串解析为 `ActionSpec`

5) 实体行动
   - 若 `ActionSpec.SKIP_THIS_STEP`：跳过本回合行动
   - 否则：`next_entity.act(action_spec)`
     - 组件生命周期：
       - `PRE_ACT`：并行收集各 `ContextComponent.pre_act(action_spec)` 产出上下文
       - `ActingComponent.get_action_attempt(contexts, action_spec)` 决策行动
       - `POST_ACT`：通知各组件 `post_act(action)`
       - `UPDATE`：组件更新内部状态

6) GM 解析事件（环境落地）
   - `Engine.resolve(game_master, putative_event)`
   - GM 将“候选事件”解析为最终事件，并通过 `observe(EVENT_TAG ...)` 回灌自身，用于后续上下文

7) 日志与检查点
   - `Sequential._log(...)` 聚合每个阶段的组件日志（过滤只保留有信息的项）
   - 可调用 `checkpoint_callback(step)` 实现持久化/可视化/中断恢复

## 3. 数据流要点

- `ActionSpec` 串起 GM 与 Agent 的约束契约（FREE/CHOICE/FLOAT/GM 专有类型）。
- `EntityAgent` 的 `ContextComponent` 产出“可解释上下文”，`ActingComponent` 消费上下文并调用 LLM 决策。
- `InteractiveDocument` 常用于组织提示词并保留思维链；组件通过 `*WithLogging` 输出可观测信息。
- 记忆子系统在 `pre_act` 检索相似片段，作为上下文拼接到提示词中。

## 4. 扩展场景

- 同步改并行：替换引擎为 `engines/parallel_*` 或 `simultaneous.py`。
- 外接新工具：在 GM `resolve` 阶段调用外部 API，将自然语言行动映射为实际副作用。
- 约束更强的行动：自定义 `ActionSpec` 的 call_to_action 与 `CHOICE` 选项，或用 `FLOAT` 量化选择。

