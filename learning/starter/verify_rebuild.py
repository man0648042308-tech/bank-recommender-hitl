"""独立复现验收器；默认验证同目录hitl_starter.py。"""

import importlib.util
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("rebuild_target", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def interrupt_kind(result):
    interruptions = result.get("__interrupt__", ())
    return interruptions[0].value["kind"] if interruptions else None


def main() -> None:
    target_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("hitl_starter.py")
    target = load_module(target_path)
    graph = target.create_graph()
    thread_id = "closed-book-check"

    result = target.start_flow(graph, "C0010", thread_id)
    assert interrupt_kind(result) == "human_review", "首次必须暂停在人工复核"
    assert result["recommendations"], "推荐列表不能为空"

    result = target.resume_flow(graph, thread_id, "批准")
    assert interrupt_kind(result) == "customer_confirmation", "批准后必须暂停在客户确认"

    result = target.resume_flow(graph, thread_id, "y")
    assert result["execution_status"] == "模拟执行成功", "客户接受后必须模拟执行成功"

    decline_graph = target.create_graph()
    decline_thread = "closed-book-decline"
    target.start_flow(decline_graph, "C0010", decline_thread)
    target.resume_flow(decline_graph, decline_thread, "批准")
    declined = target.resume_flow(decline_graph, decline_thread, "n")
    assert declined["execution_status"] == "客户拒绝", "客户拒绝时不得办理产品"
    assert "executed_product_id" not in declined, "客户拒绝时不得生成办理产品ID"

    retry_graph = target.create_graph()
    retry_thread = "closed-book-retry"
    first = target.start_flow(retry_graph, "C0010", retry_thread)
    first_ids = [item["product_id"] for item in first["recommendations"]]
    second = target.resume_flow(retry_graph, retry_thread, "拒绝, 请更换产品")
    second_ids = [item["product_id"] for item in second["recommendations"]]
    assert interrupt_kind(second) == "human_review", "第一次拒绝后必须重新推荐并再次暂停"
    assert first_ids != second_ids, "复核拒绝后推荐结果必须发生变化"

    stopped = target.resume_flow(retry_graph, retry_thread, "拒绝, 仍不合适")
    assert interrupt_kind(stopped) is None, "达到拒绝上限后流程必须结束"
    assert "重试次数已用尽" in stopped["execution_status"], "终止原因必须明确"
    assert "executed_product_id" not in stopped, "复核终止时不得办理产品"

    print("闭卷验收全部通过：成功、客户拒绝、复核重试和连续拒绝终止均正确。")


if __name__ == "__main__":
    main()
