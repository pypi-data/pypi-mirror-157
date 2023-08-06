import re
from enum import Enum
from typing import Iterator, Match, Optional, Pattern

from citation_date import decode_date, docket_date
from citation_docket import (
    Num,
    ac_key,
    ac_phrases,
    am_key,
    am_phrases,
    bm_key,
    bm_phrases,
    cull_extra,
    formerly,
    gr_key,
    gr_phrases,
    l_key,
    pp,
)
from citation_report import REPORT_REGEX, get_publisher_label, get_reports

from .helpers import filter_out_docket_reports
from .predockets import (
    CitationType,
    DocketModelConstructor,
    ModelAC,
    ModelAM,
    ModelBM,
    ModelGR,
)


class Style(Enum):
    """
    1. Limited to Docket style members: "GR", "AM", "AC" and "BM"
    2. In order to reference the `value` attributes of member in properties, must use this format: `member.value.attribute`
    3. Each `enum` member has search / match / construct patterns based on `namedtuple` properties (includes a `dataclass` field.)
    4. Each of the members is used in a filtering function `get_docketed_reports()` to determine if a given text matches the member patterns.
    5. If a match is found, a `dataclass`, e.g. "ModelGR", is instantiated with fields supplied by `regex` group names.
    6. Each of the Docket style members may contain an optional `Report` regex pattern, see `pattern` property.

    """

    GR = DocketModelConstructor(
        label="General Register",
        short_category="GR",
        group_name="gr_phrase",
        init_name="gr_mid",
        docket_regex=gr_phrases,
        key_regex=rf"{gr_key}({l_key})?",
        num_regex=Num.GR.allowed,
        model=ModelGR,
    )

    AM = DocketModelConstructor(
        label="Administrative Matter",
        short_category="AM",
        group_name="am_phrase",
        init_name="am_init",
        docket_regex=am_phrases,
        key_regex=am_key,
        num_regex=Num.AM.allowed,
        model=ModelAM,
    )

    AC = DocketModelConstructor(
        label="Administrative Case",
        short_category="AC",
        group_name="ac_phrase",
        init_name="ac_init",
        docket_regex=ac_phrases,
        key_regex=ac_key,
        num_regex=Num.AC.allowed,
        model=ModelAC,
    )

    BM = DocketModelConstructor(
        label="Bar Matter",
        short_category="BM",
        group_name="bm_phrase",
        init_name="bm_init",
        docket_regex=bm_phrases,
        key_regex=bm_key,
        num_regex=Num.BM.allowed,
        model=ModelBM,
    )

    @property
    def pattern(self) -> Pattern:
        """Construct pattern from `docket_regex`"""
        docket = rf"{self.value.docket_regex}"
        dated = rf"(?P<extra_phrase>{formerly}?{pp}?){docket_date}"
        report = rf"(?P<opt_report>\,\s*{REPORT_REGEX})?"
        return re.compile("".join([docket, dated, report]), re.I | re.X)

    def find(self, text: str) -> Optional[Match]:
        """Get first match of member's `pattern` on `text`"""
        return self.pattern.search(text)

    def find_all(self, text: str) -> Iterator[Match]:
        """Get all matches of member's `pattern` on `text`"""
        return self.pattern.finditer(text)

    def cleaned(self, text) -> str:
        """Remove category name from `text`"""
        regex = rf"""{self.value.key_regex}({self.value.num_regex})?"""
        sans_category: Pattern = re.compile(regex, re.I | re.X)
        return sans_category.sub("", text)

    def get_report_date(self, match: Match) -> str:
        return decode_date(match.group("report_date"))

    def dockets_made(self, raw: str) -> Iterator[CitationType]:
        """If `self.pattern` matches `raw` text, create a `CitationType` (with possible Report)"""
        for match in self.find_all(raw):
            if match.group(self.value.init_name):
                yield self.value.model(
                    match=match,
                    short_category=self.value.short_category,
                    category=self.value.label,
                    context=(x := match.group(self.value.group_name)),
                    ids=cull_extra(self.cleaned(x.strip(", "))),
                    docket_date=decode_date(match.group("docket_date"), True),
                    publisher=get_publisher_label(match),
                    volpubpage=match.group("volpubpage"),
                    volume=match.group("volume"),
                    page=match.group("page"),
                )


def get_dockets(raw: str) -> Iterator[CitationType]:
    """For each `Style`, create connected `CitationType`s if possible, e.g. `Style.GR` enables the `ModelGR`.

    Args:
        raw_text (str): The text to search for `CitationType` patterns, see `ModelGR`, `ModelAM`, `ModelAC`, `ModelBM`

    Yields:
        Iterator[CitationType]: `Docket` models, i.e. `Style.GR.model`,  which may contain an associated `Report`.
    """
    for styled in Style:
        yield from styled.dockets_made(raw)


def get_first_docket_model(raw: str) -> Optional[CitationType]:
    """Get the first `CitationType` found in the text, if any exist."""
    try:
        return next(get_dockets(raw))
    except:
        ...
    return None


def parse_citations(raw: str) -> list[CitationType]:
    """Based on `get_docketed_reports()`, combine `Docket`s (which have `Reports`), and filtered `Report` models, if they exist."""
    if dockets := list(get_dockets(raw)):  # each docket may have a report
        if reports := list(get_reports(raw)):  # duplicate reports now possible
            if undocketed := filter_out_docket_reports(raw, dockets, reports):
                return dockets + list(undocketed)  # ensures unique reports
            return dockets + reports
        return dockets
    else:
        if reports := list(get_reports(raw)):
            return reports
    return []


def get_first_citation_string(raw: str) -> Optional[str]:
    """Each `CitationType` is a dataclass with a `match` field that is of type `Match`, get full string matched with `.group(0)`"""
    return c[0].match.group(0) if (c := parse_citations(raw)) else None


def slice_until_end_of_first_citation(raw: str) -> Optional[str]:
    """Slice text until end of citation string found."""
    if target := get_first_citation_string(raw):
        if idx := raw.find(target):
            return raw[: idx + len(target)]
    return None
