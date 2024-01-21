def convert_to_float(value):
    try:
        return float(value)
    except ValueError:
        return float(value.replace(",", "."))
