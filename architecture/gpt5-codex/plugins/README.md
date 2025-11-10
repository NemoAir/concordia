# Concordia Plugins（实验区）

> 本目录中的插件不修改 Concordia 核心源码，侧重通过“组合”方式解决
> max token 管理与多语言管道的问题。下面列出每个新增类的职责与典型用法。

## Token Budgeting（`plugins/token_budgeting.py`）

- **`TokenBudgetRule`**：描述一个规则（名称、匹配的调用栈子串、限定的 `max_tokens`）。配置文件 `plugins/token_budget_config.json`
  里的每一项都会被解析成该类实例，便于后续序列化与调试。
- **`TokenBudgetRegistry`**：加载全部规则并对每次 LLM 请求计算最终预算。它负责：
  1. 读取 JSON（`from_json`）并构造规则列表；
  2. `resolve(...)` 时根据调用栈（来自 `_infer_callsite`）匹配规则，同时保证不超过 `global_context_window - safety_margin`；
  3. `describe()` 返回快照，方便记录到日志或文档。
- **`MaxTokenGuardLanguageModel`**：包装任意 `language_model.LanguageModel`。所有 `sample_text` 调用都会：
  1. 推断调用栈 → 交给 `TokenBudgetRegistry` 计算预算；
  2. 输出 debug 日志，包含请求上下文与最终 `max_tokens`；
  3. 如果底层模型因为超限报错，抛出 `TokenBudgetError` 并把上下文写入日志。
  `sample_choice` 直接透传，因其不包含 `max_tokens`。
- **`TokenBudgetError`**：统一的异常类型，用于在 notebook 或自定义 Runner 中捕获“预算被砍掉之后仍然失败”的场景，驱动重试/降级。

**使用示例**

```python
from plugins import token_budgeting
from concordia.language_model import utils as lm_utils

base_model = lm_utils.language_model_setup(...)
registry = token_budgeting.TokenBudgetRegistry.from_json(
    'plugins/token_budget_config.json')
model = token_budgeting.MaxTokenGuardLanguageModel(base_model, registry)
```

## Language Policy（`plugins/language_policy.py`）

- **`LanguagePolicy`**：保存“世界语言 + 兜底语言”的简单数据类，便于序列化或测试替换。
- **`LanguagePolicyStore`**：负责语言检测与上下文管理。
  - `update_world_language(shared_memories)`：合并 shared memories 后调用 `detect_language`（目前区分中/英，可扩展）。
  - `override_for_entity(name, code)`：允许角色自行声明输出语言。
  - `activate_entity(name)`：context manager，基于 `contextvars` 记住当前活跃实体，供模型包装器查语言。
- **`LanguageRoutingModel`**：包装任意 `LanguageModel`。每次调用 `sample_text / sample_choice` 时自动在 prompt 末尾追加
  “Please respond in {language}” 风格的指令（模板可自定义），确保所有组件遵循世界语言或角色 override。
- **`LanguageAwareEntityAgent`**：继承自 `EntityAgentWithLogging`。在 `act / observe` 入口把实体名称写入 `LanguagePolicyStore`
  的 contextvar，这样同一个模型实例即可知道“当前是谁在说话”，无需改动 Concordia 核心 Agent。

**使用示例**

```python
from plugins import language_policy
from concordia.prefabs import entity as entity_prefabs

policy_store = language_policy.LanguagePolicyStore()
policy_store.update_world_language(shared_memories)

base_model = ...
model = language_policy.LanguageRoutingModel(base_model, policy_store)

agent = language_policy.LanguageAwareEntityAgent(
    agent_name='项羽',
    act_component=...,
    context_components=...,
    language_policy_store=policy_store,
)
```

这些组件可与 `token_budgeting` 联合使用：先包一层语言策略，再包一层 token guard（或反之），即可在 notebook
或自定义 Runner 中同时满足“语言一致性 + max token 可观测”的需求。
