"""
JARVIS Application Entry Point

M1.2:
Application startup is delegated to JarvisOrchestrator.
"""

import logging

from core.orchestrator import JarvisOrchestrator


def configure_logging():
    """Configure application logging."""

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )


def main():
    """Start Jarvis."""

    configure_logging()

    logger = logging.getLogger(__name__)

    logger.info("===================================")
    logger.info("        JARVIS STARTING")
    logger.info("===================================")

    orchestrator = JarvisOrchestrator()

    try:
        orchestrator.start()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")

    except Exception:
        logger.exception("Fatal Jarvis error")

    finally:
        orchestrator.shutdown()


if __name__ == "__main__":
    main()