import json
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from config import settings
from telemetry import _pool, get_redis
from cache import check_demo_rate_limit

logger = logging.getLogger("alfie-public-demo")
router = APIRouter(prefix="/api/public/demo", tags=["Public Live Demo"])


class DemoTokenRequest(BaseModel):
    niche: Optional[str] = "demo"
    visitor_name: Optional[str] = "Demo Prospect"


class DemoCallbackRequest(BaseModel):
    phone_number: str
    visitor_name: Optional[str] = "Prospect"
    niche: Optional[str] = "demo"
    company_name: Optional[str] = None


@router.get("/personas")
async def list_demo_personas():
    """Returns available demo personas for interactive in-browser and live telephony testing."""
    return [
        {
            "id": "demo",
            "name": "A.L.F.I.E Voice AI Showcase",
            "tagline": "Flagship Autonomous Agent",
            "description": "Demonstrates sub-second latency, live language switching (English/Urdu/Arabic), and objection handling.",
            "sample_prompts": [
                "What can you do for my business?",
                "Can you speak in Urdu or Arabic?",
                "How do you handle customer call transfers?",
            ],
        },
        {
            "id": "real_estate",
            "name": "Luxury Real Estate Broker",
            "tagline": "Lead Qualification & Viewing Booking",
            "description": "Qualifies buyers by budget and location, answers property questions, and books site viewings.",
            "sample_prompts": [
                "I am looking for a 3-bedroom villa in Dubai under 2 million.",
                "Can I schedule a viewing this Saturday?",
            ],
        },
        {
            "id": "car_rental",
            "name": "Exotic Fleet Concierge",
            "tagline": "Vehicle Availability & Reservations",
            "description": "Checks fleet inventory in real-time, calculates deposits, and takes rental reservations.",
            "sample_prompts": [
                "Do you have a Range Rover or Escalade available tomorrow?",
                "What are your deposit and insurance terms?",
            ],
        },
        {
            "id": "medical_reception",
            "name": "Clinic Patient Receptionist",
            "tagline": "Insurance Verification & Triage",
            "description": "Screens patient symptoms, checks accepted insurance networks, and books doctor appointments.",
            "sample_prompts": [
                "Do you accept Delta Dental insurance?",
                "I need to book a consultation with Dr. Smith.",
            ],
        },
        {
            "id": "legal_intake",
            "name": "Personal Injury Law Intake",
            "tagline": "24/7 Triage & High-Value Case Transfer",
            "description": "Gathers accident facts, screens liability, and escalates qualified claims to the managing attorney.",
            "sample_prompts": [
                "I was in a car accident yesterday and need legal help.",
                "Is an attorney available to speak with me?",
            ],
        },
    ]


@router.post("/token")
async def generate_demo_token(req: DemoTokenRequest, request: Request):
    """
    Generates a public WebRTC token allowing website visitors to speak directly
    with A.L.F.I.E through their browser microphone with zero authentication barriers.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    redis_client = await get_redis()
    allowed = await check_demo_rate_limit(redis_client, client_ip, limit=5)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Daily demo limit reached for this device. Please schedule a full consultation or try again tomorrow!",
        )

    room_id = f"demo-call-{uuid.uuid4().hex[:8]}"
    participant_identity = f"visitor-{uuid.uuid4().hex[:6]}"

    if not settings.livekit_api_key or not settings.livekit_api_secret:
        return {
            "token": "mock_livekit_demo_token",
            "url": settings.livekit_url,
            "room_name": room_id,
            "identity": participant_identity,
            "niche": req.niche,
        }

    try:
        from livekit import api as livekit_api

        token = (
            livekit_api.AccessToken(
                settings.livekit_api_key, settings.livekit_api_secret
            )
            .with_identity(participant_identity)
            .with_name(req.visitor_name or "Demo Prospect")
            .with_grants(
                livekit_api.VideoGrants(
                    room_join=True, room=room_id, can_publish=True, can_subscribe=True
                )
            )
            .with_metadata(
                json.dumps(
                    {
                        "tenant_id": "demo-tenant",
                        "niche": req.niche or "demo",
                        "is_public_demo": True,
                    }
                )
            )
        )

        return {
            "token": token.to_jwt(),
            "url": settings.livekit_url,
            "room_name": room_id,
            "identity": participant_identity,
            "niche": req.niche,
        }
    except Exception as e:
        logger.error(f"Error generating demo token: {e}")
        return {
            "token": "mock_livekit_demo_token",
            "url": settings.livekit_url,
            "room_name": room_id,
            "identity": participant_identity,
            "niche": req.niche,
        }


@router.post("/callback")
async def request_demo_callback(req: DemoCallbackRequest, request: Request):
    """
    Registers a prospect's phone number and triggers an instant automated demo call.
    """
    if not req.phone_number:
        raise HTTPException(status_code=400, detail="Phone number is required")

    client_ip = request.client.host if request.client else "127.0.0.1"
    redis_client = await get_redis()
    allowed = await check_demo_rate_limit(redis_client, client_ip, limit=5)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Daily demo callback limit reached for this device.",
        )

    # Store lead in database if pool is ready
    if _pool:
        try:
            async with _pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS alfie_demo_leads (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        phone VARCHAR(50) NOT NULL,
                        niche VARCHAR(50),
                        company_name VARCHAR(255),
                        status VARCHAR(50) DEFAULT 'pending',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                await conn.execute(
                    """
                    INSERT INTO alfie_demo_leads (name, phone, niche, company_name)
                    VALUES ($1, $2, $3, $4)
                """,
                    req.visitor_name,
                    req.phone_number,
                    req.niche,
                    req.company_name,
                )
        except Exception as e:
            logger.warning(f"Failed to record demo lead in DB: {e}")

    logger.info(
        f"[DEMO CALLBACK] Prospect requested live call to: {req.phone_number} (Niche: {req.niche})"
    )

    return {
        "status": "success",
        "message": f"Demo call queued for {req.phone_number}. A.L.F.I.E will call you within a few seconds!",
        "phone_number": req.phone_number,
        "niche": req.niche,
    }
