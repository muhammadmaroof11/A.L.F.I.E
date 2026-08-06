import logging
from livekit.agents import llm
from typing import Annotated, Optional
from crm_client import crm


class CarRentalTools(llm.Toolset):
    def __init__(self, tenant_id: str):
        super().__init__(id="car_rental")
        self.tenant_id = tenant_id

    @llm.function_tool(
        description="Search for available rental vehicles matching criteria."
    )
    async def search_vehicles(
        self,
        category: Annotated[str, "car category (e.g., economy, SUV, luxury)"],
        max_daily_rate: Annotated[Optional[float], "Maximum daily rate in PKR"] = None,
    ) -> str:
        logging.info(f"[{self.tenant_id}] Searching vehicles in category {category}")

        try:
            results = await crm.find_vehicles(category=category)
            if not results:
                return f"No available vehicles found in the {category} category."

            summary = []
            for v in results[:3]:
                make = v.get("make", "Unknown")
                model = v.get("model", "")
                rate = v.get("dailyRate", "Unknown")
                summary.append(f"{make} {model} for {rate} PKR/day")
            return "Available vehicles: " + "; ".join(summary)
        except Exception as e:
            logging.error(f"Error querying vehicles: {e}")
            return "I'm having trouble accessing the fleet database right now."

    @llm.function_tool(description="Book a vehicle for rental.")
    async def book_vehicle(
        self,
        vehicle_make_model: Annotated[str, "The make and model of the vehicle"],
        start_date: Annotated[str, "Start date (YYYY-MM-DD)"],
        end_date: Annotated[str, "End date (YYYY-MM-DD)"],
    ) -> str:
        logging.info(f"[{self.tenant_id}] Booking vehicle {vehicle_make_model}")

        try:
            task_id = await crm.create_task(
                title=f"Rental: {vehicle_make_model}",
                description=f"Booking from {start_date} to {end_date}.",
            )
            return (
                f"Vehicle booked from {start_date} to {end_date}. Booking ID: {task_id}"
            )
        except Exception as e:
            logging.error(f"Error booking vehicle: {e}")
            return "I couldn't book the vehicle due to a system error."
