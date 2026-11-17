from enum import Enum


class Config(Enum):
    rakuten_carrer_url = "https://japan-job-en.rakuten.careers/search-jobs"
    rakuten_carrer_base_url = "https://japan-job-en.rakuten.careers"
    db_url = "sqlite:///scraping.db"
    testing = False
