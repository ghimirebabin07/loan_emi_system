from datetime import date
from dateutil.relativedelta import relativedelta


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    r = (annual_rate / 12) / 100
    if r == 0:
        return round(principal / tenure_months, 2)
    emi = principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
    return round(emi, 2)


def generate_schedule(start_date: date, emi_amount: float, tenure_months: int):
    schedule = []
    for i in range(1, tenure_months + 1):
        due = start_date + relativedelta(months=i)
        schedule.append((due, emi_amount))
    return schedule
