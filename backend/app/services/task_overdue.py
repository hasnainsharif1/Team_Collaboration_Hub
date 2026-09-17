"""Background service — periodic task overdue checker.

Runs as an asyncio background task started from the FastAPI lifespan.
Every CHECK_INTERVAL_SECONDS it queries for tasks whose due_date has
passed and status is not 'done', and marks them as overdue.
"""

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task import mark_overdue_tasks
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

# How often to run the check (seconds). 60 = once per minute.
CHECK_INTERVAL_SECONDS = 60


async def run_overdue_checker() -> None:
    """
    Infinite loop that periodically marks overdue tasks.
    Should be started via asyncio.create_task() inside the FastAPI lifespan.
    """
    logger.info("Overdue task checker started (interval=%ds)", CHECK_INTERVAL_SECONDS)
    while True:
        try:
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)
            async with AsyncSessionLocal() as db:
                count = await mark_overdue_tasks(db)
                if count:
                    logger.info("Overdue checker: marked %d task(s) as overdue", count)
        except asyncio.CancelledError:
            # Graceful shutdown — exit the loop cleanly
            logger.info("Overdue task checker stopped")
            break
        except Exception as exc:
            # Never crash the whole server; just log and continue
            logger.exception("Overdue checker error: %s", exc)
