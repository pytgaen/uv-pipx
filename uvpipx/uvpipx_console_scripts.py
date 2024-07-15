#!/usr/bin/env python3

from __future__ import annotations

__author__ = "Gaëtan Montury"
__copyright__ = "Copyright (c) 2024-2024 Gaëtan Montury"
__license__ = """GNU GENERAL PUBLIC LICENSE refer to file LICENSE in repo"""
__version__ = "0.6.1"  # to bump
__maintainer__ = "Gaëtan Montury"
__email__ = "#"
__status__ = "Development"


import configparser
import json
import pathlib
import sys
from dataclasses import dataclass
from pprint import pprint
from typing import Dict, Union


@dataclass
class SitePackagesManager:
    site_packages_path: pathlib.Path

    @classmethod
    def from_sys_path(cls) -> SitePackagesManager:
        """
        Creates a new instance of the SitePackagesManager class from the system path.

        Returns:
            SitePackagesManager: A new instance of the SitePackagesManager class.
        """
        return cls(pathlib.Path(SitePackagesManager.get_site_packages_dir()))

    @staticmethod
    def get_site_packages_dir() -> str:
        """
        Returns the directory path for the site-packages.

        Returns:
            str: The path to the site-packages directory.
        """
        return next(p for p in sys.path if "site-packages" in p)

    def get_package_name(self, dist_info_dir: pathlib.Path) -> str:
        """
        Retrieves the package name from the METADATA file within a .dist-info directory.

        Args:
            dist_info_dir (pathlib.Path): The path to the .dist-info directory.

        Returns:
            str: The name of the package.
        """
        metadata_file = dist_info_dir / "METADATA"
        if metadata_file.exists():
            with metadata_file.open() as f:
                for line in f:
                    if line.startswith("Name:"):
                        return line.split(":", 1)[1].strip()
        return ""

    def find_console_scripts(self) -> Dict[str, Dict[str, str]]:
        """
        Returns a dictionary mapping package names to their console script names and corresponding commands.

        Returns:
            Dict[str, Dict[str, str]]: A dictionary where keys are package names and values are dictionaries
            mapping console script names to their corresponding commands.
        """
        scripts: Dict[str, Dict[str, str]] = {}

        for dist_info_dir in self.site_packages_path.glob("*.dist-info"):
            package_name = self.get_package_name(dist_info_dir)
            entry_points_file = dist_info_dir / "entry_points.txt"
            if entry_points_file.exists():
                config = configparser.ConfigParser()
                config.read(entry_points_file)
                if "console_scripts" in config.sections():
                    for name, value in config.items("console_scripts"):
                        scripts.setdefault(package_name, {})[name] = value

        return scripts

    def save_console_scripts_json(self, json_file: pathlib.Path) -> None:
        """
        Saves the console scripts dictionary to a JSON file in the site-packages directory.

        Args:
            scripts (Dict[str, str]): The dictionary of console scripts.
        """
        metadata = {"console_scripts": self.find_console_scripts()}
        with json_file.open("w") as outfile:
            json.dump(metadata, outfile, indent=4, default=str)


def main(json_file: Union[str, None]) -> None:
    manager = SitePackagesManager.from_sys_path()
    if json_file is None:
        pprint(manager.find_console_scripts())
    else:
        manager.save_console_scripts_json(pathlib.Path(json_file))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        main(None)
    else:
        main(sys.argv[1])
