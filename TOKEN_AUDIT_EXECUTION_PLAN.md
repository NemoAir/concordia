# Token 审计执行计划

**创建时间**: 2025-11-08 Session 1
**总文件数**: 281 个 Python 文件
**预计时间**: 5-10 Sessions

---

## 🎯 可靠执行策略

### 核心原则

1. **完整阅读，不遗漏**
   - 每个文件从头到尾完整读取
   - 不依赖搜索，避免遗漏边界情况
   - 记录每个文件的阅读状态

2. **实时记录，不丢失**
   - 每发现一个参数立即记录到 TOKEN_CONFIG.md
   - 每读完 5-10 个文件更新 TOKEN_AUDIT_PROGRESS.md
   - 使用 Git commit 保存里程碑

3. **分阶段推进，可恢复**
   - 按目录分阶段审计
   - 每完成一个阶段 commit
   - Session 中断后可从任意阶段恢复

4. **优先级驱动，先重要**
   - 优先审计核心模块（language_model, document）
   - 其次审计高频使用组件
   - 最后审计辅助模块

---

## 📋 分阶段执行计划

### Phase 1: 核心层 (优先级最高) 🔴

**目标**: 审计语言模型和文档生成核心

#### Stage 1.1: Language Model 核心 (7 个文件)
- [ ] `concordia/language_model/__init__.py`
- [ ] `concordia/language_model/language_model.py` ⭐ 最重要
- [ ] `concordia/language_model/google_aistudio_model.py` ⭐
- [ ] `concordia/language_model/cloud_vertex_model.py`
- [ ] `concordia/language_model/openai_model.py`
- [ ] `concordia/language_model/mistral_model.py`
- [ ] `concordia/language_model/utils.py`

**预计发现**: 10-15 个 token 配置参数

#### Stage 1.2: Document 核心 (3 个文件)
- [x] `concordia/document/interactive_document.py` ✅ 已审计
- [ ] `concordia/document/document.py`
- [ ] `concordia/document/__init__.py`

**预计发现**: 5-10 个参数

#### Stage 1.3: Thought Chains (2 个文件)
- [ ] `concordia/thought_chains/thought_chains.py` ⭐ 部分已知
- [ ] `concordia/thought_chains/__init__.py`

**预计发现**: 15-20 个参数

**Phase 1 完成标志**: 提交 commit "审计：完成核心层 token 配置审计"

---

### Phase 2: 组件层 (优先级高) 🟠

**目标**: 审计所有 Agent 和 Game Master 组件

#### Stage 2.1: Agent 组件 (~30 个文件)

**子阶段 2.1.1: 已修改的组件** (优先验证)
- [x] `concordia/components/agent/question_of_recent_memories.py` ✅
- [x] `concordia/components/agent/concat_act_component.py` ✅
- [ ] 其他需要验证是否还有遗漏

**子阶段 2.1.2: 记忆相关组件**
- [ ] `concordia/components/agent/all_similar_memories.py`
- [ ] `concordia/components/agent/memory_component.py`
- [ ] (其他记忆组件...)

**子阶段 2.1.3: 行动相关组件**
- [ ] `concordia/components/agent/action_spec_ignored.py`
- [ ] (其他行动组件...)

**子阶段 2.1.4: 其他 Agent 组件**
- [ ] 逐一审计剩余文件

**预计发现**: 20-30 个参数

#### Stage 2.2: Game Master 组件 (~40 个文件)

**子阶段 2.2.1: 已修改的组件** (优先验证)
- [x] `concordia/components/game_master/formative_memories_initializer.py` ✅
- [ ] `concordia/components/game_master/make_observation.py` (部分已知)
- [x] `concordia/components/game_master/switch_act.py` ✅
- [x] `concordia/components/game_master/next_acting.py` ✅

**子阶段 2.2.2: 初始化器组件**
- [ ] `concordia/components/game_master/instructions.py`
- [ ] (其他初始化器...)

**子阶段 2.2.3: 事件处理组件**
- [ ] `concordia/components/game_master/event_resolution.py`
- [ ] (其他事件组件...)

**子阶段 2.2.4: 其他 GM 组件**
- [ ] 逐一审计剩余文件

**预计发现**: 30-40 个参数

**Phase 2 完成标志**: 提交 commit "审计：完成组件层 token 配置审计"

---

### Phase 3: 应用层 (优先级中) 🟡

#### Stage 3.1: Agents 实现 (~10 个文件)
- [ ] `concordia/agents/entity_agent.py`
- [ ] `concordia/agents/entity_agent_with_logging.py`
- [ ] (其他...)

#### Stage 3.2: Prefabs 预制模板 (~20 个文件)
- [ ] `concordia/prefabs/simulation/*.py`
- [ ] `concordia/prefabs/agent/*.py`
- [ ] `concordia/prefabs/game_master/*.py`

