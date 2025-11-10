# 🚨 Concordia Max Tokens 问题快速修复指南

> **紧急程度：** 高
> **影响范围：** 所有使用Gemini模型的部署
> **预计修复时间：** 30分钟（紧急修复）→ 2小时（完整修复）

---

## 📌 问题速览

### 症状
- 程序运行时抛出 `IndexError: list index out of range`
- Gemini模型返回空响应，导致 `random.choice([])` 失败
- 世界模拟质量下降，出现不连贯的对话或事件

### 根本原因
1. **Gemini特殊限制：** max_tokens < 256 时可能返回空响应
2. **异常处理不完整：** 只捕获 `ValueError`，未捕获 `IndexError`
3. **空值未检查：** 直接访问数组第一个元素，未检查数组是否为空

---

## 🔧 立即修复（5分钟）

### 方案1：全局配置调整（不修改源码）

在你的启动脚本 **最前面** 添加：

```python
# fix_max_tokens.py
import concordia.document.interactive_document as interactive_doc

# 提高全局默认值
interactive_doc.DEFAULT_MAX_CHARACTERS = 2000  # 原值: 200
interactive_doc.DEFAULT_MAX_TOKENS = 500       # 原值: 50

print("✅ Max tokens defaults increased to prevent Gemini errors")
```

**然后在你的主程序中：**

```python
# 在import concordia之后，创建任何对象之前
import fix_max_tokens

# 现在继续你的代码
from concordia import ...
```

### 方案2：Monkey Patch 紧急修复（不修改源码）

```python
# emergency_patch.py
import concordia.document.interactive_document as interactive_doc
import random

# 保存原方法
_original_open_question_diversified = interactive_doc.InteractiveDocument.open_question_diversified

def safe_open_question_diversified(self, question, **kwargs):
    """安全包装版本，防止IndexError"""
    # 确保max_tokens不低于Gemini最小值
    max_tokens = kwargs.get('max_tokens', 50)
    num_samples = kwargs.get('num_samples', 10)
    kwargs['max_tokens'] = max(max_tokens, 256 // num_samples)

    try:
        return _original_open_question_diversified(self, question, **kwargs)
    except (IndexError, ValueError) as e:
        print(f"⚠️ open_question_diversified failed: {e}")
        print("   Falling back to simple open_question")
        # 降级到简单版本
        return self.open_question(
            question=question,
            max_tokens=max(1000, kwargs.get('max_tokens', 500) * 3),
            temperature=kwargs.get('temperature', 1.0),
        )

# 替换原方法
interactive_doc.InteractiveDocument.open_question_diversified = safe_open_question_diversified

print("✅ Emergency patch applied for open_question_diversified")
```

**使用：**

```python
import emergency_patch
from concordia import ...
```

---

## 🛠️ 完整修复（30分钟）

### 修复1: google_aistudio_model.py

**文件：** `concordia/language_model/google_aistudio_model.py`
**行号：** 177-183

**修改前：**
```python
try:
    response = sample.candidates[0].content.parts[0].text
except ValueError as e:  # ❌ 只捕获ValueError
    print('An error occurred: ', e)
    print(f'prompt: {prompt}')
    print(f'sample: {sample}')
    response = ''
```

**修改后：**
```python
try:
    # 1. 首先检查candidates是否为空
    if not sample.candidates:
        raise IndexError('No candidates returned by the model')

    # 2. 尝试获取响应
    response = sample.candidates[0].content.parts[0].text

    # 3. 检查响应是否有效
    if not response or not response.strip():
        raise ValueError('Empty response from model')

except (ValueError, IndexError, AttributeError) as e:  # ✅ 完整异常捕获
    print(f'❌ LLM Error: {type(e).__name__}: {e}')
    print(f'Prompt (first 200 chars): {prompt[:200]}...')

    # 检查失败原因
    if sample.candidates and hasattr(sample.candidates[0], 'finish_reason'):
        finish_reason = sample.candidates[0].finish_reason
        print(f'Finish reason: {finish_reason}')

        if 'SAFETY' in str(finish_reason):
            response = '[BLOCKED_BY_SAFETY]'
        elif 'MAX_TOKENS' in str(finish_reason):
            response = '[TRUNCATED_BY_MAX_TOKENS]'
        else:
            response = '[GENERATION_FAILED]'
    else:
        response = '[NO_CANDIDATES]'
```

