import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator


class Settings(BaseSettings):
    """
    Application settings, loaded securely using Docker Secrets or Environment Variables.
    Pydantic will automatically look in the `secrets_dir` (e.g., /run/secrets)
    for files matching the attribute names (lowercase).
    """

    # LiveKit
    livekit_url: str = Field(default="wss://alfie-ai-9ngpqe5q.livekit.cloud")
    livekit_api_key: str = Field(default="")
    livekit_api_secret: str = Field(default="")

    # AI Providers
    deepgram_api_key: str = Field(default="")
    openrouter_api_key: str = Field(default="")
    fish_audio_api_key: str = Field(default="")

    # Twenty CRM API
    twenty_api_url: str = Field(default="http://twenty-server:3000")
    twenty_api_key: str = Field(default="")

    # n8n Event Bus
    n8n_webhook_url: str = Field(default="http://n8n:5678/webhook/alfie-events")

    # Telemetry Database (uses same Postgres instance as Twenty)
    telemetry_db_dsn: str = Field(
        default="postgresql://postgres:alfie_secure_postgres_pass@postgres:5432/twenty_db"
    )

    # Redis (Caching, Rate Limiting, Pub/Sub)
    redis_dsn: str = Field(default="redis://redis:6379/0")

    # Security Secrets
    jwt_secret_key: str = Field(default="")
    super_admin_email: str = Field(default="")
    super_admin_password: str = Field(default="")
    
    # Billing & Telephony Fallbacks
    stripe_secret_key: str = Field(default="")
    stripe_webhook_secret: str = Field(default="")
    twilio_account_sid: str = Field(default="")
    twilio_auth_token: str = Field(default="")

    @model_validator(mode="after")
    def validate_required_secrets(self) -> "Settings":
        required = {
            "livekit_api_key": self.livekit_api_key,
            "livekit_api_secret": self.livekit_api_secret,
            "deepgram_api_key": self.deepgram_api_key,
            "openrouter_api_key": self.openrouter_api_key,
            "fish_audio_api_key": self.fish_audio_api_key,
            "twenty_api_key": self.twenty_api_key,
            "jwt_secret_key": self.jwt_secret_key,
            "super_admin_email": self.super_admin_email,
            "super_admin_password": self.super_admin_password,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(
                f"STARTUP FAILED: The following required secrets are missing or empty: {missing}. "
                "Ensure they are set in /run/secrets or the .env file before starting A.L.F.I.E."
            )
        return self

    model_config = SettingsConfigDict(
        # In a Docker container, secrets are mounted here by default
        secrets_dir="/run/secrets" if os.path.exists("/run/secrets") else "secrets",
        # Fallback to env vars if not found in secrets dir (useful for local dev without docker)
        env_file=".env",
        env_file_encoding="utf-8",
        # Ignore extra fields that might exist in the environment
        extra="ignore",
    )


# Instantiate settings singleton
settings = Settings()
