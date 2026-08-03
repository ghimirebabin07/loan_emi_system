from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

class CustomerCreate(BaseModel):
    name: str
    phone: str
    address: Optional[str] = None

class CustomerOut(CustomerCreate):
    id: int

class LoanCreate(BaseModel):
    customer_id: int
    officer_id: int
    amount: float = Field(gt=0)
    interest_rate: float = Field(gt=0)
    tenure_months: int = Field(gt=0)

class EMIOut(BaseModel):
    id: int
    due_date: date
    emi_amount: float
    status: str

class LoanOut(BaseModel):
    id: int
    amount: float
    interest_rate: float
    tenure_months: int
    start_date: date
    status: str
    emis: List[EMIOut] = Field(default_factory=list)


class LoanListOut(BaseModel):
    id: int
    customer_name: str
    officer_name: str | None = None
    amount: float
    status: str
    start_date: date


class PaymentCreate(BaseModel):
    emi_id: int
    amount_paid: float = Field(gt=0)
    payment_mode: str
    paid_date: Optional[date] = None


class OfficerCreate(BaseModel):
    name: str
    branch: Optional[str] = None


class OfficerOut(OfficerCreate):
    id: int