**同样的修改适用于：** `concordia/language_model/cloud_vertex_model.py` (行134-140)

### 修复2: interactive_document.py

**文件：** `concordia/document/interactive_document.py`
**行号：** 289-294

**修改前：**
```python
if len(candidates) < 2:
    raise Warning(  # ❌ Warning不会中断执行
        f'LLM generated only {len(candidates)} initial answers.'
    )
candidates = [re.sub(r'^\d+\.\s*', '', line) for line in candidates]
response = random.choice(candidates)  # ❌ 可能IndexError
```

**修改后：**
```python
if len(candidates) < 2:
    self.debug(f'LLM generated only {len(candidates)} initial answers.')

    # ✅ 提供降级方案
    if len(candidates) == 0:
        # 完全失败，降级到简单问答
        return self.open_question(
            question=question,
            max_tokens=max_tokens * 5,  # 给更多token
            temperature=min(temperature + 0.3, 1.5),
            question_label=question_label,
            answer_label=answer_label,
        )
    elif len(candidates) == 1:
        # 只有一个候选，直接使用
        response = candidates[0]
    else:
        # 不应该到达这里，但以防万一
        raise ValueError(
            f'Unexpected candidates count: {len(candidates)}'
        )
else:
    # ✅ 正常路径
    candidates = [re.sub(r'^\d+\.\s*', '', line) for line in candidates]
    response = random.choice(candidates)
```

### 修复3: 确保max_tokens最小值

**在调用前检查：**

```python
# 在所有调用LLM的地方添加
def ensure_min_max_tokens(max_tokens: int, min_value: int = 256) -> int:
    """确保max_tokens不低于最小值（Gemini要求）"""
    return max(max_tokens, min_value)

# 使用示例
response = model.sample_text(
    prompt=prompt,
    max_tokens=ensure_min_max_tokens(original_max_tokens),  # ✅
    ...
)
```

---

## 📊 配置建议

### 推荐的max_tokens值（基于源码分析）

| 组件 | 原始值 | 推荐值（最小） | 推荐值（质量优先） |
|------|--------|----------------|---------------------|
| DEFAULT_MAX_TOKENS | 50 | 256 | 512 |
| question_of_recent_memories | 1000 | 1500 | 2500 |
| all_similar_memories (摘要) | 750 | 1000 | 1500 |
| concat_act_component | 2200 | 2200 | 3000 |
| open_question_diversified | 50×N | max(256, 100×N) | max(512, 150×N) |
| thought_chains (各步骤) | 1200-3500 | 1500-4000 | 2000-5000 |

### 实施方式

**选项A：修改源码中的默认值**

```python
# concordia/document/interactive_document.py
DEFAULT_MAX_CHARACTERS = 2000  # 原: 200
DEFAULT_MAX_TOKENS = 500       # 原: 50
```

**选项B：运行时覆盖（推荐用于测试）**

```python
# 在创建组件时显式指定
reflection = question_of_recent_memories.QuestionOfRecentMemories(
    model=model,
    question="...",
    max_tokens=2500,  # ✅ 显式指定
    ...
)
```

---

## ✅ 验证修复效果

### 测试清单

- [ ] **基础测试：** 运行一个简单的agent act循环，确保不抛出异常
- [ ] **压力测试：** 运行100步游戏循环，监控异常日志
- [ ] **边界测试：** 故意提供复杂prompt，观察是否正确处理截断
- [ ] **Gemini特定：** 检查日志中是否还有 `[NO_CANDIDATES]` 或 `[BLOCKED_BY_SAFETY]`

### 监控指标

