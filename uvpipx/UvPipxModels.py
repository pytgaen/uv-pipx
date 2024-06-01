from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, TypeVar, Union

T = TypeVar("T")


@dataclass
class UvPipxVenvExposeAppModel:
    bin_app_name: str
    exposed_app_path: str
    packages_name_sets: List[str]

    def exposed_app(self) -> Path:
        return Path(self.exposed_app_path)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "UvPipxVenvExposeAppModel":
        return UvPipxVenvExposeAppModel(
            bin_app_name=data["bin_app_name"],
            exposed_app_path=data["exposed_app_path"],
            packages_name_sets=data["packages_name_sets"],
        )


@dataclass
class UvPipxExposeInstallSets:
    package_name_sets: List[str]
    exposed_apps_rules: List[str]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "UvPipxExposeInstallSets":
        return UvPipxExposeInstallSets(
            package_name_sets=data["package_name_sets"],
            exposed_apps_rules=data["exposed_apps_rules"],
        )


@dataclass
class UvPipxExposedModel:
    venv_bin_dir: str
    install_sets: List[UvPipxExposeInstallSets] = field(default_factory=list)
    apps: Dict[str, UvPipxVenvExposeAppModel] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "UvPipxExposedModel":
        return UvPipxExposedModel(
            venv_bin_dir=data["venv_bin_dir"],
            install_sets=[
                UvPipxExposeInstallSets.from_dict(item) for item in data["install_sets"]
            ],
            apps={
                k: UvPipxVenvExposeAppModel.from_dict(v)
                for k, v in data["apps"].items()
            },
        )


@dataclass
class UvPipxVenvModel:
    uvpipx_dir: str
    name_override: Union[None, str] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "UvPipxVenvModel":
        return UvPipxVenvModel(
            uvpipx_dir=data["uvpipx_dir"],
            name_override=data.get("name_override"),
        )

    def name(self) -> str:
        return self.name_override or self.uvpipx_path().name

    def uvpipx_path(self) -> Path:
        return Path(self.uvpipx_dir)


@dataclass
class UvPipxPackageModel:
    package_name_spec: str
    package_name: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "UvPipxPackageModel":
        return UvPipxPackageModel(
            package_name_spec=data["package_name_spec"],
            package_name=data["package_name"],
        )


@dataclass
class UvPipxModel:
    venv: UvPipxVenvModel
    main_package: UvPipxPackageModel
    injected_packages: Dict[str, UvPipxPackageModel]
    exposed: UvPipxExposedModel
    config_version: str = "0.2.0"

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "UvPipxModel":
        return UvPipxModel(
            venv=UvPipxVenvModel.from_dict(data["venv"]),
            main_package=UvPipxPackageModel.from_dict(data["main_package"]),
            injected_packages={
                k: UvPipxPackageModel.from_dict(v)
                for k, v in data["injected_packages"].items()
            },
            exposed=UvPipxExposedModel.from_dict(data["exposed"]),
            config_version=data.get("config_version", "0.2.0"),
        )

    def save_json(self, file_name: Union[str, Path]) -> None:
        with (self.venv.uvpipx_path() / file_name).open("w") as outfile:
            json.dump(to_dict(self), outfile, indent=4, default=str)


def to_dict(obj: T) -> Dict[str, Any]:
    """
    A helper function to recursively convert a dataclass instance to a dictionary.
    """
    return asdict(obj)
