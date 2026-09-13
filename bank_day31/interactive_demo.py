"""可交互演示：在两个interrupt处由终端用户亲自输入。"""

from uuid import uuid4

from bank_day31.full_bank_hitl import (
    create_graph,
    interrupt_payload,
    resume_flow,
    start_flow,
)


def main() -> None:
    graph = create_graph()
    thread_id = f"interactive-{uuid4()}"
    result = start_flow(graph, "C0010", thread_id)

    while payload := interrupt_payload(result):
        print("\nGraph已主动暂停，不是报错。")
        print("中断类型：", payload["kind"])
        print("问题：", payload["question"])
        print("当前推荐：", payload.get("recommendations", []))
        answer = input("请输入人工决定：")
        result = resume_flow(graph, thread_id, answer)

    print("\n流程已经结束。")
    print("执行状态：", result.get("execution_status"))
    print("审计轨迹：", " → ".join(result.get("audit_log", [])))


if __name__ == "__main__":
    main()

