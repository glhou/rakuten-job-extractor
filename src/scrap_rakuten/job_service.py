import re

from loguru import logger
from sqlalchemy import select

from scrap_rakuten.db import session_scope
from scrap_rakuten.models import Job
from scrap_rakuten.scrapper import PageContent


def save_job_url(urls: list[str]) -> dict[int, str]:
    with session_scope() as session:
        existing_jobs = (
            session.execute(select(Job).where(Job.url.in_(urls))).scalars().all()
        )
        existing_urls = [job.url for job in existing_jobs]
        to_add_urls = set(urls) - set(existing_urls)
        jobs = []
        for url in to_add_urls:
            job = Job(url=url)
            session.add(job)
            jobs.append(job)
        session.commit()
        return {job.id: job.url for job in jobs + existing_jobs}


def update_job_infos(job_content: dict[int, PageContent | None]):
    with session_scope() as session:
        for job_id, content in job_content.items():
            job = session.get(Job, job_id)
            if not job:
                logger.critical("Couldn't find job id {}", job_id)
                continue
            if not content:
                continue
            job.title = content.title
            job.raw_content = content.raw_text.lower()
            job.date = content.date
            process_tags(job)
        session.commit()


# 4 years or 4 year or 4+ years
years_re = re.compile(r"(\d+)\+?\s+years?")

# japanese (overall - 4 - fluent)
language_re = re.compile(r"(\w+)\s\((\w+)\s-\s(\d)\s-\s(\w+)\)")


def process_tags(job: Job):
    tags = job.get_tags()
    for language in ("python", "go"):
        if language in job.raw_content:
            tags.add(language)
    for language_level in ("business-level", "business level", "n1", "n2", "n3"):
        if language_level in job.raw_content:
            tags.add(language_level)
    for match in language_re.findall(job.raw_content):
        tags.add(f"{' '.join(match)}")
    for match in years_re.findall(job.raw_content):
        tags.add(f"{match} years")
    job.set_tags(tags)
