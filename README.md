# Hermes Causal Memory

`causal-memory` is a Hermes general plugin that separates procedural skills from evidence-backed causal candidates. The LLM only extracts structured observations; deterministic code computes conditional probabilities, counterexamples, lift, and a confidence score.

## Ubuntu installation

On the Ubuntu machine where Hermes is installed, copy only this source directory (not Python's generated `__pycache__` folders):

```bash
mkdir -p ~/.hermes/plugins
cp -a /path/to/Hermes-Temporal-Memory ~/.hermes/plugins/causal-memory
hermes plugins enable causal-memory
hermes plugins list
```

The last command should show `causal-memory` enabled. Data is stored outside the plugin install directory in Hermes' plugin-data folder. Set `HERMES_CAUSAL_MEMORY_DIR` to override it, which is useful for an AIWiki repository.

## Workflow

1. Run a normal task. The plugin records user intent and non-plugin tool calls.
2. When the task is complete, invoke `/causal-learn capture-dut-trigger` in the same interactive session. It writes raw observations and updates `causal/<task>.yaml`.
3. Use `causal_query` and `causal_check` in later tasks. Promote candidates only after independent validation or a controlled intervention.

`auto_extract` is disabled by default to avoid an LLM call at the end of every Hermes `run_conversation` call. Enable it in the plugin settings only if that cost and cadence fit your workflow.

## Agent tools

- `causal_record_observation` records context, before-state facts, actions, effects, and an outcome.
- `causal_query` returns causal candidates with 2×2 counts, conditional probabilities, and lift.
- `causal_check` warns when a planned action is missing a historically strong condition; it never blocks execution.

## Important integration note

This MVP deliberately does not override Hermes' built-in `/learn`. It runs beside it: `/learn` produces `SKILL.md` (how), while `/causal-learn` produces observations and a causal candidate graph (what tends to influence what). That avoids coupling to internal `/learn` output formats and keeps model spending explicit.

## End-to-end smoke test

1. Start `hermes chat` and complete a small workflow with at least two tool calls, for example creating and then reading a scratch file.
2. Record observations with `causal_record_observation`, including both successful and failed attempts. For example, use `causes: [scope.armed]`, `actions: [dut.start]`, `effects: [trigger.captured]`; then record a comparable failed attempt without `scope.armed` and with `trigger.missed`.
3. In that same chat, run `/causal-learn smoke-test`. Hermes performs one structured LLM call, appends only grounded observations, and rebuilds the graph.
4. Ask the agent to call `causal_query` with `query: smoke test`. It should return `P(effect | cause)`, `P(effect | !cause)`, risk difference, lift, and sample counts.
5. Check `~/.hermes/plugin-data/causal-memory/causal/`. `candidate_cause` is still a statistical hypothesis—not proof—and should be validated before AIWiki promotion.
# Hermes 因果记忆插件

`causal‑memory` 是 Hermes 的通用插件，它把过程性技能与基于实证的因果候选项做解耦。大模型仅负责提取结构化观测数据；条件概率、反例、提升度（lift）以及置信分数全部由确定性代码计算得出。

## Ubuntu 安装步骤

在已部署 Hermes 的 Ubuntu 主机上，仅复制该源码目录（不要复制 Python 自动生成的 `__pycache__` 文件夹）：

```
mkdir -p ~/.hermes/plugins
cp -a /path/to/Hermes-Temporal-Memory ~/.hermes/plugins/causal-memory
hermes plugins enable causal-memory
hermes plugins list
```

执行最后一条命令后，输出应当显示 `causal‑memory` 已启用。
数据不存放在插件安装目录，而是保存在 Hermes 的 `plugin‑data` 目录。可以设置环境变量 `HERMES_CAUSAL_MEMORY_DIR` 修改存储路径，对接 AIWiki 知识库仓库时该配置十分有用。

## 工作流程

1. 执行普通任务。插件会记录用户意图以及非插件类工具调用。
2. 任务结束后，在同一个交互会话中执行 `/causal‑learn capture‑dut‑trigger`。该命令写入原始观测记录，并更新 `causal/<task>.yaml` 文件。
3. 在后续任务中使用 `causal_query` 和 `causal_check`。因果候选项必须经过独立验证或受控干预实验之后，才可以升级采信。

`auto_extract` 默认关闭，避免每次 Hermes 的 `run_conversation` 会话结束都额外调用大模型。只有当你可以接受对应的算力开销与执行频率时，才在插件配置中开启该选项。

## Agent 工具集

- `causal_record_observation`：记录上下文、执行前状态事实、动作、产生的影响以及最终结果。
- `causal_query`：返回因果候选项，附带 2×2 列联统计计数、条件概率、提升度（lift）。
- `causal_check`：当待执行动作缺少历史上关联性很强的前置条件时给出警告；**不会阻断任务执行**。

## 重要集成说明

本最小可用版本（MVP）刻意不去覆盖 Hermes 原生的 `/learn` 能力，二者并行工作：
`/learn` 生成 `SKILL.md`，描述**怎么做**；
`/causal‑learn` 输出观测数据集与因果候选关系图，描述**什么因素倾向于影响什么结果**。
这样设计避免强依赖 `/learn` 的内部输出格式，同时大模型调用开销清晰可控。

## 完整冒烟测试

1. 启动 `hermes chat`，完成一套简短流程，至少包含两次工具调用，例如创建临时文件，再读取该文件。
2. 使用 `causal_record_observation` 记录观测，成功、失败场景都要录入。示例：设置 `causes: [scope.armed]`，`actions: [dut.start]`，`effects: [trigger.captured]`；再记录一组对比失败案例：无 `scope.armed`，结果为 `trigger.missed`。
3. 在同一个对话会话里执行 `/causal‑learn smoke‑test`。Hermes 会发起一次结构化大模型调用，追加经过事实锚定的观测记录，重新构建因果关系图。
4. 让 Agent 调用 `causal_query`，参数 `query: smoke test`。应当返回：`P(结果 | 原因)`、`P(结果 | 无该原因)`、风险差值、提升度、样本统计数量。
5. 查看目录 `~/.hermes/plugin‑data/causal‑memory/causal/`。

> 
> 注意：`candidate_cause` 只是统计学假设，不等同于客观事实结论；在导入 AIWiki 知识库前务必完成验证。

---

### 术语小注

- lift：提升度，因果统计指标，衡量某原因对结果发生概率的增益幅度
- smoke‑test：冒烟测试，快速基础功能验证
- DUT：被测设备
- MVP：最小可用版本
- controlled intervention：受控干预实验
- 2×2 counts：2×2 列联表计数，因果统计基础样本表