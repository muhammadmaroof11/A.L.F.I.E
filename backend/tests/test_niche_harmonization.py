import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure test environment variables are set before config initializes
for secret_key in [
    "LIVEKIT_API_KEY",
    "LIVEKIT_API_SECRET",
    "DEEPGRAM_API_KEY",
    "OPENROUTER_API_KEY",
    "FISH_AUDIO_API_KEY",
    "JWT_SECRET_KEY",
    "SUPER_ADMIN_EMAIL",
    "SUPER_ADMIN_PASSWORD",
]:
    if secret_key not in os.environ:
        os.environ[secret_key] = "test-dummy-key"


from prompts.registry import PROMPT_REGISTRY, get_prompt_for_niche
from prompts.legal import LEGAL_INTAKE_PROMPT
from prompts.medical import MEDICAL_RECEPTION_PROMPT
from prompts.hospitality import HOSPITALITY_CONCIERGE_PROMPT
from prompts.luxury_transport import LUXURY_TRANSPORT_PROMPT
from prompts.real_estate import REAL_ESTATE_PROMPT
from prompts.car_rental import CAR_RENTAL_PROMPT
from tools.registry import ToolRegistry
from tools.legal import LegalIntakeTools
from tools.medical import MedicalTools
from tools.hospitality import HospitalityTools
from tools.luxury_transport import LuxuryTransportTools
from tools.car_rental import CarRentalTools
from tools.real_estate import RealEstateTools
from tools.calendar import CalendarTools


class TestNicheHarmonization(unittest.IsolatedAsyncioTestCase):
    def test_prompt_registry_contains_all_verticals_and_aliases(self):
        """Verify prompt registry properly maps every known frontend/backend alias."""
        # Legal
        for key in ["legal", "legal_intake", "personal_injury", "law_firm", "law_firms"]:
            self.assertEqual(PROMPT_REGISTRY[key], LEGAL_INTAKE_PROMPT, f"Mismatch for {key}")
            self.assertIn("Statute of Limitations", get_prompt_for_niche(key))

        # Medical
        for key in ["clinic", "clinics", "medical", "medical_reception", "dental", "dental_clinic"]:
            self.assertEqual(PROMPT_REGISTRY[key], MEDICAL_RECEPTION_PROMPT, f"Mismatch for {key}")
            self.assertIn("Insurance", get_prompt_for_niche(key))

        # Hospitality
        for key in ["hospitality", "hospitality_concierge", "restaurant", "dining"]:
            self.assertEqual(PROMPT_REGISTRY[key], HOSPITALITY_CONCIERGE_PROMPT, f"Mismatch for {key}")
            self.assertIn("Dining Concierge", get_prompt_for_niche(key))

        # Transport & Fleet
        for key in ["luxury_transfer", "luxury_transport", "fleet", "chauffeur"]:
            self.assertEqual(PROMPT_REGISTRY[key], LUXURY_TRANSPORT_PROMPT, f"Mismatch for {key}")
            self.assertIn("Chauffeur", get_prompt_for_niche(key))

        # Real Estate
        for key in ["real_estate", "realestate", "realty", "property"]:
            self.assertEqual(PROMPT_REGISTRY[key], REAL_ESTATE_PROMPT, f"Mismatch for {key}")
            self.assertIn("Real Estate", get_prompt_for_niche(key))

        # Car Rental
        for key in ["car_rental", "carrental"]:
            self.assertIn(key, PROMPT_REGISTRY)

    async def test_tool_registry_injects_tools_for_all_vertical_aliases(self):
        """Verify tool registry dynamically injects toolsets for all vertical aliases."""
        registry = ToolRegistry()
        registry.register("legal_intake_tools", LegalIntakeTools)
        registry.register("medical_tools", MedicalTools)
        registry.register("hospitality_tools", HospitalityTools)
        registry.register("luxury_transport_tools", LuxuryTransportTools)
        registry.register("car_rental_tools", CarRentalTools)
        registry.register("real_estate_tools", RealEstateTools)
        registry.register("calendar_tools", CalendarTools)

        test_cases = [
            ("legal", LegalIntakeTools),
            ("legal_intake", LegalIntakeTools),
            ("personal_injury", LegalIntakeTools),
            ("clinic", MedicalTools),
            ("medical", MedicalTools),
            ("medical_reception", MedicalTools),
            ("hospitality", HospitalityTools),
            ("hospitality_concierge", HospitalityTools),
            ("luxury_transfer", LuxuryTransportTools),
            ("carrental", LuxuryTransportTools),
            ("realestate", RealEstateTools),
            ("real_estate", RealEstateTools),
        ]

        for niche_alias, expected_class in test_cases:
            toolsets = await registry.build_toolsets(
                enabled_tools=[],
                niche=niche_alias,
                tenant_id="test-tenant",
            )
            matching = [ts for ts in toolsets if isinstance(ts, expected_class)]
            self.assertTrue(
                len(matching) >= 1,
                f"Failed to inject {expected_class.__name__} for niche alias '{niche_alias}'"
            )

    async def test_migration_006_schema_statements(self):
        """Verify migration 006 contains all necessary DDL statements for hardened schemas."""
        from migrations import migration_006_schema_hardening_columns

        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = 0

        await migration_006_schema_hardening_columns(mock_conn)

        # Check that conn.execute was called with DDL containing persona, niche, and recording columns
        executed_sqls = [call.args[0] for call in mock_conn.execute.call_args_list]
        combined_sql = " ".join(executed_sqls)

        self.assertIn("alfie_call_recordings ADD COLUMN IF NOT EXISTS duration_seconds", combined_sql)
        self.assertIn("alfie_call_recordings ADD COLUMN IF NOT EXISTS quality_score", combined_sql)
        self.assertIn("alfie_call_recordings ADD COLUMN IF NOT EXISTS cost_usd", combined_sql)
        self.assertIn("alfie_personas ADD COLUMN IF NOT EXISTS niche_name", combined_sql)
        self.assertIn("alfie_niches ADD COLUMN IF NOT EXISTS default_tools_json", combined_sql)


if __name__ == "__main__":
    unittest.main()