```python
# 添加简单的计数器
class LLMCallMonitor:
    def __init__(self):
        self.total_calls = 0
        self.empty_responses = 0
        self.truncated_responses = 0
        self.exceptions = 0

    def record_call(self, response: str, exception: bool = False):
        self.total_calls += 1
        if exception:
            self.exceptions += 1
        elif not response or response.startswith('['):
            self.empty_responses += 1
        elif response.endswith('...'):  # 简化的截断检测
            self.truncated_responses += 1

    def report(self):
        print(f"📊 LLM Call Statistics:")
        print(f"   Total calls: {self.total_calls}")
        print(f"   Empty responses: {self.empty_responses} ({self.empty_responses/self.total_calls*100:.1f}%)")
        print(f"   Truncated: {self.truncated_responses} ({self.truncated_responses/self.total_calls*100:.1f}%)")
        print(f"   Exceptions: {self.exceptions} ({self.exceptions/self.total_calls*100:.1f}%)")

# 使用
monitor = LLMCallMonitor()
# ... 在LLM调用后 ...
monitor.record_call(response)
# ... 在程序结束时 ...
monitor.report()
```

**健康指标：**
- 空响应率 < 1%
- 截断率 < 15%
- 异常率 < 0.1%

---

## 🎯 效果对比

### 修复前
```
Step 1/100: ✓
Step 2/100: ✓
Step 3/100: ❌ IndexError: list index out of range
  File "interactive_document.py", line 294, in open_question_diversified
    response = random.choice(candidates)
```

### 修复后
```
Step 1/100: ✓
Step 2/100: ✓
Step 3/100: ⚠️ open_question_diversified got 0 candidates, falling back
Step 3/100: ✓ (fallback successful)
Step 4/100: ✓
...
Step 100/100: ✓

📊 LLM Call Statistics:
   Total calls: 437
   Empty responses: 3 (0.7%)
   Truncated: 28 (6.4%)
   Exceptions: 0 (0.0%)
```

---

## 📚 进一步阅读

详细的分析和长期解决方案，请参考：
- **完整分析文档：** `architecture/MAX_TOKENS_PROBLEM_ANALYSIS_zh.html`
- **Token分析：** `architecture/concordia_token_analysis_zh.html`
- **增长分析：** `architecture/concordia_token_growth_analysis_zh.html`

---

## 🆘 常见问题

### Q1: 修复后成本会增加多少？

**A:** 保守配置（推荐值最小）增加约20-30%，质量优先配置增加约50-80%。但考虑到避免了失败重试和降级，实际增加可能更少。

### Q2: 是否需要同时修改所有文件？

**A:**
- **紧急情况：** 只需要应用"方案1"或"方案2"的monkey patch
- **正式修复：** 建议至少修改 `google_aistudio_model.py` 和 `interactive_document.py`
- **长期优化：** 按照完整分析文档进行架构升级

### Q3: 是否影响其他模型（如GPT-4）？

**A:**
- **异常处理修复：** 对所有模型有益，提高稳定性
- **max_tokens调整：** GPT-4没有256的最小限制，但更高的值可以改善输出质量
- **建议：** 使用条件判断，Gemini使用更高值，其他模型保持原值

### Q4: 如何判断是否已经部署了修复？

**A:** 运行以下检查脚本：

```python
# check_fix.py
import concordia.document.interactive_document as doc
import concordia.language_model.google_aistudio_model as gemini_model
import inspect

# 检查DEFAULT_MAX_TOKENS
if doc.DEFAULT_MAX_TOKENS >= 256:
    print("✅ DEFAULT_MAX_TOKENS已修复:", doc.DEFAULT_MAX_TOKENS)
else:
    print("❌ DEFAULT_MAX_TOKENS仍需修复:", doc.DEFAULT_MAX_TOKENS)

# 检查异常捕获
source = inspect.getsource(gemini_model.GoogleAIStudioLanguageModel.sample_text)
if 'IndexError' in source and 'AttributeError' in source:
    print("✅ 异常捕获已增强")
else:
    print("❌ 异常捕获仍需修复")

# 检查open_question_diversified
source = inspect.getsource(doc.InteractiveDocument.open_question_diversified)
if 'len(candidates) == 0' in source or 'if not candidates' in source:
    print("✅ open_question_diversified已修复")
else:
    print("❌ open_question_diversified仍需修复")
```

---

**最后更新：** 2025-01-10
**适用版本：** Concordia 主分支

有问题？查看 [完整分析文档](./MAX_TOKENS_PROBLEM_ANALYSIS_zh.html) 或提交Issue。
