# Repository Guidelines

## 项目结构与模块组织
- `concordia/`：核心库（agents、environment、language_model、utils、prefabs、testing）；测试与代码同目录，命名为 `*_test.py`。
- `examples/`：示例与教程笔记本（测试前会转换为 `.py`）。
- `bin/`：脚本：`install.sh`、`test.sh`、`test_examples.sh`、`convert_notebooks.sh`。
- `.github/`：CI 工作流与复合动作 `actions/install`（固定依赖、venv）。
- 根目录：`pyproject.toml`、`requirements.txt`、`setup.py`、`.pylintrc`、`.devcontainer/`。

## 构建、测试与本地开发
- 安装（开发）：`pip install -e .[dev]` 或 `./bin/install.sh`（使用固定的 `requirements.txt`）。
- 单元测试：`pytest -n auto` 或 `./bin/test.sh`（pytest + pytype + pylint）。
- 示例/笔记本：`./bin/test_examples.sh`（测试 `examples/`，转换并检查 notebooks）。
- 类型检查：`pytype concordia`，`pytype examples`。
- Lint：`pylint --errors-only concordia examples`。

## 代码风格与命名约定
- Python 3.11+；格式化：`pyink`（见 `pyproject.toml`），80 列、2 空格缩进。
- 导入：`isort`（Google profile）。提交前运行格式化与排序。
- 命名：文件/模块 `snake_case.py`；类 `PascalCase`；函数/变量 `snake_case`。
- 文档：Google 风格 Docstring，配合类型注解；为公共 API 保持文档齐全。

## 测试指引
- 框架：`pytest` + `xdist`（`-n auto`）。测试文件命名为 `*_test.py` 并与代码同目录。
- 新功能与缺陷修复需附带测试；保持小而可复现。
- 提交前本地运行：`./bin/test.sh`；如涉及示例，再运行 `./bin/test_examples.sh`。

## 提交与 Pull Request 规范
- 提交信息用祈使句、聚焦变更（如 “Fix parser for commas”）；必要时补充背景说明。
- PR 内容：变更说明、关联 issue、是否破坏性变更、测试/文档更新；确保本地测试、lint、类型检查均通过。
- 贡献需签署 Google CLA（见 `CONTRIBUTING.md`）。

## 安全与配置提示（可选）
- 通过环境变量配置 LLM：如 `OPENAI_API_KEY`、`GOOGLE_API_KEY`；其他提供商按对应包装器说明。
- 切勿提交秘钥；请遵循 `SECURITY.md` 报告安全问题。
