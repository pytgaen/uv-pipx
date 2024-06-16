from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Union

RE_PIP_REQ = re.compile(
    r"""(?P<name>[A-Za-z0-9._-]+)\s*                   # Nom du projet
(\[(?P<extras>[A-Za-z0-9._,-]+)\])?\s*        # Extras optionnels, entourés de []
(?P<version_specifiers>[^;]+)?\s*              # Spécifications des versions
(;\s*(?P<environment_marker>.+))?              # Environnement optionnel, après ;
""",
    re.VERBOSE,
)


@dataclass
class Requirement:
    # PEP 508 - Dependency specification for Python Software Packages
    name: str
    extras: Union[None, List[str]] = None
    version_specifiers: Union[None, List[str]] = None
    environment_marker: Union[None, str] = None

    @staticmethod
    def _split_str(data: str) -> List[str]:
        return [element.strip() for element in data.split(",")] if data else []

    @classmethod
    def from_str(cls, line: str) -> "Requirement":  # noqa: ANN102
        match = RE_PIP_REQ.match(line)
        if not match:
            msg = f"Line {line} not match PIP_REQ"
            raise RuntimeError(msg)

        return cls(
            name=match.group("name"),
            extras=Requirement._split_str(match.group("extras")),
            version_specifiers=Requirement._split_str(
                match.group("version_specifiers"),
            ),
            environment_marker=match.group("environment_marker"),
        )

    def to_str(self) -> str:
        s = f"{self.name}"
        if self.extras:
            s += f"[{','.join(self.extras)}]"
        if self.version_specifiers:
            s += f" {','.join(self.version_specifiers)}"
        if self.environment_marker:
            s += f"; {self.environment_marker}"

        return s


# requirements = [
#     "SomeProject",
#     "SomeProject == 1.3",
#     "SomeProject >= 1.2, < 2.0",
#     "SomeProject [foo, bar]",
#     "SomeProject ~= 1.4.2",
#     "SomeProject == 5.4 ; python_version < '3.8'",
#     "SomeProject ; sys_platform == 'win32'",
#     'requests [security] >= 2.8.1, == 2.8.* ; python_version < "2.7"',
#     "SomeProject==1.3",
#     "SomeProject>= 1.2, < 2.0",
#     "SomeProject[foo, bar]",
#     "SomeProject~=1.4.2",
#     "SomeProject==5.4;python_version<'3.8'",
#     "SomeProject;sys_platform=='win32'",
#     'requests[security]>=2.8.1,==2.8.*;python_version<"2.7"',
# ]
