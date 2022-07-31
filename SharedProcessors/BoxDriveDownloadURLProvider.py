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

from autopkglib import Processor, ProcessorError, URLGetter

__all__ = ["BoxDriveDownloadURLProvider"]


class BoxDriveDownloadURLProvider(URLGetter):
    """Provides download URL for specific box drive installer from update json"""

    description = "Provides download URL for Box Drive."
    input_variables = {
        "update_url": {
            "required": False,
            "description": "URL for Box json",
        },
        "os_type": {
            "required": True,
            "description": "os_type: mac, win, win32",
        },
        "release": {
            "required": True,
            "description": "Release to check for: alpha, beta, enterprise, free, eap",
        },
        "url_type": {
            "required": False,
            "description": "URL type to check for: rollout-url, download-url. Defaults to download-url",
        },
    }
    output_variables = {
        "url": {"description": "The url for the Box Drive download."},
        "version": {
            "description": "The version reported from the json for requested download."
        },
    }

    __doc__ = description

    def main(self):

        default_box_json_url = "https://cdn07.boxcdn.net/Autoupdate.json"
        os_type = self.env.get("os_type")
        release = self.env.get("release")
        update_url = self.env.get("update_url", default_box_json_url)
        url_type = self.env.get("url_type", "download-url")
        verbosity = self.env.get("verbose", 0)

        if verbosity > 1:
            self.output(
                "Checking json for: {0}, {1}, {2} from {3}".format(
                    os_type, release, url_type, update_url
                )
            )

        json_results = json.loads(self.download(update_url))

        try:
            box_download_url = json_results[os_type][release][url_type]
        except:
            self.output("Failed to get %s, checking for download-url" % url_type)
            box_download_url = json_results[os_type][release]["download-url"]

        self.output(box_download_url)
        try:
            # Get the version associated with the download type
            if "rollout" in url_type:
                box_version = json_results[os_type][release]["rollout-version"]
            else:
                box_version = json_results[os_type][release]["version"]
        except:
            box_version = json_results[os_type][release]["version"]

        self.env["url"] = box_download_url
        self.env["version"] = box_version


if __name__ == "__main__":
    processor = BoxDriveDownloadURLProvider()
    processor.execute_shell()
