from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from uvpipx import uvpipx_venv_factory
# from uvpipx.uvpipx_expose import ExposeApps
from uvpipx.UvPipxModels import (
    UvPipxExposedModel,
    UvPipxExposeInstallSets,
    UvPipxModel,
    UvPipxPackageModel,
    UvPipxVenvExposeAppModel,
)

# def read_config(    package_name: str, venv_name: Union[str, None] = None
# ) -> UvPipxModel:
#     venv_name_ = venv_name or package_name
#     pck_venv = config.uvpipx_venvs / venv_name_

#     if not (pck_venv / ".venv").exists():
#         msg = "{pck_venv} not exist or ready"
#         raise RuntimeError(msg)

#     with (pck_venv / "uvpipx.json").open() as outfile:
#         uvpipx_dict = json.load(
#             outfile,
#         )

#     return uvpipx_dict


def check_and_upgrade(config: Dict[str, Any]):  # noqa: ANN201
    vers = config.get("config_version")

    if vers == "0.2.0":
        return config, False

    if vers is None:
        return asdict(transform_old_to_0_2_0(config)), True

    return None, False


def transform_old_to_0_2_0(old_config: dict) -> UvPipxPackageModel:
    vers = old_config.get("version")

    if vers is None:
        venv_model, venv = uvpipx_venv_factory.uvpipx_venv_factory(
            old_config["package_name"], old_config["venv_name"],
        )

        install_sets = [
            UvPipxExposeInstallSets(
                [old_config["package_name"]], old_config["bin_names"],
            ),
        ]

        # expo_app = ExposeApps(venv)

        exposed_bins = {}
        for bin_pair in old_config["exposed_bins"]:
            venv_bin_split = bin_pair[0].rsplit("/", maxsplit=1)
            local_bin_split = bin_pair[1].rsplit("/", maxsplit=1)
            ren_bin = (
                local_bin_split[1] if local_bin_split[1] != venv_bin_split[1] else None
            )

            pl = uvpipx_venv_factory.path_link_factory(
                Path(bin_pair[0]),
                Path(local_bin_split[0]),
                rename_local_bin=ren_bin,
            )

            exposed_bins[venv_bin_split[1]] = UvPipxVenvExposeAppModel(
                venv_bin_split[1], pl.link_path, install_sets[0].package_name_sets,
            )

        injected_packages = {
            k: UvPipxPackageModel(
                package_name_spec=v,
                package_name=k,
            )
            for k, v in old_config.get("injected_package", {}).items()
        }

        install_sets.append(UvPipxExposeInstallSets(list(injected_packages.keys()), []))

        exposed = UvPipxExposedModel(
            venv.venv_path / ".venv/bin", install_sets, exposed_bins,
        )

        return UvPipxModel(
            venv=venv_model,
            main_package=UvPipxPackageModel(
                package_name_spec=old_config["package_name_ref"],
                package_name=old_config["package_name"],
            ),
            injected_packages=injected_packages,
            exposed=exposed,
        )

    return None


# TODO move to test

# no_vers_config = {
#     "package_name_ref": "jc",
#     "package_name": "jc",
#     "venv_name": None,
#     "bin_names": ["*"],
#     "uvpipx_package_path": "/home/gaetan/.local/uv-pipx/venvs/jc",
#     "exposed_bins": [
#         [
#             "/home/gaetan/.local/uv-pipx/venvs/jc/.venv/bin/jc",
#             "/home/gaetan/.local/bin/jc",
#         ]
#     ],
#     "injected_package": {"rich": "rich==12.0.0"},
# }

# new_vers = transform_old_to_0_2_0(no_vers_config)
# pass
