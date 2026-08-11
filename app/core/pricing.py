"""
Core Pricing Engine for NQS POS v2.0
Handles Trade Price (TP = MRP - 15%) calculations and variable customer tier discounts.
"""

def calculate_tp(mrp: float) -> float:
    """
    Trade Price (TP) Rule: Automatically calculated as MRP - 15%.
    """
    if mrp is None or mrp < 0:
        return 0.0
    return round(float(mrp) * 0.85, 2)


def calculate_final_rate(tp: float, discount_percent: float) -> float:
    """
    Applies the selected discount percentage (0%, 4%, 7%, 12%) directly to the Trade Price (TP).
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
        'tp': float,
        'discount_percent': float,
        'final_rate': float,
        'quantity': int,
        'total': float
      }
    Returns:
      {
        'subtotal': float (Sum of base TP * quantity),
        'discount_amount': float (Total discount saved across items),
        'grand_total': float (Final collectable revenue)
      }
    """
    subtotal = 0.0
    discount_amount = 0.0
    grand_total = 0.0

    for item in items:
        tp = item.get('tp', calculate_tp(item.get('mrp', 0.0)))
        disc_pct = item.get('discount_percent', 0.0)
        final_rate = item.get('final_rate', calculate_final_rate(tp, disc_pct))
        qty = int(item.get('quantity', 1))

        base_tp_total = tp * qty
        line_total = item.get('total', calculate_line_total(final_rate, qty))

        subtotal += base_tp_total
        grand_total += line_total
        discount_amount += (base_tp_total - line_total)

    return {
        'subtotal': round(subtotal, 2),
        'discount_amount': round(max(0.0, discount_amount), 2),
        'grand_total': round(grand_total, 2)
    }
