def convert_to_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return float(value.replace(",", "."))
