# Concordia Token 配置统一文档

**版本**: 1.0.0  
**最后更新**: 2025-11-08 Session 1  
**维护状态**: 🟡 审计进行中

---

## 📖 文档说明

本文档集中记录 Concordia 框架中所有与 token 限制相关的配置参数。

### 目的
1. **集中管理**：一处查看所有 token 配置
2. **避免冲突**：识别不一致的配置
3. **易于调优**：快速定位需要调整的参数
4. **跨 Session 连续性**：完整记录便于长期维护

### 使用场景
- 🔧 **性能调优**：遇到截断问题时查找相关参数
- 📊 **系统分析**：了解各组件的 token 预算
- 🚀 **新功能开发**：添加新组件时参考现有配置
- 🐛 **问题排查**：定位 MAX_TOKENS 错误来源

---

## 🎯 配置层级

Concordia 的 token 配置分为 4 个层级：

```
Level 1: 全局默认值 (Global Defaults)
   ↓
Level 2: 模块级配置 (Module Configs)
   ↓
Level 3: 组件级配置 (Component Configs)
   ↓
Level 4: 函数调用配置 (Call-site Configs)
```

**优先级**：Level 4 > Level 3 > Level 2 > Level 1

---

## 📊 Level 1: 全局默认值

这些是框架最底层的默认配置，影响所有未显式指定的调用。

### 1.1 Document 层默认值

**文件**: `concordia/document/interactive_document.py`

```python
# Line 27-28
DEFAULT_MAX_CHARACTERS = 16384  
DEFAULT_MAX_TOKENS = 4096  # = DEFAULT_MAX_CHARACTERS // 4
```

| 参数 | 值 | 说明 | 影响范围 |
|------|-----|------|---------|
| `DEFAULT_MAX_CHARACTERS` | 16384 | 最大字符数 | 所有 InteractiveDocument 实例 |
| `DEFAULT_MAX_TOKENS` | 4096 | 最大 token 数 | 所有 `open_question()` 调用 |

**用途**:
- `InteractiveDocument.open_question()` 的默认 `max_tokens`
- 所有基于文档的交互式对话生成

**修改历史**:
- 初始值: `4000 chars / 1000 tokens`
- 2025-11-08: 增加到 `16384 chars / 4096 tokens` (commit: 604a3fd)
- **原因**: 解决多语言（中文）内容截断问题

**影响分析**:
- ✅ 减少 MAX_TOKENS 错误
- ✅ 支持更长的推理链
- ⚠️ 增加 API 成本
- ⚠️ 增加响应延迟

**建议**:
- 保持当前值 4096 用于一般场景
- 特殊组件（如长对话）可以显式指定更大值
- 简单查询可以显式指定更小值（如 500-1000）

---

### 1.2 Language Model 层默认值

**文件**: `concordia/language_model/language_model.py`

> **待审计** - 需要完整阅读此文件

**已知的**:
```python
DEFAULT_TEMPERATURE = 1.0
DEFAULT_TOP_P = 1.0
DEFAULT_TOP_K = 40
# DEFAULT_MAX_TOKENS 值待确认
```

**需要确认**:
- [ ] 是否有模型级别的 `DEFAULT_MAX_TOKENS`？
- [ ] 不同模型类型的默认值差异？
- [ ] Safety settings 对 token 的影响？

---

## 📊 Level 2: 模块级配置

### 2.1 Thought Chains 模块

**文件**: `concordia/thought_chains/thought_chains.py`

> **待系统审计** - 目前已知的部分配置

**已知的 max_tokens 配置**:

| 函数/方法 | 行号 | max_tokens | 用途 |
|-----------|------|-----------|------|
| (直接引用) | 74 | 2500 | 提取角色引述 |
| `result_to_who_what_where` | 140 | 3000 | 事件因果分析 |
| `result_to_who_what_where` | 151 | 3000 | 因果陈述重写 |
| `attempt_to_result` | 176 | 3000 | 尝试行动结果 |
| `result_to_who_what_where` | 200 | 3000 | 位置查询 |
| `result_to_who_what_where` | 205 | 3000 | 行动意图查询 |
| `result_to_who_what_where` | 214 | 3000 | 结果描述 |
| `result_to_who_what_where` | 219 | 3000 | 最可能结果 |
| `result_to_who_what_where` | 249 | 3000 | 事件重写 |
| (其他) | 282, 316, 356, 436, 510, 633, 678, 692, 716, 767 | 2200-3500 | 各种推理任务 |

