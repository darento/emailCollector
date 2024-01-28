from collections import defaultdict


def convert_to_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return float(value.replace(",", "."))


def extract_expenses_per_month(all_items):
    expenses_per_month = defaultdict(float)
    for items, date in all_items:
        for item in items:
            year, month = date[:4], date[4:6]
            expenses_per_month[(year, month)] += item["total_price"]
    return expenses_per_month


def extract_expenses_per_item(all_items):
    expenses_per_item = defaultdict(float)
    for items, _ in all_items:
        for item in items:
            expenses_per_item[item["product"]] += item["total_price"]
    return expenses_per_item
