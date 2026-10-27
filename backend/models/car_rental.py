from typing import Optional
from pydantic import Field
from datetime import datetime, timezone
from .core import MongoBaseModel


class Vehicle(MongoBaseModel):
    make: str
    model: str
    year: int
    category: str  # sedan, suv, economy, luxury
    license_plate: str
    color: str
    daily_rate: float
    weekly_rate: Optional[float] = None
    monthly_rate: Optional[float] = None
    currency: str = "PKR"
    location_id: Optional[str] = None
    fuel_type: str
    seats: int
    transmission: str
    status: str = "available"
    min_driver_age: int = 21
    deposit_amount: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CRReservation(MongoBaseModel):
    call_id: Optional[str] = None
    vehicle_id: str
    lead_id: Optional[str] = None
    confirmation_number: str
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    pickup_date: datetime
    return_date: datetime
    total_days: int
    base_rate: float
    total_cost: float
    currency: str = "PKR"
    status: str = "confirmed"
    admin_notified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
