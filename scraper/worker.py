# written by sounic behera
import os
import asyncio
from celery import Celery
from scraper.factory import ScraperFactory
from storage.orchestrator import StorageOrchestrator

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery('vayu_scraper', broker=REDIS_URL)

@app.task(name='scraper.worker.scrape_flight_corridor')
def scrape_flight_corridor(provider: str, src: str, dest: str, depart_date: str, lead_tag: str):
    """
    Celery worker task that invokes the specified scraper and persists results.
    Runs asynchronously inside a new event loop since Celery tasks are synchronous by default.
    """
    scraper = ScraperFactory.get_scraper(provider)
    
    # Run the async Playwright scraper inside the synchronous Celery worker
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    quotes = loop.run_until_complete(
        scraper.extract_quotes(src, dest, depart_date, lead_tag)
    )
    
    if quotes:
        result_msg = StorageOrchestrator.persist_quotes(quotes)
        return {"status": "success", "message": result_msg, "extracted": len(quotes)}
    else:
        return {"status": "failed", "message": "No quotes extracted", "extracted": 0}
