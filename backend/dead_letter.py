"""
A.L.F.I.E. Dead Letter Queue (DLQ) Manager.
Records and tracks background jobs that have exhausted all retry attempts
or encountered critical unrecoverable operational errors.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger("alfie.dead_letter")


async def record_dead_letter(
    conn: Any,
    job_name: str,
    job_args: Any,
    error: str,
    attempts: int = 1,
) -> Optional[int]:
    """
    Persists a failed job to alfie_dead_letter_queue for operator triage.
    Returns the newly created dead letter ID or None if persistence fails.
    """
    try:
        if isinstance(job_args, (dict, list)):
            args_json = json.dumps(job_args, default=str)
        elif isinstance(job_args, str):
            args_json = json.dumps({"raw_args": job_args})
        else:
            args_json = json.dumps({"raw_args": str(job_args)})

        now = datetime.now(timezone.utc)
        dlq_id = await conn.fetchval(
            """
            INSERT INTO alfie_dead_letter_queue (
                job_name, job_args, error_message, attempts, created_at
            ) VALUES ($1, $2::jsonb, $3, $4, $5)
            RETURNING id
            """,
            job_name,
            args_json,
            str(error),
            int(attempts),
            now,
        )
        logger.error(
            f"[DEAD LETTER QUEUE] Recorded job '{job_name}' (ID: {dlq_id}) after {attempts} attempts: {error}"
        )
        return dlq_id
    except Exception as e:
        logger.error(f"[DEAD LETTER QUEUE] Failed to record dead letter for '{job_name}': {e}")
        return None