**观察**:
- 大部分使用 3000 tokens
- 有一个 2200，一个 2500，一个 3500
- **不一致性**: 需要评估是否应该统一

**待审计**:
- [ ] 完整阅读文件，确认所有 token 配置
- [ ] 分析每个值的合理性
- [ ] 建议统一或差异化配置

---

## 📊 Level 3: 组件级配置

### 3.1 Agent 组件

#### 3.1.1 QuestionOfRecentMemories

**文件**: `concordia/components/agent/question_of_recent_memories.py`

```python
# Line ~390 (具体行号待确认)
max_tokens=4096  # 原值: 1000
```

**用途**: Agent 查询最近记忆时的 token 限制

**修改历史**:
- 初始值: 1000
- 2025-11-08: 增加到 4096 (commit: d055504)

**依赖**:
- 依赖 `InteractiveDocument.open_question()`
- 间接受 `DEFAULT_MAX_TOKENS` 影响

---

#### 3.1.2 ConcatActComponent

**文件**: `concordia/components/agent/concat_act_component.py`

```python
# Line ~170 (具体行号待确认)
max_tokens=4096  # 原值: 2200
```

**用途**: Agent 拼接多个行动组件输出

**修改历史**:
- 初始值: 2200
- 2025-11-08: 增加到 4096 (commit: d055504)

---

### 3.2 Game Master 组件

#### 3.2.1 SwitchAct

**文件**: `concordia/components/game_master/switch_act.py`

```python
# Line ~340 (具体行号待确认)
max_tokens=4096  # 原值: 1000
```

**用途**: GM 决定是否切换当前行动者

**修改历史**:
- 初始值: 1000
- 2025-11-08: 增加到 4096 (commit: d055504)

---

#### 3.2.2 NextActing

**文件**: `concordia/components/game_master/next_acting.py`

```python
# Line ~650 (具体行号待确认)
max_tokens=4096  # 原值: 1024
```

**用途**: GM 选择下一个行动的角色

**修改历史**:
- 初始值: 1024
- 2025-11-08: 增加到 4096 (commit: d055504)

---

#### 3.2.3 MakeObservation

**文件**: `concordia/components/game_master/make_observation.py`

```python
# Line 173
max_tokens=3000
```

**用途**: 生成角色观察描述

**状态**: 未修改（使用显式 3000）

**待评估**: 是否需要增加？

---

#### 3.2.4 FormativeMemoriesInitializer

**文件**: `concordia/components/game_master/formative_memories_initializer.py`

> **待系统审计** - 此文件包含多个 token 配置

**已知配置**:
- 语言检测元提示: `max_tokens=500`
- 其他生成任务: 待确认

**特殊性**: 此组件实现了语言自适应架构

---

## 📊 Level 4: 函数调用配置

这一层级是代码中直接调用时传递的 `max_tokens` 参数。

> **大量待审计** - 需要系统性地读取所有文件

**示例** (examples/tutorial_chinese.ipynb):
```python
# Cell 7: 测试语言模型
response = model.sample_text(
    prompt="...",
    max_tokens=500,  # 显式指定
    terminators=('\n',)
)
```

---

## 🔍 待审计的关键文件

### 优先级 1 (核心模块)

- [ ] `concordia/language_model/language_model.py`
- [ ] `concordia/language_model/google_aistudio_model.py`
- [ ] `concordia/language_model/cloud_vertex_model.py`
- [ ] `concordia/language_model/utils.py`
- [ ] `concordia/document/interactive_document.py` ✅
- [ ] `concordia/thought_chains/thought_chains.py` (部分已知)

### 优先级 2 (组件)

**Agent 组件** (~20 个文件):
- [ ] `concordia/components/agent/question_of_recent_memories.py` ✅
- [ ] `concordia/components/agent/concat_act_component.py` ✅
- [ ] `concordia/components/agent/*.py` (其他)

**Game Master 组件** (~30 个文件):
- [ ] `concordia/components/game_master/formative_memories_initializer.py` (部分已知)
- [ ] `concordia/components/game_master/make_observation.py` (部分已知)
- [ ] `concordia/components/game_master/switch_act.py` ✅
- [ ] `concordia/components/game_master/next_acting.py` ✅
- [ ] `concordia/components/game_master/*.py` (其他)

