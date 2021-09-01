#!/usr/local/autopkg/python
#
# Copyright 2010 Per Olofsson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# Updated by rzm102 to work as an archiver 2021
"""See docstring for Archiver class"""

import os
import shutil
import subprocess
import tarfile
import zipfile
from typing import Dict, Type, Union

from autopkglib import Processor, ProcessorError, is_mac

__all__ = ["Archiver"]

EXTNS = {
    "zip": ["zip"],
    "tar_gzip": ["tar.gz", "tgz"],
    "tar_bzip2": ["tar.bz2", "tbz"],
    "tar": ["tar"],
    "gzip": ["gzip"],
}


ExtractorType = Union[Type[tarfile.TarFile], Type[zipfile.ZipFile]]
Extractor = Union[tarfile.TarFile, zipfile.ZipFile]

NATIVE_EXTRACTORS: Dict[str, ExtractorType] = {
    "tar_bzip2": tarfile.TarFile,
    "tar_gzip": tarfile.TarFile,
    "tar": tarfile.TarFile,
    "zip": zipfile.ZipFile,
    # gzip not supported for now -- 2020-07-22
}


def _default_use_python_native_extractor() -> bool:
    if is_mac():
        return False
    return True


class Archiver(Processor):
    """Archive decompressor for zip and common tar-compressed formats."""

    description = __doc__
    input_variables = {
        "archive_path": {
            "required": False,
            "description": "Path to the archive created. Defaults to contents of the "
            "'pathname' variable, for example as is set by "
            "URLDownloader.",
        },
        "destination_path": {
            "required": False,
            "description": (
                "Directory archive will use to be created "
                "if necessary. Defaults to RECIPE_CACHE_DIR/NAME.zip"
            ),
        },
        "purge_destination": {
            "required": False,
            "description": "Whether the contents of the destination directory "
            "will be removed before unpacking.",
        },
        "archive_format": {
            "required": False,
            "description": (
                "The archive format. Currently supported: 'zip', "
                "'tar_gzip', 'tar_bzip2', 'tar'. If omitted, the "
                "file extension is used to guess the format."
            ),
        },
        "USE_PYTHON_NATIVE_EXTRACTOR": {
            "required": False,
            "description": (
                "Controls whether or not Archiver extracts the archive with native "
                "Python code, or calls out to a platform specific utility. "
                "The default is determined on a platform specific basis. "
                "Currently, this means that on macOS platform utilities are used, "
                "and otherwise Python is used."
            ),
            "default": _default_use_python_native_extractor(),
        },
    }

    output_variables = {}

    def get_archive_format(self, destination_path):
        """Guess archive format based on filename extension"""
        for format_str, extns in list(EXTNS.items()):
            for extn in extns:
                if destination_path.endswith(extn):
                    return format_str
        # We found no known archive file extension if we got this far
        return None

    def _extract(self, format: str, archive_path: str, destination_path: str) -> None:
        if self.env["USE_PYTHON_NATIVE_EXTRACTOR"]:
            self._extract_native(format, archive_path, destination_path)
        else:
            self._extract_utility(format, archive_path, destination_path)

    # def _extract_native(
    #     self, format: str, archive_path: str, destination_path: str
    # ) -> None:
    #     archivefile_class: ExtractorType = NATIVE_EXTRACTORS[format]
    #     archive: Extractor = archivefile_class(archive_path, mode="r")
    #     try:
    #         archive.extractall(path=destination_path)
    #     except Exception as ex:
    #         raise ProcessorError(
    #             f"Unarchiving {archive_path} with <native extractor> failed: {ex}"
    #         )

    def _extract_utility(
        self, format: str, archive_path: str, destination_path: str
    ) -> None:
        """Extracts an archive using a platform specific utility."""
        if format == "zip":
            cmd = [
                "/usr/bin/ditto",
                "-c",
                "-k",
                "--noqtn",
                archive_path,
                destination_path
            ]
        elif format == "gzip":
            cmd = ["/usr/bin/ditto", "--noqtn", "-c", destination_path, archive_path]
        elif format.startswith("tar"):
            cmd = ["/usr/bin/tar", "-c", "-f", destination_path, "-C", archive_path]
            if format.endswith("gzip"):
                cmd.append("-z")
            elif format.endswith("bzip2"):
                cmd.append("-j")

        # Call command.
        self.output(cmd)
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            (_, stderr) = proc.communicate()
        except OSError as err:
            raise ProcessorError(
                f"{os.path.basename(cmd[0])} execution failed with error code "
                f"{err.errno}: {err.strerror}"
            )
        if proc.returncode != 0:
            raise ProcessorError(
                f"Archiving {archive_path} with {os.path.basename(cmd[0])} failed: "
                f"{stderr}"
            )

    def main(self):
        """Archive a file"""
        # handle some defaults for archive_path and destination_path
        archive_path = self.env.get("archive_path")
        # if not archive_path:
        #     raise ProcessorError(
        #         "Expected an 'archive_path' input variable but none is set!"
        #     )
        destination_path = self.env.get(
            "destination_path",
            os.path.join(self.env["RECIPE_CACHE_DIR"], self.env["NAME"]),
        )

        # Create the directory if needed.
        if os.path.exists(destination_path):
            # try:
            #     os.makedirs(destination_path)
            # except OSError as err:
            #     raise ProcessorError(f"Can't create {destination_path}: {err.strerror}")
            if self.env.get("purge_destination"):
                try:
                    if os.path.isfile(destination_path) and not os.path.islink(destination_path):
                        os.remove(destination_path)
                    else:
                        os.unlink(destination_path)
                except OSError as err:
                    raise ProcessorError(f"Can't remove {path}: {err.strerror}")

        fmt = self.env.get("archive_format")
        if fmt is None:
            fmt = self.get_archive_format(destination_path)
            if not fmt:
                raise ProcessorError(
                    "Can't guess archive format for filename "
                    f"{os.path.basename(archive_path)}"
                )
            self.output(
                f"Guessed archive format '{fmt}' from filename "
                f"{os.path.basename(archive_path)}"
            )
        elif fmt not in list(EXTNS.keys()):
            msg = ", ".join(list(EXTNS.keys()))
            raise ProcessorError(
                f"'{fmt}' is not valid for the 'archive_format' variable. "
                f"Must be one of {msg}."
            )

        self._extract(fmt, archive_path, destination_path)
        self.output(f"Archived {archive_path} to {destination_path}")


if __name__ == "__main__":
    PROCESSOR = Archiver()
    PROCESSOR.execute_shell()
