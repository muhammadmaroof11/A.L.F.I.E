from prompts.real_estate import REAL_ESTATE_PROMPT
from prompts.car_rental import CAR_RENTAL_PROMPT
from prompts.demo import DEMO_SALES_PROMPT
from prompts.legal import LEGAL_INTAKE_PROMPT
from prompts.medical import MEDICAL_RECEPTION_PROMPT
from prompts.hospitality import HOSPITALITY_CONCIERGE_PROMPT
from prompts.luxury_transport import LUXURY_TRANSPORT_PROMPT

# Registry maps niche keys and all known frontend/database aliases to the system prompt string.
PROMPT_REGISTRY: dict = {
    # Real Estate aliases
    "real_estate": REAL_ESTATE_PROMPT,
    "realestate": REAL_ESTATE_PROMPT,
    "realty": REAL_ESTATE_PROMPT,
    "property": REAL_ESTATE_PROMPT,

    # Car Rental / Luxury Transport aliases
    "car_rental": CAR_RENTAL_PROMPT,
    "carrental": CAR_RENTAL_PROMPT,
    "luxury_transfer": LUXURY_TRANSPORT_PROMPT,
    "luxury_transport": LUXURY_TRANSPORT_PROMPT,
    "fleet": LUXURY_TRANSPORT_PROMPT,
    "chauffeur": LUXURY_TRANSPORT_PROMPT,

    # Legal Intake aliases
    "legal": LEGAL_INTAKE_PROMPT,
    "legal_intake": LEGAL_INTAKE_PROMPT,
    "personal_injury": LEGAL_INTAKE_PROMPT,
    "law_firm": LEGAL_INTAKE_PROMPT,
    "law_firms": LEGAL_INTAKE_PROMPT,
    "lawyer": LEGAL_INTAKE_PROMPT,

    # Medical / Clinic aliases
    "clinic": MEDICAL_RECEPTION_PROMPT,
    "clinics": MEDICAL_RECEPTION_PROMPT,
    "medical": MEDICAL_RECEPTION_PROMPT,
    "medical_reception": MEDICAL_RECEPTION_PROMPT,
    "dental": MEDICAL_RECEPTION_PROMPT,
    "dental_clinic": MEDICAL_RECEPTION_PROMPT,
    "healthcare": MEDICAL_RECEPTION_PROMPT,

    # Hospitality aliases
    "hospitality": HOSPITALITY_CONCIERGE_PROMPT,
    "hospitality_concierge": HOSPITALITY_CONCIERGE_PROMPT,
    "restaurant": HOSPITALITY_CONCIERGE_PROMPT,
    "dining": HOSPITALITY_CONCIERGE_PROMPT,

    # Showcase & Sales Demo aliases
    "demo": DEMO_SALES_PROMPT,
    "sales_demo": DEMO_SALES_PROMPT,
    "sales": DEMO_SALES_PROMPT,
    "general": DEMO_SALES_PROMPT,
}


def get_prompt_for_niche(niche: str) -> str:
    """Safely retrieves vertical system prompt with fallback to demo prompt."""
    if not niche:
        return DEMO_SALES_PROMPT
    key = niche.strip().lower().replace("-", "_")
    return PROMPT_REGISTRY.get(key, DEMO_SALES_PROMPT)

