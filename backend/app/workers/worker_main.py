"""
LEGACYX — Worker Entry Point (Phase 1 Stub).

This module is the entry point for the background worker process.
In Phase 1 it does nothing but start successfully and log a message.

The worker will be fully implemented in Phase 3 (analysis) and later phases.
Do not add job processing logic here until the appropriate phase.
"""

import asyncio

from app.core.logging import configure_logging, get_logger


async def main() -> None:
    configure_logging()
    logger = get_logger(__name__)
    logger.info(
        "worker_started",
        note="Phase 1 stub — no jobs are processed yet. Implementation begins in Phase 3.",
    )
    # Keep the process alive so docker-compose doesn't restart it repeatedly.
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
