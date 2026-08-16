import httpx
import logging

logger = logging.getLogger("alfie-http")

# Global HTTP client with aggressive connection pooling limits
# max_keepalive_connections: limit the number of idle connections kept alive
# max_connections: total max concurrent connections allowed
global_http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(timeout=15.0),
    limits=httpx.Limits(max_keepalive_connections=50, max_connections=200),
)


def get_http_client() -> httpx.AsyncClient:
    """Returns the global HTTP client instance."""
    return global_http_client


async def close_http_client():
    """Closes the global HTTP client gracefully."""
    logger.info("Closing global HTTP client...")
    await global_http_client.aclose()
