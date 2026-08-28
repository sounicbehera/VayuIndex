import asyncio
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from scraping.live_crawler import run_live_pipeline
from index_engine.calculator import calculate_and_store_index

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scheduler.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("vayuScheduler")

def job_crawl_quotes():
    """Triggers real-time asynchronous fare crawl across corridors."""
    logger.info("[SCHEDULER] Starting scheduled flight fare ingestion cycle...")
    try:
        asyncio.run(run_live_pipeline())
        logger.info("[SCHEDULER] Fare ingestion cycle completed successfully.")
    except Exception as e:
        logger.error(f"[SCHEDULER] Fare ingestion error: {e}", exc_info=True)

def job_compute_daily_index():
    """Computes daily Jevons-Laspeyres aggregation and persists to apix_daily_indices."""
    logger.info("[SCHEDULER] Triggering daily Jevons-Laspeyres APIx index computation...")
    try:
        calculate_and_store_index()
        logger.info("[SCHEDULER] Daily index computed and stored.")
    except Exception as e:
        logger.error(f"[SCHEDULER] Index computation error: {e}", exc_info=True)

def main():
    scheduler = BlockingScheduler(timezone="UTC")

    # 1. Scheduled Ingestion: Crawl live quotes every 6 hours
    scheduler.add_job(
        job_crawl_quotes,
        trigger=IntervalTrigger(hours=6),
        id="live_quote_crawler",
        name="Crawl Domestic Routes",
        replace_existing=True,
        next_run_time=datetime.now(timezone.utc)  # Run immediate initial crawl on start
    )

    # 2. Daily Index Seal: Compute and persist index at 23:55 UTC every day
    scheduler.add_job(
        job_compute_daily_index,
        trigger=CronTrigger(hour=23, minute=55),
        id="daily_index_sealer",
        name="Compute & Seal Daily APIx",
        replace_existing=True
    )

    logger.info("=" * 60)
    logger.info(" vayuIndex Automated Engine Scheduler Online ")
    logger.info(" - Fare Crawl Interval: Every 6 Hours (with instant boot run)")
    logger.info(" - Daily APIx Computation: 23:55 UTC")
    logger.info("=" * 60)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("[SCHEDULER] Shutdown signal received. Stopping worker...")

if __name__ == "__main__":
    main()