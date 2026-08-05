import asyncio
import os
import json
from livekit import api
from config import settings

async def setup_sip_trunk():
    """
    Automates the creation of a LiveKit SIP Trunk and Dispatch Rule.
    This connects a phone number to the A.L.F.I.E agent.
    """
    print("Initializing LiveKit API Client...")
    
    # Needs LiveKit API credentials from secrets
    lkapi = api.LiveKitAPI(
        settings.livekit_url,
        settings.livekit_api_key,
        settings.livekit_api_secret
    )
    
    # 1. Create a SIP Trunk (connecting LiveKit to your SIP Provider like Twilio)
    print("Creating SIP Trunk...")
    try:
        trunk = await lkapi.sip.create_sip_inbound_trunk(
            api.CreateSIPInboundTrunkRequest(
                name="alfie-twilio-trunk",
                numbers=["+1234567890"], # Replace with your purchased number
                # Whitelist provider IPs here to prevent Toll Fraud / unauthorized calls
                allowed_addresses=["twilio.com", "54.172.60.0/24"],
                allowed_numbers=[]
            )
        )
        print(f"Trunk Created: {trunk.sip_trunk_id}")
        
        # 2. Create a Dispatch Rule (routes incoming SIP calls to a specific Room/Agent)
        # NOTE: Each phone number / tenant needs its own dispatch rule with its own metadata.
        # The metadata JSON is read by agent.py at call start to determine the tenant.
        rule = await lkapi.sip.create_sip_dispatch_rule(
            api.CreateSIPDispatchRuleRequest(
                name="route-to-alfie",
                trunk_ids=[trunk.sip_trunk_id],
                rule=api.SIPDispatchRule(
                    # This routes the call to a room named "alfie-call-<random>"
                    dispatch_rule_direct=api.SIPDispatchRuleDirect(
                        room_prefix="alfie-call-",
                        pin="1234" # Optional PIN for extra security
                    )
                ),
                # CRITICAL: Encode the tenant_id here so agent.py can route dynamically.
                # Each dispatch rule for a different client must have a different tenant_id here.
                metadata=json.dumps({"tenant_id": "alfie_realty_pk"})
            )
        )
        print(f"Dispatch Rule Created: {rule.sip_dispatch_rule_id}")
        
    except Exception as e:
        print(f"Error setting up SIP: {e}")
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    if not settings.livekit_api_key:
        print("Error: Missing LiveKit API Key in secrets.")
    else:
        asyncio.run(setup_sip_trunk())
