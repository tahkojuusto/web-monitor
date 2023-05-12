import asyncio
import aiohttp
import aiofiles
import logging
import re
import time

from models.Settings import Settings
from models.Website import Website
from models.WebsiteStatus import WebsiteStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


async def check_website(
    website: Website, queue: asyncio.Queue, checking_period_seconds: int
):
    while True:
        async with aiohttp.ClientSession() as session:
            try:
                # Measure latency of the request
                tic = time.perf_counter()
                response = await session.get(website.url)
                toc = time.perf_counter()

                response_text = ""
                if response.ok:
                    # Get the response body if the request was successful
                    response_text = await response.text()

                website_status = WebsiteStatus(
                    website=website,
                    status=response.status,
                    latency_ms=round((toc - tic) * 1000),
                    content_ok=bool(re.search(website.content, response_text)),
                )
                if response.reason:
                    website_status.reason = response.reason
            except Exception as error:
                website_status = WebsiteStatus(website=website, reason=str(error))

        # Pass the status result to the log writer thru an async queue
        await queue.put(website_status)

        # Wait until the next run
        await asyncio.sleep(checking_period_seconds)


async def write_log_row(queue: asyncio.Queue, log_filename: str):
    while True:
        # Get one website status result
        website_status = await queue.get()

        async with aiofiles.open(log_filename, mode="a") as log_file:
            logger.info(website_status)
            await log_file.write(website_status.get_log_row())

        # Mark the enqueued task done
        queue.task_done()


async def main():
    # Read settings from the config file
    config = Settings()

    # Buffer between website polling and log writing.
    response_queue = asyncio.Queue()

    async with asyncio.TaskGroup() as task_group:
        # Create a task for each website polling (producers).
        producer_tasks = [
            task_group.create_task(
                check_website(website, response_queue, config.checking_period_seconds)
            )
            for website in config.websites
        ]

        # Create a task for scanning the response queue and writing results to a log file (consumer).
        consumer_tasks = [
            task_group.create_task(write_log_row(response_queue, config.log_filename))
        ]

    await response_queue.join()


if __name__ == "__main__":
    asyncio.run(main())
