import logging
from typing import Dict, List, Tuple
from cache.semantic_cache import store_semantic_cache

logger = logging.getLogger("alfie-faq-prewarmer")

NICHE_FAQS: Dict[str, List[Tuple[str, str]]] = {
    "legal_intake": [
        (
            "What are your office hours?",
            "Our office is open Monday through Friday from 9:00 AM to 6:00 PM Eastern. However, our 24/7 intake team is always available for urgent legal consultations.",
        ),
        (
            "Do you offer free consultations?",
            "Yes, we provide a 100% free, confidential initial consultation to review your case and outline your legal options.",
        ),
        (
            "What practice areas do you handle?",
            "Our attorneys specialize in personal injury, motor vehicle accidents, wrongful death, workplace injury, and civil litigation.",
        ),
        (
            "How much do you charge for personal injury cases?",
            "We operate on a contingency fee basis. That means you pay zero legal fees unless we successfully win or settle your case.",
        ),
        (
            "Can I schedule an appointment with an attorney?",
            "I would be glad to help schedule a consultation. Could you share your preferred day, time, and the best callback number?",
        ),
    ],
    "real_estate": [
        (
            "What properties do you currently have available?",
            "We have a curated collection of luxury villas, penthouses, and modern apartments. Are you interested in purchasing or leasing?",
        ),
        (
            "Can I schedule a private property viewing?",
            "Certainly! I can schedule an in-person or virtual walkthrough for you. Which property and date would you prefer?",
        ),
        (
            "What are the typical closing costs or deposit requirements?",
            "For purchases, standard earnest deposits range between 5% and 10%, with closing timelines around 30 days. For rentals, standard security deposits apply.",
        ),
        (
            "Do you assist international buyers?",
            "Yes, our advisory team specializes in international buyer representation, currency transfers, and cross-border property transactions.",
        ),
    ],
    "car_rental": [
        (
            "What luxury and exotic vehicles are in your fleet?",
            "Our fleet includes the latest Range Rover, Cadillac Escalade, Lamborghini Urus, Ferrari F8, Porsche 911, and Mercedes G-Wagon.",
        ),
        (
            "What are the age and driver license requirements?",
            "Drivers must be at least 21 years old (25 for high-performance exotics), with a valid government driver's license and comprehensive insurance coverage.",
        ),
        (
            "Do you deliver the vehicle to airports or private residences?",
            "Yes, we provide VIP white-glove delivery and pickup directly to international airports, private FBOs, and luxury hotels.",
        ),
        (
            "What is your security deposit policy?",
            "A refundable security deposit is authorized on your credit card at dispatch and released upon vehicle return inspection.",
        ),
    ],
    "medical_reception": [
        (
            "What are your clinic operating hours?",
            "Our clinic is open Monday through Friday from 8:00 AM to 6:00 PM, and Saturdays from 9:00 AM to 2:00 PM.",
        ),
        (
            "Do you accept my medical insurance?",
            "We accept major insurance carriers including Blue Cross, Aetna, Cigna, UnitedHealthcare, and Medicare. We can verify your specific network benefits during check-in.",
        ),
        (
            "How can I book or reschedule an appointment?",
            "I can book your appointment right now. Would you like a morning or afternoon slot, and is this for a general exam or a specialist consultation?",
        ),
        (
            "What should I bring for my first visit?",
            "Please bring a valid photo ID, your insurance card, and a list of any current medications you are taking.",
        ),
    ],
    "hospitality": [
        (
            "What are the hotel check-in and check-out times?",
            "Standard check-in begins at 3:00 PM and check-out is at 11:00 AM. Early check-in or late check-out can be requested upon availability.",
        ),
        (
            "Is breakfast included with room reservations?",
            "Yes, all deluxe suites and club room reservations include complimentary gourmet breakfast buffet served daily from 6:30 AM to 10:30 AM.",
        ),
        (
            "Do you have valet parking and electric vehicle charging?",
            "We offer 24-hour valet parking with complimentary high-speed EV charging stations for all registered guests.",
        ),
        (
            "What amenities and wellness facilities are available?",
            "Our guests enjoy access to a heated rooftop pool, 24/7 fitness center, full-service spa, and executive business lounge.",
        ),
    ],
    "demo": [
        (
            "What is A.L.F.I.E and how does it work?",
            "A.L.F.I.E is an autonomous voice AI receptionist engine engineered for enterprise workflows. It handles inbound calls, qualifies leads, checks schedules, and routes calls with human-grade latency under 400ms.",
        ),
        (
            "Can A.L.F.I.E transfer callers to live human staff?",
            "Yes! A.L.F.I.E performs warm and blind SIP transfers with zero downtime, passing complete call transcripts and caller notes directly to your staff's phone or CRM.",
        ),
        (
            "How does A.L.F.I.E integrate with our existing CRM and calendar?",
            "A.L.F.I.E connects natively to Google Calendar, Cal.com, Twenty CRM, Salesforce, HubSpot, and custom webhooks via n8n automation pipelines.",
        ),
    ],
}


async def prewarm_niche_faqs(tenant_id: str = "demo-tenant", niche: str = "demo"):
    """
    Pre-warms the semantic cache for a specific tenant and niche.
    """
    faqs = NICHE_FAQS.get(niche) or NICHE_FAQS.get("demo", [])
    count = 0
    for prompt, response in faqs:
        await store_semantic_cache(
            prompt=prompt,
            response=response,
            tenant_id=tenant_id,
            niche=niche,
        )
        count += 1
    logger.info(
        f"Pre-warmed {count} semantic FAQ responses for niche: '{niche}' (Tenant: {tenant_id})"
    )
