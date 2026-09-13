"""银行产品确定性适当性规则。"""

from typing import Any


RISK_ORDER = {
    "保守型": 1,
    "稳健型": 2,
    "平衡型": 3,
    "进取型": 4,
}


def eligible_products(
    customer: dict[str, Any],
    products: list[dict[str, Any]],
    excluded_product_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """返回风险不越级、金额足够且未被复核排除的产品。"""
    excluded = set(excluded_product_ids or [])
    customer_risk = RISK_ORDER[customer["risk_tolerance"]]
    amount = float(customer["investment_amount"])

    matched = []
    for product in products:
        risk_ok = RISK_ORDER[product["risk_level"]] <= customer_risk
        amount_ok = float(product["min_investment"]) <= amount
        not_excluded = product["product_id"] not in excluded
        if risk_ok and amount_ok and not_excluded:
            matched.append(dict(product))

    preferred = set(customer.get("preferred_categories", []))
    return sorted(
        matched,
        key=lambda product: (
            product["category"] not in preferred,
            product["product_id"],
        ),
    )

