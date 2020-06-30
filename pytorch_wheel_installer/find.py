import re
from typing import Any, Iterable, List, Optional, Text, Tuple, cast

from pip._internal.index.collector import LinkCollector
from pip._internal.index.package_finder import (
    CandidateEvaluator,
    CandidatePreferences,
    LinkEvaluator,
    PackageFinder,
)
from pip._internal.models.candidate import InstallationCandidate
from pip._internal.models.link import Link
from pip._internal.models.search_scope import SearchScope
from pip._internal.models.selection_prefs import SelectionPreferences
from pip._internal.models.target_python import TargetPython
from pip._internal.network.session import PipSession
from pip._internal.req.constructors import install_req_from_line
from pip._internal.req.req_install import InstallRequirement
from pip._internal.req.req_set import RequirementSet

from .computation_backend import ComputationBackend, detect_computation_backend
from .utils import get_public_or_private_attr

__all__ = ["find_links"]


def find_links(
    distributions: Iterable[str],
    computation_backend: Optional[ComputationBackend] = None,
) -> List[str]:
    reqs = get_requirements(distributions)
    finder = make_pytorch_packager_finder(computation_backend=computation_backend)
    return [finder.find_requirement(req, upgrade=True).url for req in reqs]


def get_requirements(args: Iterable[str]) -> List[InstallRequirement]:
    requirement_set = RequirementSet()
    for req in args:
        req_to_add = install_req_from_line(req, comes_from=None)
        req_to_add.is_direct = True
        requirement_set.add_requirement(req_to_add)
    return cast(List[InstallRequirement], requirement_set.all_requirements)


def make_pytorch_packager_finder(
    session: Optional[PipSession] = None,
    target_python: Optional[TargetPython] = None,
    computation_backend: Optional[ComputationBackend] = None,
) -> PackageFinder:
    if session is None:
        session = PipSession()
    if target_python is None:
        target_python = TargetPython()
    if computation_backend is None:
        computation_backend = detect_computation_backend()

    link_collector = make_pytorch_link_collector(session)
    selection_prefs = SelectionPreferences(allow_yanked=True)
    return PytorchPackageFinder.create(
        link_collector=link_collector,
        selection_prefs=selection_prefs,
        target_python=target_python,
        computation_backend=computation_backend,
    )


def make_pytorch_link_collector(
    session: PipSession, url: str = "https://download.pytorch.org/whl/torch_stable.html"
) -> LinkCollector:
    search_scope = SearchScope.create(find_links=[url], index_urls=[])
    return LinkCollector(session=session, search_scope=search_scope)


class PytorchLinkEvaluator(LinkEvaluator):
    HAS_LOCAL_PATTERN = re.compile(r"[+](cpu|cu\d+)$")
    EXTRACT_LOCAL_PATTERN = re.compile(r"^/whl/(?P<local>(cpu|cu\d+))")

    def evaluate_link(self, link: Link) -> Tuple[bool, Optional[Text]]:
        output = cast(Tuple[bool, Optional[Text]], super().evaluate_link(link))
        is_candidate, result = output
        if not is_candidate:
            return output

        result = cast(Text, result)
        has_local = self.HAS_LOCAL_PATTERN.search(result) is not None
        if has_local:
            return output

        local = self.extract_local_from_link(link)
        if local is None:
            return output

        return True, f"{result}+{local}"

    def extract_local_from_link(self, link: Link) -> Optional[str]:
        match = self.EXTRACT_LOCAL_PATTERN.match(link.path)
        if match is None:
            return None

        return match.group("local")

    @classmethod
    def from_link_evaluator(
        cls, link_evaluator: LinkEvaluator
    ) -> "PytorchLinkEvaluator":
        kwargs = {
            attr: get_public_or_private_attr(link_evaluator, attr)
            for attr in (
                "project_name",
                "canonical_name",
                "formats",
                "target_python",
                "allow_yanked",
                "ignore_requires_python",
            )
        }
        return cls(**kwargs)


class PytorchCandidatePreferences(CandidatePreferences):
    def __init__(
        self,
        *args: Any,
        computation_backend: Optional[ComputationBackend] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        if computation_backend is None:
            computation_backend = detect_computation_backend()
        self.computation_backend = computation_backend

    @classmethod
    def from_candidate_preferences(
        cls,
        candidate_preferences: CandidatePreferences,
        computation_backend: Optional[ComputationBackend] = None,
    ) -> "PytorchCandidatePreferences":
        kwargs = {
            attr: get_public_or_private_attr(candidate_preferences, attr)
            for attr in ("prefer_binary", "allow_all_prereleases",)
        }
        return cls(computation_backend=computation_backend, **kwargs)


class PytorchCandidateEvaluator(CandidateEvaluator):
    @classmethod
    def create(
        cls,
        *args: Any,
        computation_backend: Optional[ComputationBackend] = None,
        **kwargs: Any,
    ) -> "PytorchCandidateEvaluator":
        return cls(*args, computation_backend=computation_backend, **kwargs)

    def __init__(
        self,
        *args: Any,
        computation_backend: Optional[ComputationBackend] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._computation_backend = computation_backend

    @classmethod
    def from_candidate_evaluator(
        cls,
        candidate_evaluator: CandidateEvaluator,
        computation_backend: Optional[ComputationBackend] = None,
    ) -> "PytorchCandidateEvaluator":
        kwargs = {
            attr: get_public_or_private_attr(candidate_evaluator, attr)
            for attr in (
                "project_name",
                "supported_tags",
                "specifier",
                "prefer_binary",
                "allow_all_prereleases",
                "hashes",
            )
        }
        return cls(computation_backend=computation_backend, **kwargs)

    def get_applicable_candidates(
        self, candidates: List[InstallationCandidate]
    ) -> List[InstallationCandidate]:
        return [
            candidate
            for candidate in super().get_applicable_candidates(candidates)
            if candidate.version.local == self._computation_backend
        ]


class PytorchPackageFinder(PackageFinder):
    _candidate_prefs: PytorchCandidatePreferences

    @classmethod
    def create(
        cls,
        *args: Any,
        computation_backend: Optional[ComputationBackend] = None,
        **kwargs: Any,
    ) -> PackageFinder:
        package_finder = super().create(*args, **kwargs)

        candidate_prefs = PytorchCandidatePreferences.from_candidate_preferences(
            package_finder._candidate_prefs, computation_backend=computation_backend
        )
        package_finder._candidate_prefs = candidate_prefs

        return package_finder

    def make_candidate_evaluator(
        self, *args: Any, **kwargs: Any,
    ) -> PytorchCandidateEvaluator:
        candidate_evaluator = super().make_candidate_evaluator(*args, **kwargs)
        return PytorchCandidateEvaluator.from_candidate_evaluator(
            candidate_evaluator,
            computation_backend=self._candidate_prefs.computation_backend,
        )

    def make_link_evaluator(self, *args: Any, **kwargs: Any) -> PytorchLinkEvaluator:
        link_evaluator = super().make_link_evaluator(*args, **kwargs)
        return PytorchLinkEvaluator.from_link_evaluator(link_evaluator)
