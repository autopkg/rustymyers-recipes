#!/usr/local/autopkg/python
#
# Copyright 2018 The Pennsylvania State University.
#
# Updated by Rusty Myers (rzm102@psu.edu)

from __future__ import absolute_import, print_function

import json

from autopkglib import Processor, ProcessorError, URLGetter

__all__ = ["FossHubURLProvider"]


class FossHubURLProvider(URLGetter):
    """Provides download URL for specific fosshub installer from projects json"""

    description = "Provides download URL for a given FossHub project."
    input_variables = {
        "projects_url": {
            "required": False,
            "description": "URL for FossHub projects json",
        },
        "app_name": {
            "required": True,
            "description": "Name of FossHub app",
        },
        "app_type": {
            "required": False,
            "description": "Type of installer prefered, defaults to dmg",
        },
    }
    output_variables = {
        "url": {"description": "The url for the Box Drive download."},
        "version": {
            "description": "The version reported from the json for requested download."
        },
        "file_sha1": {"description": "The sha1 of the file download found."},
        "file_sha256": {"description": "The sha256 of the file download found."},
    }

    __doc__ = description

    def get_json(self, url):
        hdr = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 "
                "(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
            )
        }
        raw_json = self.download(url, headers=hdr)

        return json.loads(raw_json)

    def unique_types(self, json_dict):
        file_types = []
        # Return list of unique file types
        for project in json_dict["projects"]:
            for projectfile in project["files"]:
                file_types.append(projectfile["type"])
        myset = set(file_types)
        for filetype in list(myset):
            print(filetype)

    def main(self):
        projects_url = self.env.get(
            "projects_url", "https://university.fosshub.com/projects.json"
        )
        app_name = self.env.get("app_name")
        app_type = self.env.get("app_type", "macOS DMG")
        verbosity = self.env.get("verbose", 0)

        if verbosity > 1:
            self.output(
                "Checking json for: '{0}' & '{1}' from {2}".format(
                    app_name, app_type, projects_url
                )
            )

        try:
            json_results = self.get_json(projects_url)
        except:
            raise

        if verbosity > 2:
            # Print unique file types
            self.unique_types(json_results)

        # Print last updated time of json
        last_update = json_results["lastUpdatedAt"]
        if verbosity > 1:
            self.output("Projects JSON last updated: {0}".format(last_update))

        # Check each project name to find app_name
        for project in json_results["projects"]:
            # If we find a project that matches
            if project["name"] == app_name:
                # print(project['name'])
                # print(project)
                # Check each file in the matched project
                for projectfile in project["files"]:
                    # print(projectfile)
                    # print(projectfile['name'])
                    # print(projectfile['downloadUrl'])
                    # print(projectfile['version'])
                    # print(projectfile['hashes'])
                    # print(projectfile['type'])
                    # If we match the app type in the project file
                    if projectfile["type"] == app_type:
                        # Return match if found
                        self.env["url"] = projectfile["downloadUrl"]
                        self.env["version"] = projectfile["version"]
                        self.env["file_sha1"] = projectfile["hashes"]["sha1"]
                        self.env["file_sha256"] = projectfile["hashes"]["sha256"]
                        continue


if __name__ == "__main__":
    processor = FossHubURLProvider()
    processor.execute_shell()
