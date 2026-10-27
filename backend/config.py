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

    # AI Audio Providers & Multi-Provider Mesh
    deepgram_api_key: str = Field(default="")
    openrouter_api_key: str = Field(default="")
    fish_audio_api_key: str = Field(default="")
    cartesia_api_key: str = Field(default="")
    elevenlabs_api_key: str = Field(default="")
    assemblyai_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")
    groq_api_key: str = Field(default="")
    cerebras_api_key: str = Field(default="")
    tts_primary_provider: str = Field(default="cartesia")
    tts_fallback_provider: str = Field(default="fish_audio")
    stt_primary_provider: str = Field(default="deepgram")
    stt_fallback_provider: str = Field(default="groq")
    fast_filler_model: str = Field(default="groq/llama-3.1-8b-instant")
    litellm_url: str = Field(default="http://litellm:4000")
    litellm_master_key: str = Field(default="")

    # OpenAI Realtime Native S2S Engine
    openai_realtime_model: str = Field(default="gpt-4o-realtime-preview")
    openai_realtime_voice: str = Field(default="alloy")

    # Twenty CRM API (Optional downstream sync)
    twenty_api_url: str = Field(default="http://twenty-server:3000")
    twenty_api_key: str = Field(default="")

    # n8n Event Bus
    n8n_webhook_url: str = Field(default="http://n8n:5678/webhook/alfie-events")

    # Telemetry Database (PostgreSQL)
    telemetry_db_dsn: str = Field(
        default_factory=lambda: os.environ.get(
            "TELEMETRY_DB_DSN",
            f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}:{os.environ.get('POSTGRES_PASSWORD', '')}@{os.environ.get('POSTGRES_HOST', 'postgres')}:5432/{os.environ.get('POSTGRES_DB', 'alfie_db')}"
            if os.environ.get("POSTGRES_PASSWORD")
            else "postgresql://postgres@localhost:5432/alfie_db",
        )
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
    twilio_phone_number: str = Field(default="")
    telnyx_api_key: str = Field(default="")
    carrier_provider: str = Field(default="twilio")

    # Audio Vault & Object Storage (Cloudflare R2 / AWS S3 / MinIO)
    s3_endpoint_url: str = Field(default="")
    s3_access_key_id: str = Field(default="")
    s3_secret_access_key: str = Field(default="")
    s3_bucket_name: str = Field(default="alfie-recordings")
    s3_region: str = Field(default="auto")
    audio_vault_local_dir: str = Field(default="recordings")

    # Logging & Observability
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="text")

    # Operational Flags
    sandbox_mode: bool = Field(default=False)

    @model_validator(mode="after")
    def validate_required_secrets(self) -> "Settings":
        required = {
            "livekit_api_key": self.livekit_api_key,
            "livekit_api_secret": self.livekit_api_secret,
            "deepgram_api_key": self.deepgram_api_key,
            "openrouter_api_key": self.openrouter_api_key,
            "fish_audio_api_key": self.fish_audio_api_key,
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
        # In a Docker container, secrets are mounted at /run/secrets; locally check secrets or ../secrets
        secrets_dir=(
            "/run/secrets"
            if os.path.exists("/run/secrets")
            else "secrets"
            if os.path.exists("secrets")
            else "../secrets"
            if os.path.exists("../secrets")
            else None
        ),
        # Fallback to env vars if not found in secrets dir (useful for local dev without docker)
        env_file=".env",
        env_file_encoding="utf-8",
        # Ignore extra fields that might exist in the environment
        extra="ignore",
    )


# Instantiate settings singleton
settings = Settings()