### 优先级 3 (其他模块)

- [ ] `concordia/agents/*.py`
- [ ] `concordia/environment/*.py`
- [ ] `concordia/associative_memory/*.py`
- [ ] `concordia/prefabs/*.py`

---

## 📈 统计分析

### 当前状态 (Session 1)

| 指标 | 数值 | 说明 |
|------|------|------|
| 已审计文件 | 6 | 部分完成，非系统审计 |
| 发现参数 | ~25 | 估计值 |
| 已统一配置 | 0 | 尚未开始重构 |
| 待审计文件 | ~100+ | 完整审计待开始 |

### Token 值分布 (已知)

```
500   █ (1个)  语言检测
1000  ███ (3个) 旧默认值
2200  █ (1个)  对话生成
2500  █ (1个)  引述提取
3000  ████████ (10+个) 推理链标准值
3500  █ (1个)  复杂推理
4096  █████ (6个) 新增高限制
```

**观察**:
- 大部分使用 3000 或 4096
- 存在一些异常值（500, 2200, 2500, 3500）
- 需要评估是否应该标准化

---

## 🎯 重构建议

### 阶段 1: 创建配置类

```python
# concordia/config/token_config.py (建议)

class TokenLimits:
    """统一的 Token 限制配置"""
    
    # 全局默认值
    DEFAULT = 4096
    
    # 语义层级
    SHORT_RESPONSE = 500      # 简短回答（如名字、日期）
    MEDIUM_RESPONSE = 1000    # 中等回答（如简短描述）
    LONG_RESPONSE = 2000      # 长回答（如完整事件）
    VERY_LONG_RESPONSE = 4096 # 超长回答（如复杂推理）
    
    # 功能分类
    LANGUAGE_DETECTION = 500
    SIMPLE_QUERY = 1000
    MEMORY_QUERY = 2000
    EVENT_RESOLUTION = 3000
    COMPLEX_REASONING = 4096
    BACKSTORY_GENERATION = 4096
```

### 阶段 2: 逐步替换

1. 替换所有硬编码值为配置类引用
2. 保持向后兼容
3. 添加弃用警告

### 阶段 3: 文档和测试

1. 更新所有文档
2. 添加配置测试
3. 提供迁移指南

---

## 🚨 注意事项

### 修改风险

1. **API 成本**: 增加 max_tokens 会增加 API 调用成本
2. **延迟**: 更大的 token 限制可能增加响应时间
3. **兼容性**: 某些模型可能有更低的限制
4. **质量**: 并非所有场景都需要长回答

### 最佳实践

1. **最小必要原则**: 使用满足需求的最小值
2. **显式优于隐式**: 重要场景显式指定 max_tokens
3. **分层配置**: 全局默认 + 组件覆盖 + 调用覆盖
4. **充分测试**: 修改后测试各种场景

---

## 📝 审计日志

| 日期 | Session | 审计内容 | 发现数 | 提交 |
|------|---------|---------|--------|------|
| 2025-11-08 | 1 | 创建追踪系统 | 6 | - |
| - | - | 待继续... | - | - |

---

## 🔄 下一步

1. ✅ 创建本文档
2. ⏳ 生成完整文件清单
3. ⏳ 开始系统审计 `language_model/`
4. ⏳ 完成所有核心模块审计
5. ⏳ 设计配置类
6. ⏳ 实施重构

---

*本文档将随审计进度持续更新*
*每发现新参数立即添加到对应章节*


---

## 🔍 Phase 1 审计结果

### Phase 1, Stage 1.1: Language Model 核心 ✅

**审计时间**: 2025-11-08 Session 1
**文件数量**: 19 个文件
**发现参数**: 20+

#### 关键发现总结

1. **全局默认值** (`language_model.py` Line 27)
   ```python
   DEFAULT_MAX_TOKENS = 5000
   ```
   - 这是所有语言模型的基础默认值
   - 优先级：语言模型层 > 文档层 (4096)

