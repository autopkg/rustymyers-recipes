#!/usr/local/autopkg/python
#
# Copyright 2018 The Pennsylvania State University.
#
# Updated by Rusty Myers (rzm102@psu.edu)
# Modified original by Matt Hansen (mah60@psu.edu).
# Based on WinInstallerExtractor


from __future__ import absolute_import

import json
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["readTextFile"]


class readTextFile(Processor):
    """Returns the text from a file"""

    description = "Returns text from provided file."
    input_variables = {
        "file_path": {
            "required": True,
            "description": "Path to file",
        },
    }
    output_variables = {
        "text": {"description": "The text from the file_path."},
    }

    __doc__ = description

    def main(self):
        file_path = self.env.get("file_path")
        verbosity = self.env.get("verbose", 0)
        text_output = ""

        if verbosity > 1:
            self.output("Checking file_path for text: {0}".format(file_path))
        try:
            with open(file_path) as f:
                text_output = f.readlines()
        except:
            raise ProcessorError("Failed to get text from: %s" % file_path)
        self.env["text"] = text_output


if __name__ == "__main__":
    processor = readTextFile()
    processor.execute_shell()
