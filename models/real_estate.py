from typing import List, Optional
from pydantic import Field
from datetime import datetime
from .core import MongoBaseModel


class PropertyAmenities(MongoBaseModel):
    parking: int = 0
    garden: bool = False
    servant_quarter: bool = False
    central_heating: bool = False
    security: str = "none"
    gas: bool = False
    electricity_backup: str = "none"


class Property(MongoBaseModel):
    title: str
    description: str
    city: str
    area: str
    neighborhood_id: Optional[str] = None
    property_type: str  # house, apartment, plot
    bedrooms: int = 0
    bathrooms: int = 0
    area_sqft: float
    area_marla: float
    price: float
    currency: str = "PKR"
    price_per_sqft: Optional[float] = None
    listing_url: Optional[str] = None
    images: List[str] = []
    amenities: PropertyAmenities = Field(default_factory=PropertyAmenities)
    status: str = "available"
    featured: bool = False
    agent_notes: Optional[str] = None
    listed_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class REBooking(MongoBaseModel):
    call_id: Optional[str] = None
    property_id: str
    lead_id: Optional[str] = None
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    viewing_date: datetime
    time_slot: str
    assigned_agent: Optional[str] = None
    status: str = "scheduled"
    notes: Optional[str] = None
    admin_notified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
