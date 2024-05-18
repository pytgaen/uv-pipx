from __future__ import annotations

from typing import List, Optional, Union

from uvpipx.internal_libs.misc import (
    log_error,
    log_info,
    log_warm,
)
from uvpipx.UvPipxEnv import ExposeBin, UvPipx


def relink_bins(
    package_name: str,
    *,
    expose_bin_names: Optional[List[str]] = None,
    venv_name: Union[None, str] = None,
) -> None:
    expose_bin_names_ = expose_bin_names or ["*"]

    uvp = UvPipx(
        package_name=package_name,
        venv_name=venv_name,
        # expose_bin_names=expose_bin_names_,
    )
    new_bins = uvp.dir_bins_to_expose(expose_bin_names_)

    exposed_bins_state: dict[str, list[ExposeBin]] = {
        "new": [],
        "exist_me": [],
        "exist_not_me": [],
        "not_exist": [],
        "del": [],
    }

    for new_bin in new_bins:
        if new_bin.link_exists():
            if new_bin.valid():
                exposed_bins_state["exist_me"].append(new_bin)
            else:
                exposed_bins_state["exist_not_me"].append(new_bin)
        else:
            if new_bin.exists():
                exposed_bins_state["new"].append(new_bin)
            else:
                exposed_bins_state["not_exist"].append(new_bin)

    new_bin_names = set(n.venv_bin_name for n in new_bins)
    for old_bin in uvp.saved_bin_exposed():
        if old_bin.venv_bin_name not in new_bin_names:
            exposed_bins_state["del"].append(old_bin)

    uvpipx_new_bins = apply_relink_bins(exposed_bins_state)
    uvp.uvpipx_dict["exposed_bins"] = sorted(uvpipx_new_bins)

    uvp.save(uvp.uvpipx_dict)


def apply_relink_bins(exposed_bins_state: dict[str, list[ExposeBin]]):  # -> list:
    uvpipx_new_bins = []
    for exposing in exposed_bins_state["new"]:
        log_info(
            f"  📁 Exposing program {exposing.venv_bin_path()} to {exposing.local_bin_path}"
        )
        exposing.link()
        uvpipx_new_bins.append((str(exposing.venv_bin_path()), exposing.local_bin_path))

    for exposing in exposed_bins_state["del"]:
        log_info(
            f"  🗑️  Remove exposed program {exposing.local_bin_path} -> {exposing.venv_bin_path()}"
        )
        exposing.unlink()

    for exposing in exposed_bins_state["exist_me"]:
        # log_info(f"Exposing program {exposing.venv_bin_name} to {exposing.local_bin_path}")
        uvpipx_new_bins.append((str(exposing.venv_bin_path()), exposing.local_bin_path))

    for exposing in exposed_bins_state["exist_not_me"]:
        log_warm(
            f"  🟡 Link {exposing.local_bin_path} already exist. Skipping {exposing.venv_bin_name}!"
        )

    for exposing in exposed_bins_state["not_exist"]:
        log_error(f"  🔴 {exposing.venv_bin_name} not exist. Cannot expose !")

    return uvpipx_new_bins
