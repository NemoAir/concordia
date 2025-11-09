Concordia 架构与技术文档（工作区）

> 本目录用于系统化沉淀 Concordia 的架构与技术文档，并与两篇论文对齐：
> - `Concordia-2312.03664v2-google.md`
> - `Concordia-2507.08892v1-google.md`
>
> 状态：进行中（rolling docs）。本页置顶 TODO 列表用于驱动学习与文档完善。

## 置顶 TODO（优先级从上到下）

- [ ] 高层架构速读与术语统一（Entity / Component / Engine / Game Master / LanguageModel / ActionSpec）
- [ ] 跑通一个最小示例（examples/）并记录最短路径与依赖配置
- [ ] 阅读与标注关键代码：
  - [ ] `concordia/agents/entity_agent.py` 与 `typing/entity_component.py`
  - [ ] `typing/entity.py`（`ActionSpec` / `OutputType`）与 `environment/engine.py`
  - [ ] `environment/engines/sequential.py`（主循环与日志）
  - [ ] 语言模型抽象：`language_model/language_model.py` 及具体实现
  - [ ] 组件体系：`components/agent/*`（plan/memory/observation/...）
  - [ ] 预制件：`prefabs/game_master/*` 与 `prefabs/entity/*`
  - [ ] 记忆与嵌入：`associative_memory/basic_associative_memory.py`
  - [ ] 时钟与时间：`clocks/game_clock.py`
  - [ ] 交互式文档与思维链：`document/*`、`thought_chains/*`
  - [ ] 可观测性：`*WithLogging` 与 engine 日志结构
- [ ] 与论文 2312.03664 对齐：概念-代码映射表与关键差异说明
- [ ] 与论文 2507.08892 对齐：新增能力/改动点与实现落点
- [ ] 写出模块地图（见 `MODULES.md` 初版）并补齐交叉依赖说明
- [ ] 写出运行时流程与数据流（见 `FLOW.md` 初版）并补充时序图
- [ ] 给出“如何扩展”的实践指南：新增自定义 Act 组件与自定义 Engine
- [ ] 质量保障与最小测试套：如何运行核心单测与常见失败排查
- [ ] 最佳实践：模型选择、温度/采样、Memory 配置、性能与成本权衡
- [ ] 用例索引：把 examples 场景与核心概念一一对照

## 当前问题与插件化方案（WIP）

1. **max token 统一治理**：新增 `plugins/token_budgeting.py` 与集中配置 `plugins/token_budget_config.json`（详见 `plugins/README.md`）。通过 `MaxTokenGuardLanguageModel` 包裹任何现有 `LanguageModel`，即可：
   - 从 JSON 读取各组件的 `max_tokens`，对照 `concordia/components/agent/concat_act_component.py`、`concordia/document/interactive_document.py` 等硬编码数值做统一裁剪；
   - 记录调用栈与最终预算，定位是哪一个组件触发 API 报错；
   - 在溢出时抛出 `TokenBudgetError`，配合日志即可快速追溯；下一步会把日志输出格式纳入 `FLOW.md`。
2. **世界语言自动流转**：`plugins/language_policy.py`（详见 `plugins/README.md`）自带
   `LanguagePolicyStore`、`LanguageRoutingModel` 与 `LanguageAwareEntityAgent`：
   - 通过 `shared_memories` 侦测世界设定语言（当前实现先区分中/英，可按需扩展）；
   - 用 contextvars 维护“当前行动的实体”，在不改动核心类的前提下，把语言偏好传给模型包装器；
   - 所有角色默认继承世界语言，若 Prefab 参数指定其它语言，可调用 `override_for_entity` 保留角色特性。
3. **执行节奏**：
   - 将 tutorial 场景切换到新的 model wrapper + agent，以便记录真实的 token 消耗与语言切换行为；
   - 依据日志反推 `token_budget_config.json` 的上限，并补充「超限后的重试/降级策略」；
   - 在 `MODULES.md` / `FLOW.md` 中描述数据流的语言/Token 控制点，方便推演未来的不可控场景。

## 文档导航

