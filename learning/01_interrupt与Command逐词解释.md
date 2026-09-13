# interrupt与Command逐词解释

## interrupt

```python
answer = interrupt({"question": "是否批准？"})
```

- `answer`：恢复后接收到的人工答案。
- `=`：把右边最终产生的值交给左边变量。
- `interrupt`：LangGraph提供的暂停函数。
- `(`和`)`：函数调用。
- `{}`：Python字典，用于向外部传递结构化问题。
- `"question"`：字典键。
- `"是否批准？"`：字典值。

首次执行到这里时，函数不会获得`answer`，而是让Graph暂停。恢复后，节点会重新进入，`interrupt`返回人工输入，代码才继续向下执行。

## Command(resume=...)

```python
graph.invoke(Command(resume="批准"), config)
```

- `Command`：告诉LangGraph这次不是启动新状态，而是发送控制命令。
- `resume=`：把值交给当前待恢复的interrupt。
- `graph.invoke`：真正执行Graph并取得结果。
- `config`：其中包含原来的`thread_id`。

## 为什么必须相同thread_id

```python
config = {"configurable": {"thread_id": "customer-C0010"}}
```

Checkpointer用`thread_id`寻找保存点。恢复时换成其他ID，相当于拿另一张取件号去取包裹，无法找到原流程。

## 当前可以忽略

- `Command`的全部高级参数。
- 分布式Checkpointer内部存储格式。
- interrupt ID的底层生成算法。

