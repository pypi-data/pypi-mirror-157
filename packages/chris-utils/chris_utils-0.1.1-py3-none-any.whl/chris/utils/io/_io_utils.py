from typing import Dict


def print_map(score_map: Dict[str, float], asc: bool = False, line_format: str = "{}: {}\n") -> None:
    """ Print a map from names to numbers ordered by the number.

    Args:
        score_map: Dictionary from names to scores.
        asc: Whether the items should be printed in ascending order.
        line_format: The format string used when printint each item.
    """
    items = list(score_map.items())
    order_coef = 1 if asc else -1
    sorted_items = sorted(items, key=lambda x: order_coef * x[1])
    for key, value in sorted_items:
        line = line_format.format(key, value)
        print(line, end="")
