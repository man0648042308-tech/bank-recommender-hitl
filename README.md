> 本仓库为个人作品集公开版：AI 大模型应用开发工程实践项目，模拟数据，非生产系统。更多项目见作品集主页。

# 项目：LangGraph人类在环银行推荐流程

## 项目完成情况

| 要求 | 对应文件 |
|---|---|
| Typora技术总结 | `Day31学习总结.md` |
| 示例5完整银行推荐流程 | `bank_day31/full_bank_hitl.py` |
| 交互式人工复核与客户确认 | `bank_day31/interactive_demo.py` |
| Checkpointer、interrupt、Command恢复 | `full_bank_hitl.py`及自动测试 |
| VS Code/Codex子智能体附加题 | `subagent_evidence/VSCode_Codex子智能体实践.md` |
| Claude Code附加题说明 | `subagent_evidence/ClaudeCode子智能体实践说明.md` |
| 自动验证 | `tests/test_full_bank_hitl.py`、`bank_day31/run_evidence.py` |

## 项目流程

```text
客户画像 → 确定性推荐 → 人工复核interrupt
                         ├─ 拒绝且可重试 → 重新推荐
                         ├─ 连续拒绝 → 终止
                         └─ 批准 → 客户确认interrupt
                                      ├─ 接受 → 模拟执行
                                      └─ 拒绝 → 不执行
```

金融适当性由普通Python规则负责：产品风险不能超过客户风险承受等级，产品起投金额不能超过客户可投资金额。大模型不参与最终准入判断。

## 安装

在PowerShell中执行：

```powershell
Set-Location ./BankRS_Day31_HITL
uv sync
```

## 一键验证

```powershell
uv run python -m bank_day31.run_evidence
```

预期结果包括：

- 10项测试全部通过；
- 批准且客户接受后“模拟执行成功”；
- 人工拒绝后重新推荐；
- 客户拒绝时不办理产品；
- 连续两次复核拒绝后流程终止。

## 亲自操作两个中断点

```powershell
uv run python -m bank_day31.interactive_demo
```

第一次提示输入复核决定，可输入：

```text
批准, 产品合适
```

第二次提示输入客户决定，可输入：

```text
y
```

拒绝重试可在第一次输入：

```text
拒绝, 请更换首选产品
```

程序显示“Graph已主动暂停”是HITL正常行为，不是异常。

`MemorySaver`只在当前Python进程内保存状态，适合功能演示和测试，不是跨进程的生产持久化。生产环境应替换为PostgresSaver等持久化Checkpointer。

## 单独运行

```powershell
uv run python -m pytest
uv run python -m bank_day31.full_bank_hitl
uv run python -m bank_day31.interactive_demo
```

## 截图建议

1. `uv run python -m pytest`显示10项测试通过。
2. 批准、客户接受、模拟执行成功场景。
3. 拒绝重试和连续拒绝终止场景。
4. Typora打开`Day31学习总结.md`。
5. 子智能体审查任务和结论。

不要提交`.venv`、`.env`、缓存或真实客户数据。本项目未调用外部模型，没有读取API Key。
