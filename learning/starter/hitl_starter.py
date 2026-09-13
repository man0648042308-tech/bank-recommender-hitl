"""Day31闭卷骨架：完成Day29双条件筛选后再开始。"""

from typing import Any, TypedDict

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


def profile_analysis(state: FullBankState) -> dict[str, Any]:
    # TODO：按照customer_id读取客户并返回customer_info。
    raise NotImplementedError


def initial_recommendation(state: FullBankState) -> dict[str, Any]:
    # TODO：调用eligible_products并返回最多三个recommendations。
    raise NotImplementedError


def human_review(state: FullBankState) -> dict[str, Any]:
    # TODO：调用interrupt，解析批准/拒绝，更新复核次数。
    # 拒绝时还要排除当前首选产品，以便下一次推荐发生变化。
    raise NotImplementedError


def route_after_review(state: FullBankState) -> str:
    # TODO：批准→confirm；第一次拒绝→retry；第二次拒绝→stop。
    raise NotImplementedError


def customer_confirmation(state: FullBankState) -> dict[str, Any]:
    # TODO：调用interrupt，把人工输入转换为customer_accept。
    raise NotImplementedError


def execute_operation(state: FullBankState) -> dict[str, Any]:
    # TODO：接受时模拟成功，拒绝时记录客户拒绝。
    raise NotImplementedError


def create_graph():
    # TODO：添加五个节点、边、条件边，并使用MemorySaver编译。
    raise NotImplementedError


def start_flow(graph, customer_id: str, thread_id: str):
    # TODO：使用graph.invoke启动流程，并初始化retry_count和排除列表。
    raise NotImplementedError


def resume_flow(graph, thread_id: str, answer: str):
    # TODO：使用Command(resume=answer)恢复同一thread。
    raise NotImplementedError
