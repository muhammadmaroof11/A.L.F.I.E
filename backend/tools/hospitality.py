import logging
from livekit.agents import llm
from typing import Annotated
from datetime import datetime


class HospitalityTools(llm.Toolset):
    def __init__(self, tenant_id: str):
        super().__init__(id="hospitality_tools")
        self.tenant_id = tenant_id

    @llm.function_tool(
        description="Check if a table is available for a specific date, time, and party size."
    )
    async def check_table_availability(
        self,
        date: Annotated[str, "The requested date (YYYY-MM-DD)"],
        time: Annotated[str, "The requested time (HH:MM AM/PM)"],
        party_size: Annotated[int, "Number of guests"],
    ) -> str:
        logging.info(
            f"[{self.tenant_id}] Checking availability for party of {party_size} on {date} at {time}"
        )

        from datetime import datetime

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Error: Invalid date format. Please format as YYYY-MM-DD"

        try:
            import asyncio
            from telemetry import _pool

            if not _pool:
                return "System error: Database not connected."

            try:
                conn = await asyncio.wait_for(_pool.acquire(), timeout=3.0)
            except asyncio.TimeoutError:
                return (
                    "The system is currently very busy. Please hold on and try again."
                )

            try:
                # 1. Total capacity
                total_capacity = await conn.fetchval(
                    "SELECT SUM(capacity) FROM alfie_restaurant_inventory WHERE tenant_id = $1",
                    self.tenant_id,
                )
                if not total_capacity:
                    total_capacity = 100  # default mock

                # 2. Existing reservations for that day
                booked = await conn.fetchval(
                    """
                    SELECT SUM(party_size) FROM alfie_restaurant_reservations 
                    WHERE tenant_id = $1 AND reservation_time::date = $2::date
                    AND status = 'confirmed'
                """,
                    self.tenant_id,
                    date,
                )
                if not booked:
                    booked = 0

                if (booked + party_size) <= total_capacity:
                    return f"Yes, we have availability for a party of {party_size} on {date} at {time}."
                else:
                    return f"I'm sorry, we are fully booked for a party of {party_size} on that date."
            finally:
                await _pool.release(conn)
        except Exception as e:
            logging.error(f"Error checking availability: {e}")
            return "Failed to check availability due to a system error."

    @llm.function_tool(description="Book a restaurant reservation.")
    async def book_reservation(
        self,
        customer_name: Annotated[str, "Full name of the customer"],
        customer_phone: Annotated[str, "Phone number"],
        party_size: Annotated[int, "Number of guests"],
        reservation_datetime: Annotated[
            str, "The combined date and time (ISO 8601 format)"
        ],
        special_requests: Annotated[
            str, "Any special requests (e.g., allergies, anniversary)"
        ],
    ) -> str:
        logging.info(f"[{self.tenant_id}] Booking reservation for {customer_name}")

        try:
            import asyncio
            from telemetry import _pool

            if not _pool:
                return "System error: Database not connected."

            try:
                conn = await asyncio.wait_for(_pool.acquire(), timeout=3.0)
            except asyncio.TimeoutError:
                return (
                    "The system is currently very busy. Please hold on and try again."
                )

            try:
                await conn.execute(
                    """
                    INSERT INTO alfie_restaurant_reservations 
                    (tenant_id, customer_name, customer_phone, party_size, reservation_time, special_requests)
                    VALUES ($1, $2, $3, $4, $5::timestamp with time zone, $6)
                """,
                    self.tenant_id,
                    customer_name,
                    customer_phone,
                    party_size,
                    reservation_datetime,
                    special_requests,
                )

                return "Reservation confirmed! We look forward to hosting them."
            finally:
                await _pool.release(conn)
        except Exception as e:
            logging.error(f"Error booking reservation: {e}")
            return "Failed to book the reservation due to a system error."
