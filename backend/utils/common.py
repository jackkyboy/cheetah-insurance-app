# utils/common.py
from decimal import Decimal

def convert_decimal(data):
    """
    Convert Decimal objects to float in the given data.

    Args:
        data (list or dict): Data structure containing Decimal values.

    Returns:
        list or dict: Data with Decimal values converted to float.
    """
    if isinstance(data, list):
        return [convert_decimal(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_decimal(value) for key, value in data.items()}
    elif isinstance(data, Decimal):
        return float(data)
    else:
        return data