2. **模型特定的硬编码值**

   | 模型 | 场景 | max_tokens | 文件 | 行号 |
   |------|------|-----------|------|------|
   | Google AI Studio | sample_choice | 8192 | `google_aistudio_model.py` | 303 |
   | Cloud Vertex | sample_choice | 2048 | `cloud_vertex_model.py` | 172 |
   | Mistral (completion) | sample_choice | 256 | `mistral_model.py` | 263 |
   | Mistral (chat) | sample_choice | 3 | `mistral_model.py` | 271 |
   | VLLM | logprobs only | 1 | `vllm_model.py` | 211 |
   | Together AI | sample_choice | 1 | `together_ai.py` | 294 |

3. **模型特定的限制常量**

   ```python
   # together_ai.py Line 53
   _DEFAULT_NUM_RESPONSE_TOKENS = 5000
   # 用于cap max_tokens: min(max_tokens, 5000)
   
   # google_cloud_custom_model.py Line 33
   _DEFAULT_MAX_TOKENS = 5000
   # 用于cap max_tokens: min(max_tokens, 5000)
   
   # amazon_bedrock_model.py Line 28-32
   MODEL_MAX_OUTPUT_TOKENS_LIMITS = {
       'ai21.jamba-instruct-v1:0': 4096,
       'ai21.jamba-1.5-mini-v1:0': 4096,
       'ai21.jamba-1.5-large-v1:0': 4096,
       'meta.llama3-1-405b-instruct-v1:0': 4096,
       'us.meta.llama3-2-90b-instruct-v1:0': 4096,
   }
   # 不同模型有不同的硬限制
   ```

#### ⚠️ 发现的不一致性

1. **sample_choice 的 token 限制极不一致**
   - Google AI Studio: 8192
   - Cloud Vertex: 2048
   - Mistral completion: 256
   - Mistral chat: 3
   - Together AI: 1
   - VLLM: 1
   
   **原因**: 不同的实现策略
   - 有的生成完整回答再提取
   - 有的只生成选项字母
   - 有的使用 logprobs 不生成文本

2. **语言模型层 vs 文档层的默认值**
   - `language_model.DEFAULT_MAX_TOKENS` = **5000**
   - `interactive_document.DEFAULT_MAX_TOKENS` = **4096** (刚修改)
   
   **影响**: 
   - 直接调用 `model.sample_text()` 默认 5000
   - 通过 `InteractiveDocument.open_question()` 默认 4096
   - 可能导致混淆

#### 📊 完整文件列表

| 文件 | Token 配置 | 说明 |
|------|-----------|------|
| `__init__.py` | 无 | 空文件 |
| `language_model.py` | DEFAULT_MAX_TOKENS = 5000 | ⭐ 基础接口 |
| `google_aistudio_model.py` | 5000 (默认), 8192 (choice) | ⭐ Gemini API |
| `cloud_vertex_model.py` | 5000 (默认), 2048 (choice) | Google Cloud |
| `mistral_model.py` | 5000 (默认), 256/3 (choice) | Mistral API |
| `together_ai.py` | 5000 (默认, capped) | Together AI |
| `amazon_bedrock_model.py` | 5000 (默认), 模型特定上限 | AWS Bedrock |
| `google_cloud_custom_model.py` | 5000 (capped) | Custom model |
| `vllm_model.py` | 5000 (默认), 1 (logprobs) | vLLM 本地 |
| `ollama_model.py` | 5000 (默认) | Ollama 本地 |
| `langchain_ollama_model.py` | 5000 (默认) | LangChain + Ollama |
| `pytorch_gemma_model.py` | 5000 (默认) | PyTorch Gemma |
| `base_gpt_model.py` | 5000 (默认) | GPT 基类 |
| `gpt_model.py` | 5000 (默认) | OpenAI GPT |
| `azure_gpt_model.py` | 5000 (默认) | Azure GPT |
| `no_language_model.py` | 5000 (默认) | 占位符模型 |
| `retry_wrapper.py` | 透传 | 重试包装器 |
| `call_limit_wrapper.py` | 透传 | 限流包装器 |
| `utils.py` | 无配置 | 工具函数 |

#### 🎯 建议

1. **标准化 sample_choice 的行为**
   - 文档化不同实现的差异
   - 或统一到一个合理的值（如 1000-2000）

2. **统一层级默认值**
   - 考虑将 `language_model.DEFAULT_MAX_TOKENS` 也改为 4096
   - 或在文档层显式引用语言模型层的默认值

3. **添加配置类**
   - 创建 `TokenLimits` 类统一管理
   - 区分不同场景的推荐值

---

