#!/usr/bin/python
#
# Antti Pettinen
# Copyright 2017 Tampere University of Technology
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
"""See docstring for MSTeamsURLProvider class"""
#import re
from __future__ import absolute_import

from autopkglib import Processor, ProcessorError

try:
    from urllib.parse import urlopen  # For Python 3
except ImportError:
    from urllib2 import urlopen  # For Python 2

__all__ = ["MSTeamsURLProvider"]

BASE_URL = "https://teams.microsoft.com/downloads/DesktopURL?"
TEAMS_ENVIRONMENT = "production"
TEAMS_PLATFORM = "osx"
TEAMS_ARCH = ""

class MSTeamsURLProvider(Processor):
    """Provides a download URL for the latest MS Teams release. Supports both macOS and Windows clients, with the latter requiring the architecture to be defined"""
    description = __doc__
    input_variables = {
        "base_url": {
            "required": False,
            "description": ("Default is %s" % BASE_URL),
        },
        "environment": {
            "required": False,
            "description": ("Default is %s" % TEAMS_ENVIRONMENT),
        },
        "platform": {
            "required": False,
            "description": ("Default is %s" % TEAMS_PLATFORM),
        },
        "architecture": {
            "required": False,
            "description": ("Default is empty string, as MS Teams for macOS does not provide different architectures."),
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the desired MSTeams release.",
        },
    }

    def get_msteams_pkg_url(self, fetch_url):
        """Finds a download URL for latest MSTeams release"""
        try:
            fref = urlopen(fetch_url)
            dl_url = fref.read()
            fref.close()
        except Exception as err:
            raise ProcessorError("Could not retrieve %s: %s" %(fetch_url, err))
        # if the URL is empty, raise error
        if not dl_url:
            raise ProcessorError(
                "Could not find MSTeams download URL in %s" %fetch_url)
        return dl_url

    def main(self):
        """Find and return download URL for MSTeams"""
        base_url = self.env.get("base_url", BASE_URL)
        teams_env = self.env.get("environment", TEAMS_ENVIRONMENT)
        teams_plat = self.env.get("platform", TEAMS_PLATFORM)
        teams_arch = self.env.get("architecture", TEAMS_ARCH)

        fetch_url = "".join([base_url, "env=", teams_env, "&plat=", teams_plat])
        # Windows only:
        if teams_arch and teams_plat == "windows":
            fetch_url = "".join([fetch_url, "&arch=", teams_arch])

        self.env["url"] = self.get_msteams_pkg_url(fetch_url)
        self.output("MSTeams URL found: %s" % self.env["url"])

if __name__ == "__main__":
    PROCESSOR = MSTeamsURLProvider()
    PROCESSOR.execute_shell()
