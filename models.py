from pydantic import BaseModel
from typing import Optional

class Compensation(BaseModel):
    from_: Optional[int] = None
    to: Optional[int] = None
    currency: Optional[str] = None

class Vacancy(BaseModel):
    id: int
    name: str
    company: str
    area: str
    url: str
    compensation: Optional[Compensation] = None
    work_formats: list[str] = []
    experience: str = ""
    employment_form: str = ""

    @classmethod
    def from_raw(cls, raw: dict) -> "Vacancy":
        # compensation
        comp_raw = raw.get("compensation", {})
        comp = None
        if comp_raw and "noCompensation" not in comp_raw:
            comp = Compensation(
                from_=comp_raw.get("from"),
                to=comp_raw.get("to"),
                currency=comp_raw.get("currencyCode"),
            )

        # workFormats
        wf = raw.get("workFormats", [])
        formats = wf[0].get("workFormatsElement", []) if wf else []

        return cls(
            id=raw["vacancyId"],
            name=raw["name"],
            company=raw["company"]["visibleName"],
            area=raw["area"]["name"],
            url=raw["links"]["desktop"],
            compensation=comp,
            work_formats=formats,
            experience=raw.get("workExperience", ""),
            employment_form=raw.get("employmentForm", ""),
        )