- 架构模块地图：`MODULES.md`
- 运行时流程（引擎/回合/观察-行动）：`FLOW.md`
- 论文（随附原文转存）：
  - `Concordia-2312.03664v2-google.md`
  - `Concordia-2507.08892v1-google.md`

## 高层架构速览

- Entity 抽象（`typing/entity.py`）
  - `Entity.name / act / observe`；`ActionSpec` 描述行动类型与约束；`OutputType` 定义输出种类（FREE/CHOICE/FLOAT 以及 GM 专用类型）。
- 组件化 Agent（`agents/entity_agent.py` + `typing/entity_component.py`）
  - `EntityWithComponents` + 多个 `ContextComponent`（pre_act / post_act / pre_observe / post_observe / update 钩子）
  - 一个 `ActingComponent` 负责最终行动；可选 `ContextProcessorComponent` 汇总/加工上下文。
- 游戏主持人（Game Master, GM）与引擎（`environment/engine.py` / `engines/sequential.py`）
  - 引擎驱动回合：生成观察 → 选择下一个行动者与 `ActionSpec` → 实体行动 → GM 解析与“落地”事件 → 终止判定。
- 语言模型抽象（`language_model/language_model.py`）
  - 统一 `sample_text / sample_choice` 接口，便于替换后端（OpenAI/Azure/Vertex/TogetherAI/Mock）。
- 记忆与嵌入（`associative_memory/*`）
  - 使用句向量检索相关记忆；可替换嵌入器（需要“固定维度”嵌入）。
- 交互式提示与思维链（`document/*`, `thought_chains/*`）
  - `InteractiveDocument` 组织多轮问答与 yes/no/open 问句；部分组件在日志中保留“推理痕迹”。

## 与论文对齐（初版）

- 2312.03664（Tech Report）
  - Agent 的“情景-身份-规则”三问设计（README 亦有概述）在 `components/agent/*` 的 plan/observation/memory 等实现中落地。
  - GM 作为环境代理的抽象在 `environment/*` 与 `prefabs/game_master/*` 中实现，可把自然语言行动“翻译”为环境影响。
- 2507.08892（新版/扩展）
  - 更强调可插拔组件与可观测性，代码中 `*WithLogging` 与 `engine` 的分段日志结构反映这一点。
  - 并行/同时制式的引擎扩展见 `engines/parallel_* / simultaneous.py`。

后续我们会把论文关键概念与具体文件/类做成一一映射表并补充差异细节。

## 学习路径建议（实践导向）

1) 10 分钟跑通：
- 选一个 LLM 提供方并配置凭据；先用 `concordia/testing/mock_model.py` 做无网验证。
- 跑 `examples/` 中最小场景（或改写成脚本）并观察日志与数据流。

2) 60 分钟代码走查：
- 顺序阅读：`typing/entity.py` → `typing/entity_component.py` → `agents/entity_agent.py` → `environment/engine.py` → `engines/sequential.py`。
- 快速过一遍 `components/agent/*` 与 `prefabs/game_master/*` 的角色划分。

3) 120 分钟动手扩展：
- 新增一个简单 `ActingComponent`（基于 `LanguageModel.sample_text`）
- 按需替换/注入 `ContextComponent`（例如加入记忆或计划）
- 写一个极简 GM（或复用 prefab）跑通一轮 `run_loop`。

完成以上后，回到置顶 TODO 勾选并在 `MODULES.md` / `FLOW.md` 中补充细节与截图/时序图。

## 质量与测试（入口）

- 运行核心测试：`pytest --pyargs concordia`（需要已安装依赖）
- 单测索引（可从以下开始）：
  - `concordia/concordia_integration_test.py`
  - `concordia/environment/engines/*_test.py`
  - `concordia/components/agent/agent_components_test.py`

## 常见扩展点

- 新语言模型后端：实现 `language_model.LanguageModel` 接口。
- 新 Agent 组件：继承 `ContextComponent` 或 `ActingComponent`。
- 新引擎：继承 `environment.engine.Engine`，实现 `run_loop` 等方法。
- 新 GM：参考 `prefabs/game_master/*`，把自然语言行动映射为事件与观察。

---
本页为“任务驱动”的索引页；详见 `MODULES.md` 与 `FLOW.md` 的细化解释与代码引用。
