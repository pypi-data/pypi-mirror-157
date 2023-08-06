from dataclasses import dataclass
from datetime import date
from typing import Match, NamedTuple, Optional, Union

from citation_report import Report

DOCKET_DATE_FORMAT = "%b. %d, %Y"


@dataclass
class Docket:
    """This abstract class is instantiated later in the process, specifically after a docket `Style` is constructed."""

    match: Match
    short_category: Optional[str] = None
    category: Optional[str] = None
    context: Optional[str] = None
    ids: Optional[str] = None
    cleaned_ids: Optional[str] = None
    docket_date: Optional[date] = None

    def __post_init__(self):
        self.cleaned_ids = self.ids.strip("()[] .,;") if self.ids else None

    @property
    def formatted_date(self):
        return self.docket_date.strftime(DOCKET_DATE_FORMAT)

    def __str__(self) -> str:
        singleton = None
        if self.cleaned_ids and "," in self.cleaned_ids:
            singleton = self.cleaned_ids.split(",")[0]
        return f"{self.short_category} {singleton or self.cleaned_ids}, {self.formatted_date}"


@dataclass
class ModelGR(Docket, Report):
    ...


@dataclass
class ModelAM(Docket, Report):
    ...


@dataclass
class ModelAC(Docket, Report):
    ...


@dataclass
class ModelBM(Docket, Report):
    ...


CitationType = Union[ModelGR, ModelAM, ModelAC, ModelBM, Report]  # note Report


class DocketModelConstructor(NamedTuple):
    """Docket `dataclass` later populated from data like regex `group names`. Each enum `Style` will allow this constructor to be populated."""

    label: str  # e.g. "General Register", "Administrative Matter"
    short_category: str  # e.g. G.R., A.M.
    group_name: str  # e.g. "gr_phrase", "am_phrase"; see .regexes for details
    init_name: str  # e.g. "gr_mid", "am_init"; see .regexes for details
    docket_regex: str  # this is the docket's regex string is supplemented by date, "formerly", etc.
    key_regex: str  # used for culling `ids` of the docket
    num_regex: str  # "No." used for culling the `ids` of the docket
    model: CitationType  # dataclass model to make, see `CitationType` options
