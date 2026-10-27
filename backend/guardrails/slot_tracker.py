"""
Deterministic Slot-Filling Guardrails for Regulated Vertical Niches.
Tracks mandatory and optional intake slots across Legal, Healthcare, Real Estate,
Luxury Fleet, Hospitality, and General inquiries to ensure AI captures necessary data.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("alfie.guardrails.slots")


# --- Pydantic Slot Schemas per Vertical ---

class LegalIntakeSlots(BaseModel):
    caller_name: Optional[str] = Field(default=None, description="Full name of the prospective claimant")
    caller_phone: Optional[str] = Field(default=None, description="Contact phone number")
    incident_date: Optional[str] = Field(default=None, description="Date or timeframe when injury/accident occurred")
    injury_severity: Optional[str] = Field(default=None, description="Type or severity of injury/damages sustained")
    has_attorney: Optional[str] = Field(default=None, description="Whether caller is already represented by counsel")

    @classmethod
    def mandatory_fields(cls) -> List[str]:
        return ["caller_name", "caller_phone", "incident_date", "injury_severity", "has_attorney"]


class MedicalClinicSlots(BaseModel):
    patient_name: Optional[str] = Field(default=None, description="Patient's full name")
    caller_phone: Optional[str] = Field(default=None, description="Patient callback phone number")
    reason_for_visit: Optional[str] = Field(default=None, description="Chief medical or dental complaint / appointment reason")
    insurance_provider: Optional[str] = Field(default=None, description="Health insurance provider or self-pay status")
    preferred_time: Optional[str] = Field(default=None, description="Requested appointment day or time slot")

    @classmethod
    def mandatory_fields(cls) -> List[str]:
        return ["patient_name", "caller_phone", "reason_for_visit", "insurance_provider", "preferred_time"]


class RealEstateSlots(BaseModel):
    client_name: Optional[str] = Field(default=None, description="Buyer or seller full name")
    caller_phone: Optional[str] = Field(default=None, description="Client contact phone")
    property_type_or_address: Optional[str] = Field(default=None, description="Target address, neighborhood, or property type")
    budget_range: Optional[str] = Field(default=None, description="Price budget or target valuation")
    timeframe: Optional[str] = Field(default=None, description="Expected purchase or showing timeframe")

    @classmethod
    def mandatory_fields(cls) -> List[str]:
        return ["client_name", "caller_phone", "property_type_or_address", "budget_range", "timeframe"]


class LuxuryTransportSlots(BaseModel):
    passenger_name: Optional[str] = Field(default=None, description="Passenger or booking contact name")
    caller_phone: Optional[str] = Field(default=None, description="Passenger contact phone")
    pickup_datetime: Optional[str] = Field(default=None, description="Requested pickup date and time")
    pickup_location: Optional[str] = Field(default=None, description="Origin address or airport terminal")
    dropoff_location: Optional[str] = Field(default=None, description="Destination address or airport")
    vehicle_class: Optional[str] = Field(default=None, description="Requested vehicle type: Sedan, SUV, Sprinter, Chauffeur")

    @classmethod
    def mandatory_fields(cls) -> List[str]:
        return ["passenger_name", "caller_phone", "pickup_datetime", "pickup_location", "dropoff_location", "vehicle_class"]


class HospitalitySlots(BaseModel):
    guest_name: Optional[str] = Field(default=None, description="Lead reservation guest name")
    caller_phone: Optional[str] = Field(default=None, description="Guest contact phone")
    party_size: Optional[str] = Field(default=None, description="Number of guests in dining party")
    reservation_datetime: Optional[str] = Field(default=None, description="Desired dining date and time")
    dietary_notes: Optional[str] = Field(default=None, description="Allergies, dietary restrictions, or VIP occasion")

    @classmethod
    def mandatory_fields(cls) -> List[str]:
        return ["guest_name", "caller_phone", "party_size", "reservation_datetime", "dietary_notes"]


class GeneralInquirySlots(BaseModel):
    caller_name: Optional[str] = Field(default=None, description="Caller name")
    caller_phone: Optional[str] = Field(default=None, description="Contact phone")
    inquiry_topic: Optional[str] = Field(default=None, description="Primary reason for call")
    followup_preferred: Optional[str] = Field(default=None, description="Preferred callback or contact method")

    @classmethod
    def mandatory_fields(cls) -> List[str]:
        return ["caller_name", "caller_phone", "inquiry_topic"]


# Mapping of normalized niches to slot classes
NICHE_SLOT_SCHEMAS = {
    "legal": LegalIntakeSlots,
    "clinic": MedicalClinicSlots,
    "medical": MedicalClinicSlots,
    "dental": MedicalClinicSlots,
    "realestate": RealEstateSlots,
    "realty": RealEstateSlots,
    "carrental": LuxuryTransportSlots,
    "transport": LuxuryTransportSlots,
    "fleet": LuxuryTransportSlots,
    "hospitality": HospitalitySlots,
    "dining": HospitalitySlots,
    "restaurant": HospitalitySlots,
    "general": GeneralInquirySlots,
}


class SlotTracker:
    """
    Maintains active slot-filling state for a voice session.
    Detects extracted fields, measures completeness percentage, and produces
    deterministic directives to steer the LLM towards missing mandatory slots.
    """

    def __init__(self, niche: str = "general", initial_phone: Optional[str] = None):
        self.raw_niche = niche
        self.niche = self._normalize_niche(niche)
        self.schema_cls = NICHE_SLOT_SCHEMAS.get(self.niche, GeneralInquirySlots)
        self.slots: Dict[str, Any] = {}
        self.mandatory_keys: List[str] = self.schema_cls.mandatory_fields()

        # Seed initial caller phone if provided via SIP/telemetry
        if initial_phone:
            phone_key = "caller_phone"
            self.slots[phone_key] = initial_phone

    def _normalize_niche(self, niche: str) -> str:
        clean = (niche or "general").lower().replace(" ", "").replace("_", "").replace("-", "")
        for k in NICHE_SLOT_SCHEMAS.keys():
            if k in clean:
                return k
        return "general"

    def set_slot(self, key: str, value: Any):
        if value:
            self.slots[key] = str(value).strip()

    def get_slot(self, key: str) -> Optional[str]:
        return self.slots.get(key)

    def is_slot_filled(self, key: str) -> bool:
        val = self.slots.get(key)
        return val is not None and len(str(val).strip()) > 0

    def get_missing_mandatory_slots(self) -> List[str]:
        return [k for k in self.mandatory_keys if not self.is_slot_filled(k)]

    def is_complete(self) -> bool:
        return len(self.get_missing_mandatory_slots()) == 0

    def get_completion_percentage(self) -> int:
        if not self.mandatory_keys:
            return 100
        filled = sum(1 for k in self.mandatory_keys if self.is_slot_filled(k))
        return int((filled / len(self.mandatory_keys)) * 100)

    def update_from_text(self, text: str, role: str = "user"):
        """
        Extracts common intake entity patterns from user speech turns.
        """
        if not text:
            return

        text_lower = text.lower()

        # 1. Phone number extraction
        phone_match = re.search(r'(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone_match and not self.is_slot_filled("caller_phone"):
            self.slots["caller_phone"] = phone_match.group(0).strip()

        # 2. Name extraction ("my name is...", "this is...", "I'm...")
        name_match = re.search(
            r'(?:my name is|this is|i am|i\'m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            text,
            re.IGNORECASE,
        )
        if name_match:
            name_val = name_match.group(1).strip()
            for key in ["caller_name", "patient_name", "client_name", "passenger_name", "guest_name"]:
                if key in self.mandatory_keys and not self.is_slot_filled(key):
                    self.slots[key] = name_val

        # 3. Domain-specific keyword heuristics
        if self.niche == "legal":
            # Attorney status
            if any(p in text_lower for p in ["do not have an attorney", "no lawyer", "haven't hired anyone", "no attorney"]):
                self.slots["has_attorney"] = "No"
            elif any(p in text_lower for p in ["i have a lawyer", "already have an attorney", "represented by"]):
                self.slots["has_attorney"] = "Yes"

            # Incident date
            date_match = re.search(r'\b(?:yesterday|last week|last month|today|\d{1,2}\/\d{1,2}(?:\/\d{2,4})?|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,2}(?:st|nd|rd|th)?)\b', text_lower)
            if date_match and not self.is_slot_filled("incident_date"):
                self.slots["incident_date"] = date_match.group(0)

            # Injury severity
            if any(w in text_lower for w in ["hospital", "surgery", "broken", "fracture", "pain", "whiplash", "concussion", "rear-ended", "car accident", "slip and fall"]):
                if not self.is_slot_filled("injury_severity"):
                    self.slots["injury_severity"] = text.strip()

        elif self.niche in ["clinic", "medical", "dental"]:
            # Insurance
            if any(ins in text_lower for ins in ["blue cross", "bcbs", "aetna", "cigna", "united", "medicare", "medicaid", "delta dental", "self pay", "cash"]):
                if not self.is_slot_filled("insurance_provider"):
                    self.slots["insurance_provider"] = text.strip()

            # Chief complaint / Reason for visit
            if any(r in text_lower for r in ["cleaning", "toothache", "mri", "consultation", "checkup", "back pain", "cavity", "implant", "exam"]):
                if not self.is_slot_filled("reason_for_visit"):
                    self.slots["reason_for_visit"] = text.strip()

            # Time preference
            if any(t in text_lower for t in ["morning", "afternoon", "monday", "tuesday", "wednesday", "thursday", "friday", "tomorrow", "next week", "pm", "am"]):
                if not self.is_slot_filled("preferred_time"):
                    self.slots["preferred_time"] = text.strip()

        elif self.niche in ["hospitality", "dining", "restaurant"]:
            # Party size ("table for 4", "party of 2")
            party_match = re.search(r'(?:table for|party of|for)\s+(\d+|two|three|four|five|six|seven|eight|ten)', text_lower)
            if party_match and not self.is_slot_filled("party_size"):
                self.slots["party_size"] = party_match.group(1)

            # Dietary notes
            if any(d in text_lower for d in ["allergy", "allergic", "vegan", "vegetarian", "gluten", "birthday", "anniversary", "no restrictions"]):
                if not self.is_slot_filled("dietary_notes"):
                    self.slots["dietary_notes"] = text.strip()

        elif self.niche in ["carrental", "transport", "fleet"]:
            # Vehicle class
            if any(v in text_lower for v in ["escalade", "suv", "sedan", "sprinter", "limo", "maybach", "mercedes"]):
                if not self.is_slot_filled("vehicle_class"):
                    self.slots["vehicle_class"] = text.strip()

    def generate_guidance_prompt(self) -> Optional[str]:
        """
        Produces a concise prompt injection directing the LLM to collect
        the next missing mandatory intake slot.
        """
        missing = self.get_missing_mandatory_slots()
        if not missing:
            return None

        # Human-readable slot names
        readable_map = {
            "caller_name": "caller's full name",
            "patient_name": "patient's full name",
            "client_name": "client's full name",
            "passenger_name": "passenger's full name",
            "guest_name": "guest's full name",
            "caller_phone": "mobile callback phone number",
            "incident_date": "date/time of the incident",
            "injury_severity": "type and severity of injuries",
            "has_attorney": "whether they already have legal representation",
            "reason_for_visit": "primary reason for appointment / symptoms",
            "insurance_provider": "insurance provider or self-pay preference",
            "preferred_time": "preferred day or time for appointment",
            "property_type_or_address": "target property type or address",
            "budget_range": "budget or price target",
            "timeframe": "timeline for moving or viewing",
            "pickup_datetime": "pickup date and time",
            "pickup_location": "pickup location",
            "dropoff_location": "dropoff destination",
            "vehicle_class": "preferred vehicle class (Sedan, SUV, etc.)",
            "party_size": "number of guests in dining party",
            "reservation_datetime": "date and time for reservation",
            "dietary_notes": "any dietary restrictions or special occasion",
            "inquiry_topic": "primary question or inquiry topic",
        }

        missing_readable = [readable_map.get(m, m.replace("_", " ")) for m in missing]
        primary_missing = missing_readable[0]

        return (
            f"[DETERMINISTIC INTAKE DIRECTIVE]:\n"
            f"You are missing mandatory intake information: {', '.join(missing_readable)}.\n"
            f"Please prioritize politely asking the caller for their {primary_missing} "
            f"before confirming bookings or ending the call."
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "niche": self.niche,
            "completion_percentage": self.get_completion_percentage(),
            "is_complete": self.is_complete(),
            "missing_mandatory": self.get_missing_mandatory_slots(),
            "slots": self.slots,
        }


def get_slot_tracker_for_niche(niche: str, caller_phone: Optional[str] = None) -> SlotTracker:
    return SlotTracker(niche=niche, initial_phone=caller_phone)
