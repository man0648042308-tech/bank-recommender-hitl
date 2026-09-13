# VS Code/Codex子智能体实践证据

## 实践目标

使用一个独立、只读的子智能体审查Day31练习5，不让它修改代码或读取密钥。主线程负责实现，子智能体只负责发现控制流和验证盲区，形成“生成器与评估器分离”。

## 下达的任务

```text
只读审查Day31练习5和本机LangGraph 1.2.x的interrupt、Command、MemorySaver语义。
输出课程参考代码潜在问题、推荐状态设计、节点路由、必须覆盖的测试边界，
以及如何证明暂停与相同thread_id恢复。不要修改文件，不读取.env或密钥。
```

## 子智能体环境与结论

- 角色：只读代码仓库审查子智能体。
- 实测版本：LangGraph 1.2.11。
- 未修改文件，未读取`.env`、API Key或Token。

发现的两个致命问题：

1. 课程答案使用`Command(goto="human_review_full")`，但Graph注册的节点名是`review`，拒绝后的重试会被写向不存在的节点并被忽略。
2. 课程答案创建`graph.stream(Command(resume=...))`后没有迭代。`stream()`是惰性迭代器，不消费就不会真正恢复执行。

其他重要结论：

- `MemorySaver`只适合进程内教学测试，不是生产持久化。
- interrupt恢复时节点从开头重新进入，中断之前不能放不可重复的真实副作用。
- 产品推荐应保存ID、风险和门槛，不能只保存产品名。
- 必须用`graph.get_state(config).next`证明暂停节点，不能只看打印文本。
- 错误`thread_id`不能恢复原流程，线程状态必须隔离。

## 主线程采纳的建议

- 采用纯路由函数和`add_conditional_edges`，不混用错误的`Command(goto=...)`。
- 使用`graph.invoke(Command(resume=...))`并直接取得结果，避免未消费stream。
- 在运行证据中输出首次`next=('review',)`、恢复后`next=('confirm',)`和最终`next=()`。
- 将推荐保存为包含产品ID、名称、风险和起投金额的字典。
- 增加错误thread、线程隔离、未知客户和执行次数测试。
- 明确记录MemorySaver的教学边界。

## 未完全采纳的建议及原因

子智能体建议为客户拒绝增加独立`finalize_customer_rejected`节点。本作业保留课程要求中的`execute`节点，但该节点首先检查`customer_accept`：客户拒绝时只记录状态，不办理产品、不发送通知，并由自动测试验证。这样既保持课程五节点结构，也保证没有真实执行副作用。

## 最终验证门槛

- Python编译通过。
- 10项自动测试通过。
- 三条端到端业务分支通过。
- 暂停、恢复和结束位置有快照证据。
- 不通过删除测试或放宽断言制造通过。

