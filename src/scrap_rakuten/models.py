import json
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str]
    title: Mapped[str] = mapped_column(default="")
    raw_content: Mapped[str] = mapped_column(default="")
    date: Mapped[datetime | None]
    tags: Mapped[str] = mapped_column(default="")

    def get_tags(self) -> set[str]:
        if self.tags == "":
            return set()
        tags = json.loads(self.tags)
        return set(tags)

    def set_tags(self, value: set[str]) -> None:
        self.tags = json.dumps(list(value))
