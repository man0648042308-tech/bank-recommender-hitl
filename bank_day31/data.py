"""教学用客户与产品数据；不包含真实个人信息。"""

CUSTOMERS = {
    "C0010": {
        "customer_id": "C0010",
        "name": "张三",
        "age": 36,
        "monthly_income": 25_000,
        "investment_amount": 50_000,
        "risk_tolerance": "稳健型",
        "preferred_categories": ["债券基金", "理财产品"],
    },
    "C0020": {
        "customer_id": "C0020",
        "name": "李四",
        "age": 61,
        "monthly_income": 8_000,
        "investment_amount": 5_000,
        "risk_tolerance": "保守型",
        "preferred_categories": ["定期存款", "货币基金"],
    },
}

PRODUCTS = [
    {
        "product_id": "P001",
        "name": "安心存定期存款",
        "category": "定期存款",
        "risk_level": "保守型",
        "min_investment": 1_000,
    },
    {
        "product_id": "P002",
        "name": "稳健债券基金",
        "category": "债券基金",
        "risk_level": "稳健型",
        "min_investment": 1_000,
    },
    {
        "product_id": "P003",
        "name": "天天利货币基金",
        "category": "货币基金",
        "risk_level": "保守型",
        "min_investment": 0.01,
    },
    {
        "product_id": "P004",
        "name": "稳盈理财产品",
        "category": "理财产品",
        "risk_level": "稳健型",
        "min_investment": 10_000,
    },
    {
        "product_id": "P005",
        "name": "成长混合基金",
        "category": "混合基金",
        "risk_level": "平衡型",
        "min_investment": 1_000,
    },
    {
        "product_id": "P006",
        "name": "高门槛养老保险",
        "category": "保险",
        "risk_level": "稳健型",
        "min_investment": 100_000,
    },
]

