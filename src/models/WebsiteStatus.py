from pydantic import BaseModel, Field
from models.Website import Website
from datetime import datetime


class WebsiteStatus(BaseModel):
    check_time: datetime = Field(default_factory=datetime.utcnow)
    website: Website
    status: int | None = None
    latency_ms: int | None = None
    content_ok: bool | None = None
    reason: str | None = None

    def get_log_row(self):
        values = self.dict(exclude={"website", "check_time"}).values()
        return (
            f"{self.check_time} {self.website.url} "
            + " ".join(str(val) for val in values)
            + "\n"
        )
