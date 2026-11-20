from app import config
from app.untis.base import UntisProvider


def get_provider() -> UntisProvider:
    """UNTIS_PROVIDER=real|mock (default mock, so nothing logs in by accident)."""
    if config.get("UNTIS_PROVIDER", "mock") == "real":
        from app.untis.real import RealUntisProvider
        return RealUntisProvider()
    from app.untis.mock import MockUntisProvider
    return MockUntisProvider()
