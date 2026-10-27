import logging
import httpx
from livekit.agents import llm
from typing import Annotated


class LuxuryTransportTools(llm.Toolset):
    def __init__(self, tenant_id: str):
        super().__init__(id="luxury_transport")
        self.tenant_id = tenant_id

    @llm.function_tool(
        description="Calculate the distance in miles between a pickup and dropoff location."
    )
    async def calculate_route_distance(
        self,
        pickup_location: Annotated[str, "The starting address or city"],
        dropoff_location: Annotated[str, "The destination address or city"],
    ) -> str:
        logging.info(
            f"[{self.tenant_id}] Calculating distance: {pickup_location} -> {dropoff_location}"
        )

        # 1. Geocode both locations using Nominatim (OSM)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"User-Agent": "ALFIE-Agent-1.0"}

                pickup_res = await client.get(
                    f"https://nominatim.openstreetmap.org/search?q={pickup_location}&format=json&limit=1",
                    headers=headers,
                )
                dropoff_res = await client.get(
                    f"https://nominatim.openstreetmap.org/search?q={dropoff_location}&format=json&limit=1",
                    headers=headers,
                )

                pickup_data = pickup_res.json()
                dropoff_data = dropoff_res.json()

                if not pickup_data:
                    return f"Could not find pickup location: {pickup_location}"
                if not dropoff_data:
                    return f"Could not find dropoff location: {dropoff_location}"

                p_lon, p_lat = pickup_data[0]["lon"], pickup_data[0]["lat"]
                d_lon, d_lat = dropoff_data[0]["lon"], dropoff_data[0]["lat"]

                # 2. Get Route Distance using OSRM
                route_res = await client.get(
                    f"https://router.project-osrm.org/route/v1/driving/{p_lon},{p_lat};{d_lon},{d_lat}?overview=false"
                )
                route_data = route_res.json()

                if route_data.get("code") == "Ok":
                    distance_meters = route_data["routes"][0]["distance"]
                    distance_miles = distance_meters * 0.000621371

                    # 3. Fetch Pricing from our DB
                    from telemetry import _pool

                    pricing_info = ""
                    if _pool:
                        async with _pool.acquire() as conn:
                            rates = await conn.fetch(
                                "SELECT car_class, base_fare, price_per_mile FROM alfie_transport_rates WHERE tenant_id = $1",
                                self.tenant_id,
                            )
                            if rates:
                                pricing_info = " Available Cars and Pricing:\n"
                                for r in rates:
                                    cost = float(r["base_fare"]) + (
                                        float(r["price_per_mile"]) * distance_miles
                                    )
                                    pricing_info += f"- {r['car_class']}: ${cost:.2f}\n"

                    return f"Distance is {distance_miles:.1f} miles. {pricing_info}"
                else:
                    return (
                        "Could not calculate a driving route between these locations."
                    )

        except Exception as e:
            logging.error(f"Error in map calculation: {e}")
            return "Routing service is currently down."

    @llm.function_tool(description="Book a luxury transport reservation.")
    async def book_reservation(
        self,
        customer_name: Annotated[str, "Name of the passenger"],
        customer_phone: Annotated[str, "Phone number of the passenger"],
        pickup_location: Annotated[str, "Pick-up address"],
        dropoff_location: Annotated[str, "Drop-off address"],
        car_class: Annotated[str, "The selected car class"],
        total_price: Annotated[float, "The calculated total price in USD"],
    ) -> str:
        logging.info(f"[{self.tenant_id}] Booking luxury transport for {customer_name}")

        try:
            from telemetry import _pool

            if not _pool:
                return "System error: Database not connected."

            async with _pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO alfie_transport_bookings 
                    (tenant_id, customer_name, customer_phone, pickup_location, dropoff_location, car_class, total_price)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                    self.tenant_id,
                    customer_name,
                    customer_phone,
                    pickup_location,
                    dropoff_location,
                    car_class,
                    total_price,
                )

            return "Reservation confirmed successfully. The booking has been saved in the system."
        except Exception as e:
            logging.error(f"Error booking transport: {e}")
            return "Failed to book the reservation due to a system error."
