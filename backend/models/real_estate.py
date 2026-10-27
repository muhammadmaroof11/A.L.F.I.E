from typing import List, Optional
from pydantic import Field
from datetime import datetime, timezone
from .core import MongoBaseModel


class PropertyAmenities(MongoBaseModel):
    parking: int = 0
    garden: bool = False
    servant_quarter: bool = False
    swimming_pool: bool = False
    furnished: bool = False
    gym: bool = False


class Property(MongoBaseModel):
    property_id: str
    title: str
    property_type: str  # apartment, villa, commercial, plot
    location: str
    city: str = "Dubai"
    bedrooms: int
    bathrooms: int
    area_sqft: float
    price_aed: float
    price_usd: Optional[float] = None
    price_per_sqft: Optional[float] = None
    listing_url: Optional[str] = None
    images: List[str] = []
    amenities: PropertyAmenities = Field(default_factory=PropertyAmenities)
    status: str = "available"
    featured: bool = False
    agent_notes: Optional[str] = None
    listed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
