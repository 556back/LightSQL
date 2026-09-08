"""Run with python -m app.modules.catalog.worker (one small persistent worker)."""

import logging
import time

from app.core.db import engine
from app.modules.catalog.service import claim, run_job

logger = logging.getLogger(__name__)


def run_loop() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("Catalog worker started")
    while True:
        try:
            job = claim(engine)
            if job:
                run_job(engine, *job)
            else:
                time.sleep(2)
        except KeyboardInterrupt:
            return
        except Exception:
            # Never log database exceptions containing connection credentials.
            logger.error("Catalog worker cycle failed; retrying in five seconds")
            time.sleep(5)


def main() -> None:
    from app.modules.quality.operations import heartbeat

    with heartbeat(engine, "catalog"):
        run_loop()


if __name__ == "__main__":
    main()
