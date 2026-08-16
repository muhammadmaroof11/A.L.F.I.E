import logging
from livekit.agents import llm
from typing import Annotated, Optional
import httpx
from datetime import datetime, timedelta

logger = logging.getLogger("alfie.calendar")


class CalendarTools(llm.Toolset):
    """Tools for real-time calendar availability and booking via Cal.com API."""

    def __init__(self, tenant_id: str, **kwargs):
        super().__init__(id="calendar_tools")
        self.tenant_id = tenant_id
        self.api_key = kwargs.get("calendar_api_key", "")
        self.event_type_id = kwargs.get("calendar_event_type_id", "")
        self.base_url = "https://api.cal.com/v1"
        self.client = httpx.AsyncClient(timeout=10.0)

    def _get_auth_params(self):
        return {"apiKey": self.api_key}

    @llm.function_tool(
        description="Check available time slots for a given date on the calendar. Returns available slots."
    )
    async def check_availability(
        self, date_str: Annotated[str, "Date to check availability for (YYYY-MM-DD)"]
    ) -> str:
        logger.info(f"[{self.tenant_id}] Checking availability for {date_str}")

        if not self.api_key or not self.event_type_id:
            return "Calendar integration is not configured correctly."

        try:
            # Calculate start and end date for the query (1 day window)
            start_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            end_date = start_date + timedelta(days=1)

            params = self._get_auth_params()
            params.update(
                {
                    "eventTypeId": self.event_type_id,
                    "startTime": start_date.isoformat(),
                    "endTime": end_date.isoformat(),
                }
            )

            res = await self.client.get(f"{self.base_url}/slots", params=params)
            res.raise_for_status()
            slots = res.json().get("slots", {})

            # The slots are returned keyed by date. Flatten them.
            available_times = []
            for date_key, time_slots in slots.items():
                for slot in time_slots:
                    # Slot contains "time" like "2024-10-25T09:00:00.000Z"
                    available_times.append(slot.get("time"))

            if not available_times:
                return f"No available slots on {date_str}. Please try another date."

            # Format nicely
            times_formatted = []
            for t in available_times[:10]:  # Return max 10 slots
                try:
                    dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
                    times_formatted.append(dt.strftime("%I:%M %p"))
                except:
                    pass

            return f"Available slots on {date_str}: " + ", ".join(times_formatted)

        except Exception as e:
            logger.error(f"Failed to check calendar availability: {e}")
            return "I'm having trouble accessing the calendar right now."

    @llm.function_tool(
        description="Book an appointment on the calendar at a specific time."
    )
    async def book_appointment(
        self,
        name: Annotated[str, "Full name of the caller"],
        email: Annotated[str, "Email address of the caller"],
        start_time: Annotated[
            str,
            "Start time of the booking in ISO format (e.g. 2024-10-25T09:00:00.000Z)",
        ],
        phone: Annotated[Optional[str], "Phone number"] = None,
    ) -> str:
        logger.info(
            f"[{self.tenant_id}] Booking appointment for {name} at {start_time}"
        )

        if not self.api_key or not self.event_type_id:
            return "Calendar integration is not configured correctly."

        try:
            payload = {
                "eventTypeId": int(self.event_type_id),
                "start": start_time,
                "responses": {"name": name, "email": email, "phone": phone or ""},
                "timeZone": "UTC",
                "language": "en",
            }

            res = await self.client.post(
                f"{self.base_url}/bookings",
                params=self._get_auth_params(),
                json=payload,
            )
            res.raise_for_status()

            booking_id = res.json().get("booking", {}).get("id")
            return f"Successfully booked! Your appointment ID is {booking_id}."

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                return "That time slot is already taken. Please choose another."
            logger.error(f"Failed to book appointment: {e}")
            return "I'm having trouble completing the booking right now."
        except Exception as e:
            logger.error(f"Failed to book appointment: {e}")
            return "I'm having trouble completing the booking right now."
