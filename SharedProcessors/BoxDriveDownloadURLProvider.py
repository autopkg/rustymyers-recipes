#!/usr/bin/python
#
# Copyright 2018 The Pennsylvania State University.
#
# Updated by Rusty Myers (rzm102@psu.edu)
# Modified original by Matt Hansen (mah60@psu.edu).
# Based on WinInstallerExtractor


import os
import sys
import subprocess
import re
import json

from autopkglib import Processor, ProcessorError


__all__ = ["BoxDriveDownloadURLProvider"]


class BoxDriveDownloadURLProvider(Processor):
    '''Provides download URL for specific box drive installer from update json'''
    
    description = "Provides download URL for Box Drive."
    input_variables = {
        'update_url': {
            "required": False,
            "description": "URL for Box json",            
        },
        'os_type': {
            "required": True,
            "description": "os_type: mac, win, win32",
        },
        'release': {
            "required": True,
            "description": "Release to check for: alpha, beta, enterprise, free, eap",
        },
        'url_type': {
            "required": False,
            "description": "URL type to check for: rollout-url, download-url. Defaults to download-url",
        },
            "CURL_PATH": {
            "required": False,
            "default": "/usr/bin/curl",
            "description": "Path to curl binary. Defaults to /usr/bin/curl.",
        },
    }
    output_variables = {
        "url": {
            "description": "The url for the Box Drive download."
        },
        "version": {
                "description": "The version reported from the json for requested download."
        }
    }

    __doc__ = description

    def get_json(self,url):
		try:
			f = urllib2.urlopen(url)
			raw_json = f.read()
			f.close()
		except:
			raise ProcessorError('Could not retrieve URL: "%s"' % url)

		return json.loads(raw_json)
        
    def fetch_content(self, url, headers=None):
        """Returns content retrieved by curl, given a url and an optional
        dictionary of header-name/value mappings. Logic here borrowed from
        URLTextSearcher processor."""
        try:
            cmd = [self.env["CURL_PATH"], "--location", "--compressed"]
            if headers:
                for header, value in headers.items():
                    cmd.extend(["--header", "%s: %s" % (header, value)])
            cmd.append(url)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (data, stderr) = proc.communicate()
            if proc.returncode:
                raise ProcessorError("Could not retrieve URL %s: %s" % (url, stderr))
        except OSError:
            raise ProcessorError("Could not retrieve URL: %s" % url)

        return json.loads(data)

    def main(self):

        default_box_json_url="https://cdn07.boxcdn.net/Autoupdate.json"
        os_type = self.env.get('os_type')
        release = self.env.get('release')
        update_url = self.env.get('update_url', default_box_json_url)
        url_type = self.env.get('url_type', 'download-url')
        verbosity = self.env.get('verbose', 0)
        
        if verbosity > 1:
            self.output("Checking json for: {0}, {1}, {2} from {3}".format(os_type, release, url_type, update_url))
            
        json_results = self.fetch_content(update_url)

        try:
            box_download_url = json_results[os_type][release][url_type]
        except:
            self.output("Failed to get %s, checking for download-url" % url_type)
            box_download_url = json_results[os_type][release]['download-url']
        
        print box_download_url
        try:
            # Get the version associated with the download type
            if "rollout" in url_type:
                box_version = json_results[os_type][release]["rollout-version"]
            else:
                box_version = json_results[os_type][release]["version"]
        except:
            box_version = json_results[os_type][release]["version"]
            

        self.env['url'] = box_download_url
        self.env['version'] = box_version

if __name__ == '__main__':
    processor = BoxDriveDownloadURLProvider()
    processor.execute_shell()