#### Stage 3.3: Environment 环境 (~15 个文件)
- [ ] `concordia/environment/engines/*.py`
- [ ] (其他...)

**预计发现**: 15-25 个参数

**Phase 3 完成标志**: 提交 commit "审计：完成应用层 token 配置审计"

---

### Phase 4: 支持层 (优先级低) 🟢

#### Stage 4.1: Associative Memory (~10 个文件)
#### Stage 4.2: Typing 类型定义 (~5 个文件)
#### Stage 4.3: Utils 工具 (~10 个文件)
#### Stage 4.4: Clocks 时钟 (~3 个文件)
#### Stage 4.5: Contrib 贡献 (~30 个文件)

**预计发现**: 5-10 个参数

**Phase 4 完成标志**: 提交 commit "审计：完成支持层 token 配置审计"

---

### Phase 5: 清理与文档 🔵

- [ ] 排除 deprecated/ 中的废弃代码
- [ ] 排除 testing/ 中的测试代码
- [ ] 整理 TOKEN_CONFIG.md
- [ ] 编写配置类设计文档
- [ ] 生成统计报告

**Phase 5 完成标志**: 提交 commit "审计：完成全部 token 配置审计，生成报告"

---

## 🔄 Session 恢复流程

### 如果 Session 中断，下一个 Session 应该：

```bash
# Step 1: 恢复上下文
cd /workspaces/concordia
cat TOKEN_AUDIT_PROGRESS.md        # 查看总体进度
cat TOKEN_CONFIG.md                # 查看已发现的配置
cat TOKEN_AUDIT_EXECUTION_PLAN.md # 查看当前执行计划

# Step 2: 确定位置
# 查找最后完成的文件
git log --oneline | grep "审计" | head -1

# Step 3: 继续工作
# 根据 TOKEN_AUDIT_PROGRESS.md 中的 "下一步行动" 继续
```

### 恢复检查清单

- [ ] 读取 TOKEN_AUDIT_PROGRESS.md 确认当前阶段
- [ ] 读取 TOKEN_CONFIG.md 查看已记录的参数数量
- [ ] 查看 Git log 确认最后的 commit
- [ ] 根据进度文档的 "下一步行动" 继续
- [ ] 更新进度文档的 "当前 Session" 编号

---

## 📊 预期成果

### 最终交付物

1. **TOKEN_CONFIG.md** (完整版)
   - 100+ 个 token 配置参数
   - 每个参数的详细说明
   - 配置层级和依赖关系
   - 统计分析和可视化

2. **token_config.py** (新建配置类)
   - 统一的配置接口
   - 语义化的常量定义
   - 向后兼容层

3. **重构计划** (migration guide)
   - 逐步替换硬编码
   - 迁移时间表
   - 测试策略

4. **完整的 Git 历史**
   - 每个阶段有清晰的 commit
   - Commit message 包含发现数量
   - 易于回溯和审查

---

## 📈 进度追踪

### 文件审计进度

```
总计: 281 文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1 (核心层):      0/12   [ 0%]  ░░░░░░░░░░
Phase 2 (组件层):      0/70   [ 0%]  ░░░░░░░░░░
Phase 3 (应用层):      0/45   [ 0%]  ░░░░░░░░░░
Phase 4 (支持层):      0/58   [ 0%]  ░░░░░░░░░░
Phase 5 (清理):        0/1    [ 0%]  ░░░░░░░░░░
Deprecated/Test:       96      [跳过]

已审计: 1/281 (0.4%)
剩余: 280
```

*(上述进度条将在每次更新 TOKEN_AUDIT_PROGRESS.md 时更新)*

---

## 🎯 当前任务 (Session 1)

**当前阶段**: Phase 1, Stage 1.1
**当前任务**: 审计 `language_model/` 目录

**下一个文件**: 
```
concordia/language_model/__init__.py
```

**行动**:
1. ✅ 生成文件清单 (281 文件)
2. ⏳ 开始读取 `concordia/language_model/__init__.py`
3. ⏳ 逐一读取 language_model/ 中的 7 个文件
4. ⏳ 更新 TOKEN_CONFIG.md
5. ⏳ 完成 Stage 1.1

---

## 🚀 开始执行

准备就绪，开始系统审计！

**命令序列**:
```bash
# 1. 确认当前状态
pwd  # /workspaces/concordia
ls -la TOKEN_*.md  # 确认文档已创建

# 2. 开始读取第一个文件
cat concordia/language_model/__init__.py

# 3. 使用 read_file 工具完整读取
# read_file(target_file="concordia/language_model/__init__.py")

# 4. 记录发现
# 更新 TOKEN_CONFIG.md

# 5. 继续下一个文件
# ...
```

---

*让我们开始这个漫长但有价值的旅程！* 🚀

---

*最后更新: 2025-11-08 Session 1*

