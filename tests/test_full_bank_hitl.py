import pytest

from bank_day31.full_bank_hitl import (
    create_graph,
    interrupt_payload,
    resume_flow,
    start_flow,
    thread_config,
)
from bank_day31.recommendation_rules import RISK_ORDER


def test_first_run_pauses_at_human_review_and_saves_state():
    graph = create_graph()
    result = start_flow(graph, "C0010", "pause-review")
    payload = interrupt_payload(result)

    assert payload is not None
    assert payload["kind"] == "human_review"
    assert result["recommendations"]
    assert graph.get_state(thread_config("pause-review")).next == ("review",)


def test_approve_then_accept_executes_product():
    graph = create_graph()
    thread_id = "approve-accept"
    start_flow(graph, "C0010", thread_id)
    result = resume_flow(graph, thread_id, "批准, 产品合适")

    assert interrupt_payload(result)["kind"] == "customer_confirmation"
    assert graph.get_state(thread_config(thread_id)).next == ("confirm",)

    result = resume_flow(graph, thread_id, "y")
    assert interrupt_payload(result) is None
    assert result["execution_status"] == "模拟执行成功"
    assert result["executed_product_id"]
    assert result["execution_count"] == 1
    assert graph.get_state(thread_config(thread_id)).next == ()


def test_review_rejection_changes_recommendation_and_retries():
    graph = create_graph()
    thread_id = "reject-retry"
    first = start_flow(graph, "C0010", thread_id)
    first_ids = [item["product_id"] for item in first["recommendations"]]

    second = resume_flow(graph, thread_id, "拒绝, 请更换首选产品")
    second_ids = [item["product_id"] for item in second["recommendations"]]

    assert interrupt_payload(second)["kind"] == "human_review"
    assert second["retry_count"] == 1
    assert first_ids != second_ids
    assert first_ids[0] not in second_ids


def test_two_review_rejections_stop_without_execution():
    graph = create_graph()
    thread_id = "reject-stop"
    start_flow(graph, "C0010", thread_id)
    resume_flow(graph, thread_id, "拒绝, 第一批不合适")
    result = resume_flow(graph, thread_id, "拒绝, 第二批也不合适")

    assert interrupt_payload(result) is None
    assert result["retry_count"] == 2
    assert result["execution_status"] == "人工复核拒绝：重试次数已用尽"
    assert "executed_product_id" not in result


def test_customer_decline_does_not_execute_product():
    graph = create_graph()
    thread_id = "customer-decline"
    start_flow(graph, "C0010", thread_id)
    resume_flow(graph, thread_id, "批准")
    result = resume_flow(graph, thread_id, "n")

    assert result["customer_accept"] is False
    assert result["execution_status"] == "客户拒绝"
    assert result["notification"] == "未发送通知"
    assert "executed_product_id" not in result


def test_recommendations_obey_risk_and_amount_rules():
    graph = create_graph()
    result = start_flow(graph, "C0020", "suitability")
    customer = result["customer_info"]

    assert all(
        RISK_ORDER[product["risk_level"]] <= RISK_ORDER[customer["risk_tolerance"]]
        and product["min_investment"] <= customer["investment_amount"]
        for product in result["recommendations"]
    )


def test_invalid_human_input_is_rejected():
    graph = create_graph()
    thread_id = "invalid-input"
    start_flow(graph, "C0010", thread_id)
    with pytest.raises(ValueError, match="批准.*拒绝"):
        resume_flow(graph, thread_id, "随便")


def test_wrong_thread_cannot_resume_original_checkpoint():
    graph = create_graph()
    original = "original-thread"
    start_flow(graph, "C0010", original)
    before = graph.get_state(thread_config(original))

    with pytest.raises(KeyError):
        resume_flow(graph, "wrong-thread", "批准")

    after = graph.get_state(thread_config(original))
    assert before.next == after.next == ("review",)
    assert before.values["customer_id"] == after.values["customer_id"] == "C0010"


def test_two_threads_keep_customer_state_isolated():
    graph = create_graph()
    start_flow(graph, "C0010", "thread-a")
    start_flow(graph, "C0020", "thread-b")

    state_a = graph.get_state(thread_config("thread-a")).values
    state_b = graph.get_state(thread_config("thread-b")).values
    assert state_a["customer_id"] == "C0010"
    assert state_b["customer_id"] == "C0020"
    assert state_a["customer_info"]["name"] != state_b["customer_info"]["name"]


def test_unknown_customer_has_readable_error():
    graph = create_graph()
    with pytest.raises(ValueError, match="客户不存在"):
        start_flow(graph, "UNKNOWN", "unknown-customer")
