from loguru import logger

from scrap_rakuten.db import create_db
from scrap_rakuten.job_service import save_job_url, update_job_infos
from scrap_rakuten.scrapper import get_pages_content, get_urls


def main():
    create_db()
    logger.info("Starting job")
    urls = get_urls()
    logger.info("Found {} urls", len(urls))
    logger.info("Saving jobs")
    job_urls = save_job_url(urls)
    logger.info("Extract content")
    contents = get_pages_content(job_urls)
    logger.info("Save page content")
    update_job_infos(contents)
    logger.info("Finished job")
