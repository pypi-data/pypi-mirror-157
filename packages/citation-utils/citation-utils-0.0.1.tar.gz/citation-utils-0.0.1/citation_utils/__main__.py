from dataclasses import asdict, dataclass, field
from optparse import Option
from typing import Iterator, Optional

from citation_report import Publisher, Report

from .constructors import CitationType, parse_citations
from .predockets import Docket


@dataclass
class RawCitation:
    """A `model` is created through `parse_citations()` as utilized in `CitationDocument`. This model contains data that can be assigned to fields."""

    model: CitationType
    docket: Optional[str] = None
    scra: Optional[str] = None
    phil: Optional[str] = None
    offg: Optional[str] = None

    def __post_init__(self):
        try:  # if Report model only, no ids will exist
            if isinstance(self.model, Docket) and self.model.ids:
                self.docket = self.model.__str__()
        except:
            ...

        # applies whether or not Report model or Docket model
        if self.model.publisher == Publisher.Phil.label:
            self.phil = f"{self.model.volume} Phil. {self.model.page}"

        elif self.model.publisher == Publisher.Scra.label:
            self.scra = f"{self.model.volume} SCRA {self.model.page}"

        elif self.model.publisher == Publisher.Offg.label:
            self.offg = f"{self.model.volume} O.G. {self.model.page}"

    @property
    def docket_data(self) -> Optional[dict]:
        if self.docket:
            return {
                "category": self.model.short_category,
                "serial": self.model.cleaned_ids,
                "docket_date": self.model.docket_date,
            }
        return None

    @property
    def canonical(self) -> Optional[str]:
        return self.docket or self.scra or self.phil or self.offg


@dataclass
class CitationDocument:
    """Given `text`, generate a list of `citations`."""

    text: str
    citations: list[RawCitation] = field(default_factory=list)

    def __post_init__(self):
        self.citations = [
            RawCitation(citation_type)
            for citation_type in parse_citations(self.text)
        ]

    @property
    def iter_dicts(self) -> Iterator[dict]:
        """Get citations as dict in given `text`"""
        if self.citations:
            for citation in self.citations:
                yield asdict(citation)

    @property
    def first(self) -> Optional[RawCitation]:
        """Get first citation from `text`"""
        return self.citations[0] if self.citations else None

    @property
    def first_dict(self) -> Optional[dict]:
        """Get first citation as dict in `text`"""
        return asdict(self.first) if self.first else None

    @property
    def first_canonical(self) -> Optional[str]:
        """Get first citation in canonical format from `text`"""
        return self.first.canonical if self.first else None
