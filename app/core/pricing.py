"""
Core Pricing Engine for New Quetta Surgical and Medicine Distribution (NQS POS v2.0)
Handles Trade Price (TP = MRP - 15% or MRP when sold at MRP) calculations and variable customer tier / custom discounts.
"""

def calculate_tp(mrp: float, has_tp: bool = True) -> float:
    """
    Trade Price (TP) Rule:
    - If has_tp is True: automatically calculated as MRP - 15%.
    - If has_tp is False (sold at MRP): returns MRP directly.
    """
    if mrp is None or mrp < 0:
        return 0.0
    if has_tp:
        return round(float(mrp) * 0.85, 2)
    return round(float(mrp), 2)


def calculate_final_rate(tp: float, discount_percent: float) -> float:
    """
    Applies the selected discount percentage directly to the Trade Price (or MRP if sold at MRP).
    """
    if tp is None or tp < 0:
        return 0.0
    disc = max(0.0, min(100.0, float(discount_percent or 0.0)))
    return round(float(tp) * (1.0 - (disc / 100.0)), 2)


def calculate_line_total(final_rate: float, quantity: int) -> float:
    """
    Calculates total for a single invoice line item.
    """
    qty = max(0, int(quantity or 0))
    return round(float(final_rate) * qty, 2)


def compute_cart_summary(items: list) -> dict:
    """
    Computes total breakdown for a cart list of items.
    Each item dict format:
      {
        'mrp': float,
        'has_tp': bool,
        'tp': float,
        'discount_percent': float,
        'final_rate': float,
        'quantity': int,
        'total': float
      }
    Returns:
      {
        'subtotal': float (Sum of base rate/TP * quantity),
        'discount_amount': float (Total discount saved across items),
        'grand_total': float (Final collectable revenue)
      }
    """
    subtotal = 0.0
    discount_amount = 0.0
    grand_total = 0.0

    for item in items:
        has_tp = bool(item.get('has_tp', True))
        mrp = float(item.get('mrp', 0.0))
        tp = item.get('tp')
        if tp is None:
            tp = calculate_tp(mrp, has_tp=has_tp)
        else:
            tp = float(tp)

        disc_pct = float(item.get('discount_percent', 0.0))
        final_rate = item.get('final_rate')
        if final_rate is None:
            final_rate = calculate_final_rate(tp, disc_pct)
        else:
            final_rate = float(final_rate)

        qty = int(item.get('quantity', 1))

        base_tp_total = tp * qty
        line_total = item.get('total')
        if line_total is None:
            line_total = calculate_line_total(final_rate, qty)
        else:
            line_total = float(line_total)

        subtotal += base_tp_total
        grand_total += line_total
        discount_amount += (base_tp_total - line_total)

    return {
        'subtotal': round(subtotal, 2),
        'discount_amount': round(max(0.0, discount_amount), 2),
        'grand_total': round(grand_total, 2)
    }
