from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    CARD = "card"
    BLIK = "blik"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"

class CharityGoal(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    target_amount: float
    collected_amount: float = 0

class Organization(BaseModel):
    id: str = "misjonarze-tarnow"
    name: str = "Misjonarze Parafia Świętej Rodziny"
    description: str = "Misjonarze świętego Wincentego a Paulo"
    location: str = "Tarnów"
    contact_phone: str = "790 525 400"
    contact_email: str = "kontakt@misjonarze-tarnow.pl"
    website: str = "https://misjonarze-tarnow.pl"
    logo_url: str = "/assets/mist_male_logo.png"
    primary_color: str = "#4B6A9B"
    secondary_color: str = "#2C4770"
    goals: List[CharityGoal]

class PaymentRequest(BaseModel):
    goal_id: str
    amount: float = Field(..., gt=0)
    donor_name: Optional[str] = None
    donor_email: Optional[EmailStr] = None
    message: Optional[str] = None
    payment_method: Optional[PaymentMethod] = PaymentMethod.CARD

class Payment(BaseModel):
    id: str
    goal_id: str
    amount: float
    status: PaymentStatus = PaymentStatus.PENDING
    payment_method: PaymentMethod
    donor_name: Optional[str] = None
    donor_email: Optional[EmailStr] = None
    message: Optional[str] = None
    fiserv_transaction_id: Optional[str] = None
    fiserv_checkout_id: Optional[str] = None
    payment_url: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WebhookPayload(BaseModel):
    transaction_id: str
    order_id: str
    status: str
    amount: float
    currency: str
    timestamp: str