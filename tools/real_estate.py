import logging
from livekit.agents import llm
from typing import Annotated, Optional
from crm_client import crm


class RealEstateTools(llm.Toolset):
    def __init__(self, tenant_id: str):
        super().__init__(id="real_estate")
        self.tenant_id = tenant_id

    @llm.function_tool(
        description="Search for available real estate properties matching criteria."
    )
    async def search_properties(
        self,
        city: Annotated[str, "City name"],
        property_type: Annotated[str, "house, apartment, or plot"],
        bedrooms: Annotated[Optional[int], "Number of bedrooms"] = None,
        max_price: Annotated[Optional[float], "Maximum price in PKR"] = None,
    ) -> str:
        logging.info(f"[{self.tenant_id}] Searching properties in {city}")

        try:
            results = await crm.find_properties(city=city, min_beds=bedrooms)
            if not results:
                return "No properties found matching those criteria."

            summary = [
                f"{p.get('title', 'Property')} — {p.get('price', 'Unknown')} PKR, {p.get('bedrooms', '?')} beds ({p.get('status', 'Unknown')})"
                for p in results
            ]
            return "Available properties: " + " | ".join(summary)
        except Exception as e:
            logging.error(f"Error querying properties: {e}")
            return "I'm having trouble accessing the property database right now."

    @llm.function_tool(description="Book a viewing for a specific property.")
    async def book_viewing(
        self,
        property_title: Annotated[str, "The title or ID of the property"],
        viewing_date: Annotated[str, "Date for viewing (YYYY-MM-DD)"],
        time_slot: Annotated[str, "Time slot (e.g. 14:00)"],
    ) -> str:
        logging.info(f"[{self.tenant_id}] Booking viewing for {property_title}")

        try:
            task_id = await crm.create_task(
                title=f"Viewing: {property_title}",
                description=f"Scheduled for {viewing_date} at {time_slot}.",
            )
            return (
                f"Viewing booked for {viewing_date} at {time_slot}. Task ID: {task_id}"
            )
        except Exception as e:
            logging.error(f"Error booking viewing: {e}")
            return "I couldn't book the viewing due to a system error."
