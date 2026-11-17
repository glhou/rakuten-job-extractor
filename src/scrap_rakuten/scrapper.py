from datetime import datetime
from urllib.parse import parse_qs, urlparse

from loguru import logger
from pydantic import BaseModel, ValidationError
from scrapling.spiders import Response, Spider
from trafilatura import extract, fetch_url

from scrap_rakuten.config import Config


class UrlSpider(Spider):
    name = "urls"
    start_urls = [Config.rakuten_carrer_url.value]
    concurrent_requests = 10

    async def parse(self, response: Response):
        found = False
        for link in response.css(
            'section[id="search-results-list"] > ul > li > a[href^="/job"]'
        ):
            found = True
            logger.debug("Getting {} link", link.attrib.get("href"))
            yield {"url": link.attrib.get("href")}

        if not found:
            return

        if Config.testing.value:
            return

        parsed_url = urlparse(response.url)
        query = parse_qs(parsed_url.query)
        page = query.get("p", None)
        if not page:
            page = ["0"]
        p = int(page[0])
        next_url = f"{Config.rakuten_carrer_url.value.rstrip('/')}?p={p + 1}"
        yield response.follow(next_url)


def get_urls() -> list[str]:
    result = UrlSpider().start()
    return [
        Config.rakuten_carrer_base_url.value.rstrip("/") + i["url"]
        for i in result.items
        if i.get("url")
    ]


class PageContent(BaseModel):
    title: str
    date: datetime
    raw_text: str


def get_pages_content(job_urls: dict[int, str]) -> dict[int, PageContent | None]:
    return {job_id: get_page_content(url) for job_id, url in job_urls.items()}


def get_page_content(url: str) -> PageContent | None:
    downloaded = fetch_url(url)
    extracted = extract(
        downloaded,
        output_format="json",
        with_metadata=True,
        include_formatting=False,
    )
    if not extracted:
        return None
    try:
        return PageContent.model_validate_json(extracted)
    except ValidationError:
        logger.exception("Couldn't validate the extracted content {}", extracted)
        return None
