"""Day31练习5：可暂停、人工复核、客户确认和恢复的银行推荐流程。"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from bank_day31.data import CUSTOMERS, PRODUCTS
from bank_day31.recommendation_rules import eligible_products


class FullBankState(TypedDict, total=False):
    customer_id: str
    customer_info: dict[str, Any]
    recommendations: list[dict[str, Any]]
    excluded_product_ids: list[str]
    review_decision: str
    review_comment: str
    retry_count: int
    customer_accept: bool
    execution_status: str
    executed_product_id: str
    execution_id: str
    execution_count: int
    notification: str
    audit_log: list[str]


def _append_log(state: FullBankState, event: str) -> list[str]:
    return [*state.get("audit_log", []), event]


def profile_analysis(state: FullBankState) -> dict[str, Any]:
    """根据customer_id加载数据并派生年龄、收入画像。"""
    customer_id = state["customer_id"]
    if customer_id not in CUSTOMERS:
        raise ValueError(f"客户不存在：{customer_id}")

    customer = deepcopy(CUSTOMERS[customer_id])
    age = int(customer["age"])
    income = float(customer["monthly_income"])
    customer["age_group"] = "青年" if age < 35 else "中年" if age < 55 else "老年"
    customer["income_level"] = "高" if income > 50_000 else "中" if income > 15_000 else "低"
    return {
        "customer_info": customer,
        "audit_log": _append_log(state, "画像分析完成"),
    }


def initial_recommendation(state: FullBankState) -> dict[str, Any]:
    """执行可测试的风险、金额和复核排除规则，返回最多三个产品。"""
    selected = eligible_products(
        state["customer_info"],
        PRODUCTS,
        state.get("excluded_product_ids", []),
    )[:3]
    if not selected:
        raise ValueError("没有满足适当性规则的候选产品")
    return {
        "recommendations": selected,
        "review_decision": "待复核",
        "audit_log": _append_log(state, "初步推荐完成"),
    }


def _parse_review_feedback(feedback: Any) -> tuple[str, str]:
    text = str(feedback).strip()
    decision_text, separator, comment = text.partition(",")
    if not separator:
        decision_text, separator, comment = text.partition("，")
    decision = decision_text.strip()
    if decision not in {"批准", "拒绝"}:
        raise ValueError("复核输入必须以“批准”或“拒绝”开头")
    return decision, comment.strip()


def human_review(state: FullBankState) -> dict[str, Any]:
    """暂停Graph，等待复核员批准或拒绝。"""
    feedback = interrupt(
        {
            "kind": "human_review",
            "question": "复核员请输入：批准/拒绝及理由",
            "attempt": state.get("retry_count", 0) + 1,
            "customer_id": state["customer_id"],
            "recommendations": [item["name"] for item in state["recommendations"]],
        }
    )
    decision, comment = _parse_review_feedback(feedback)
    retry_count = state.get("retry_count", 0) + 1
    update: dict[str, Any] = {
        "review_decision": decision,
        "review_comment": comment,
        "retry_count": retry_count,
        "audit_log": _append_log(state, f"人工复核：{decision}"),
    }

    if decision == "拒绝":
        excluded = list(state.get("excluded_product_ids", []))
        first_product_id = state["recommendations"][0]["product_id"]
        if first_product_id not in excluded:
            excluded.append(first_product_id)
        update["excluded_product_ids"] = excluded
        if retry_count >= 2:
            update["execution_status"] = "人工复核拒绝：重试次数已用尽"
    return update


def route_after_review(state: FullBankState) -> str:
    if state["review_decision"] == "批准":
        return "confirm"
    if state.get("retry_count", 0) >= 2:
        return "stop"
    return "retry"


def customer_confirmation(state: FullBankState) -> dict[str, Any]:
    """第二个人工中断：等待客户确认是否接受最终推荐。"""
    answer = interrupt(
        {
            "kind": "customer_confirmation",
            "question": "客户是否接受最终推荐？(y/n)",
            "customer": state["customer_info"]["name"],
            "recommendations": [item["name"] for item in state["recommendations"]],
        }
    )
    normalized = str(answer).strip().lower()
    if normalized not in {"y", "yes", "是", "n", "no", "否"}:
        raise ValueError("客户确认只能输入y/yes/是或n/no/否")
    accepted = normalized in {"y", "yes", "是"}
    return {
        "customer_accept": accepted,
        "audit_log": _append_log(state, f"客户确认：{'接受' if accepted else '拒绝'}"),
    }


def execute_operation(state: FullBankState) -> dict[str, Any]:
    """模拟办理产品和发送通知，不调用真实外部系统。"""
    if not state.get("customer_accept", False):
        return {
            "execution_status": "客户拒绝",
            "notification": "未发送通知",
            "audit_log": _append_log(state, "流程结束：客户拒绝"),
        }

    product = state["recommendations"][0]
    return {
        "execution_status": "模拟执行成功",
        "executed_product_id": product["product_id"],
        "execution_id": f"SIM-{uuid4()}",
        "execution_count": state.get("execution_count", 0) + 1,
        "notification": f"已模拟向客户发送{product['name']}办理通知",
        "audit_log": _append_log(state, "模拟执行完成"),
    }


def create_graph(checkpointer: MemorySaver | None = None):
    builder = StateGraph(FullBankState)
    builder.add_node("profile", profile_analysis)
    builder.add_node("recommend", initial_recommendation)
    builder.add_node("review", human_review)
    builder.add_node("confirm", customer_confirmation)
    builder.add_node("execute", execute_operation)

    builder.add_edge(START, "profile")
    builder.add_edge("profile", "recommend")
    builder.add_edge("recommend", "review")
    builder.add_conditional_edges(
        "review",
        route_after_review,
        {"confirm": "confirm", "retry": "recommend", "stop": END},
    )
    builder.add_edge("confirm", "execute")
    builder.add_edge("execute", END)
    return builder.compile(checkpointer=checkpointer or MemorySaver())


def thread_config(thread_id: str) -> dict[str, dict[str, str]]:
    return {"configurable": {"thread_id": thread_id}}


def initial_state(customer_id: str) -> FullBankState:
    return {
        "customer_id": customer_id,
        "retry_count": 0,
        "excluded_product_ids": [],
        "audit_log": [],
    }


def start_flow(graph, customer_id: str, thread_id: str) -> FullBankState:
    return graph.invoke(initial_state(customer_id), thread_config(thread_id))


def resume_flow(graph, thread_id: str, answer: str) -> FullBankState:
    return graph.invoke(Command(resume=answer), thread_config(thread_id))


def interrupt_payload(result: FullBankState) -> dict[str, Any] | None:
    interruptions = result.get("__interrupt__", ())  # type: ignore[typeddict-item]
    if not interruptions:
        return None
    return interruptions[0].value


def run_approved_scenario() -> FullBankState:
    graph = create_graph()
    thread_id = f"approved-{uuid4()}"
    result = start_flow(graph, "C0010", thread_id)
    assert interrupt_payload(result)["kind"] == "human_review"  # type: ignore[index]
    result = resume_flow(graph, thread_id, "批准, 风险与金额均合适")
    assert interrupt_payload(result)["kind"] == "customer_confirmation"  # type: ignore[index]
    return resume_flow(graph, thread_id, "y")


def run_retry_scenario() -> FullBankState:
    graph = create_graph()
    thread_id = f"retry-{uuid4()}"
    first = start_flow(graph, "C0010", thread_id)
    first_ids = [item["product_id"] for item in first["recommendations"]]
    result = resume_flow(graph, thread_id, "拒绝, 请更换首选产品")
    second_ids = [item["product_id"] for item in result["recommendations"]]
    assert first_ids != second_ids
    result = resume_flow(graph, thread_id, "批准, 调整后合适")
    return resume_flow(graph, thread_id, "n")


def run_rejected_scenario() -> FullBankState:
    graph = create_graph()
    thread_id = f"rejected-{uuid4()}"
    start_flow(graph, "C0010", thread_id)
    resume_flow(graph, thread_id, "拒绝, 第一批不合适")
    return resume_flow(graph, thread_id, "拒绝, 第二批仍不合适")


def collect_state_trace() -> list[str]:
    """用快照而不是只看print，证明暂停、恢复和结束位置。"""
    graph = create_graph()
    thread_id = f"trace-{uuid4()}"
    config = thread_config(thread_id)
    first = start_flow(graph, "C0010", thread_id)
    lines = [
        f"首次中断={interrupt_payload(first)['kind']}",  # type: ignore[index]
        f"首次next={graph.get_state(config).next}",
    ]
    second = resume_flow(graph, thread_id, "批准, 状态追踪")
    lines.extend(
        [
            f"恢复后中断={interrupt_payload(second)['kind']}",  # type: ignore[index]
            f"恢复后next={graph.get_state(config).next}",
        ]
    )
    resume_flow(graph, thread_id, "y")
    lines.append(f"最终next={graph.get_state(config).next}")
    return lines


def main() -> None:
    print("=== Checkpointer状态证据 ===")
    for line in collect_state_trace():
        print(line)

    approved = run_approved_scenario()
    print("\n=== 场景1：复核批准、客户接受 ===")
    print("执行状态：", approved["execution_status"])
    print("办理产品：", approved["executed_product_id"])
    print("模拟执行次数：", approved["execution_count"])
    print("通知：", approved["notification"])
    print("审计轨迹：", " → ".join(approved["audit_log"]))

    retry = run_retry_scenario()
    print("\n=== 场景2：复核拒绝后重试、客户拒绝 ===")
    print("复核次数：", retry["retry_count"])
    print("执行状态：", retry["execution_status"])
    print("审计轨迹：", " → ".join(retry["audit_log"]))

    rejected = run_rejected_scenario()
    print("\n=== 场景3：连续两次复核拒绝 ===")
    print("复核次数：", rejected["retry_count"])
    print("执行状态：", rejected["execution_status"])
    print("审计轨迹：", " → ".join(rejected["audit_log"]))
    print("\nDay31完整HITL流程验证通过。")


if __name__ == "__main__":
    main()
