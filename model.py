from __future__ import annotations


def clamp(value: float, lo: int, hi: int) -> int:
    return int(max(lo, min(hi, round(value))))


def utilization_impact(utilization: float) -> int:
    if utilization <= 10:
        return 22
    if utilization <= 30:
        return 10
    if utilization <= 50:
        return -8
    if utilization <= 75:
        return -26
    return -45


def payment_impact(on_time: float) -> int:
    if on_time >= 99.5:
        return 24
    if on_time >= 98:
        return 12
    if on_time >= 96:
        return 2
    if on_time >= 94:
        return -16
    if on_time >= 90:
        return -34
    return -60


def age_impact(age_years: float) -> int:
    if age_years >= 15:
        return 16
    if age_years >= 8:
        return 9
    if age_years >= 3:
        return 2
    return -10


def get_tips(inputs: dict, factors: list[dict]) -> list[str]:
    tips: list[str] = []

    if inputs["utilization_percent"] > 30:
        tips.append("Lower card utilization below 30% (below 10% is even better).")
    if inputs["on_time_payments_percent"] < 99:
        tips.append("Improve payment consistency with autopay and reminders.")
    if inputs["hard_inquiries_last_12mo"] > 2 or inputs["new_accounts_last_12mo"] > 1:
        tips.append("Avoid opening new credit lines for the next 6-12 months.")
    if inputs["derogatory_marks"] >= 1:
        tips.append("Address derogatory items and dispute inaccurate marks quickly.")
    if inputs["age_oldest_account_years"] < 5:
        tips.append("Keep older accounts open to strengthen average account age.")

    if len(tips) >= 3:
        return tips[:3]

    # Fill with the largest negative factors if not enough direct tips.
    negatives = [f for f in factors if f["impact"] < 0]
    negatives.sort(key=lambda x: x["impact"])

    for factor in negatives:
        label = factor["factor"]
        if label == "Hard inquiries":
            candidate = "Limit hard credit pulls until score stabilizes."
        elif label == "New accounts":
            candidate = "Pause new accounts so recent-account drag can fade."
        elif label == "Derogatory marks":
            candidate = "Build clean recent history to reduce derogatory mark impact over time."
        else:
            candidate = f"Improve {label.lower()} to support score growth."
        if candidate not in tips:
            tips.append(candidate)
        if len(tips) == 3:
            break

    if not tips:
        tips = [
            "Keep utilization low and payments on time to preserve momentum.",
            "Review your credit reports regularly for accuracy.",
            "Use only the credit you need; stability helps scores."
        ]

    return tips[:3]


def calculate(inputs: dict) -> dict:
    current_score = float(inputs["current_score"])
    utilization_percent = float(inputs["utilization_percent"])
    on_time_payments_percent = float(inputs["on_time_payments_percent"])
    age_oldest_account_years = float(inputs["age_oldest_account_years"])
    hard_inquiries_last_12mo = int(inputs["hard_inquiries_last_12mo"])
    new_accounts_last_12mo = int(inputs["new_accounts_last_12mo"])
    derogatory_marks = int(inputs["derogatory_marks"])

    util = utilization_impact(utilization_percent)
    payment = payment_impact(on_time_payments_percent)
    age = age_impact(age_oldest_account_years)
    inquiries = max(-20, -4 * hard_inquiries_last_12mo)
    new_accounts = max(-25, -5 * new_accounts_last_12mo)
    derog = 0 if derogatory_marks == 0 else (-42 if derogatory_marks == 1 else -82)

    factors = [
        {
            "factor": "Utilization",
            "impact": util,
            "effect": "helps" if util >= 0 else "hurts"
        },
        {
            "factor": "On-time payment history",
            "impact": payment,
            "effect": "helps" if payment >= 0 else "hurts"
        },
        {
            "factor": "Oldest account age",
            "impact": age,
            "effect": "helps" if age >= 0 else "hurts"
        },
        {
            "factor": "Hard inquiries",
            "impact": inquiries,
            "effect": "helps" if inquiries >= 0 else "hurts"
        },
        {
            "factor": "New accounts",
            "impact": new_accounts,
            "effect": "helps" if new_accounts >= 0 else "hurts"
        },
        {
            "factor": "Derogatory marks",
            "impact": derog,
            "effect": "helps" if derog >= 0 else "hurts"
        }
    ]

    mid = clamp(current_score + sum(f["impact"] for f in factors), 300, 850)
    uncertainty = 18 + min(16, hard_inquiries_last_12mo * 2 + new_accounts_last_12mo)
    low = clamp(mid - uncertainty, 300, 850)
    high = clamp(mid + uncertainty, 300, 850)

    tips = get_tips(inputs, factors)

    return {
        "estimated_new_score_range": {
            "low": low,
            "mid": mid,
            "high": high
        },
        "factor_breakdown": factors,
        "tips": tips,
        "note": "This is an educational estimate only and not a credit bureau score."
    }
