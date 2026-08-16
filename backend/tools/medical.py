import logging
from livekit.agents import llm
from typing import Annotated

class MedicalTools(llm.Toolset):
    def __init__(self, tenant_id: str):
        super().__init__(id="medical_tools")
        self.tenant_id = tenant_id

    @llm.function_tool(description="Verify if a specific insurance provider is accepted by the clinic.")
    async def verify_insurance_network(
        self,
        provider_name: Annotated[str, "The name of the insurance company (e.g., Delta Dental, Aetna)"],
    ) -> str:
        logging.info(f"[{self.tenant_id}] Verifying insurance: {provider_name}")
        
        try:
            import asyncio
            from telemetry import _pool
            if not _pool: return "System error: Database not connected."
            
            try:
                conn = await asyncio.wait_for(_pool.acquire(), timeout=3.0)
            except asyncio.TimeoutError:
                return "The system is currently very busy. Please hold on and try again."
                
            try:
                row = await conn.fetchrow("""
                    SELECT network_type FROM alfie_accepted_insurance 
                    WHERE tenant_id = $1 AND provider_name ILIKE $2
                """, self.tenant_id, f"%{provider_name}%")
                
                if row:
                    return f"Yes, we accept {provider_name}. Network Type: {row['network_type']}."
                else:
                    return f"No, we currently do not accept {provider_name}, or it is out of network."
            finally:
                await _pool.release(conn)
        except Exception as e:
            logging.error(f"Error checking insurance: {e}")
            return "Failed to verify insurance due to a system error."

    @llm.function_tool(description="Book a new medical or dental appointment.")
    async def book_patient_appointment(
        self,
        patient_name: Annotated[str, "Full name of the patient"],
        patient_phone: Annotated[str, "Phone number"],
        patient_dob: Annotated[str, "Date of birth (YYYY-MM-DD)"],
        is_new_patient: Annotated[bool, "True if this is a new patient, False if returning"],
        reason_for_visit: Annotated[str, "Brief reason for the appointment (e.g., Checkup, Cleaning)"],
        appointment_time: Annotated[str, "Requested time (ISO 8601 format)"],
    ) -> str:
        logging.info(f"[{self.tenant_id}] Booking medical appointment for {patient_name}")
        
        from datetime import datetime
        try:
            datetime.strptime(patient_dob, "%Y-%m-%d")
        except ValueError:
            return "Error: Invalid date format for DOB. Please format as YYYY-MM-DD"
            
        try:
            import asyncio
            from telemetry import _pool
            if not _pool: return "System error: Database not connected."
            
            try:
                conn = await asyncio.wait_for(_pool.acquire(), timeout=3.0)
            except asyncio.TimeoutError:
                return "The system is currently very busy. Please hold on and try again."
                
            try:
                await conn.execute("""
                    INSERT INTO alfie_medical_appointments 
                    (tenant_id, patient_name, patient_phone, patient_dob, is_new_patient, reason_for_visit, appointment_time)
                    VALUES ($1, $2, $3, $4::date, $5, $6, $7::timestamp with time zone)
                """, self.tenant_id, patient_name, patient_phone, patient_dob, is_new_patient, reason_for_visit, appointment_time)
                
                return "Appointment booked successfully. We will see the patient then."
            finally:
                await _pool.release(conn)
        except Exception as e:
            logging.error(f"Error booking appointment: {e}")
            return "Failed to book the appointment due to a system error."
