#!/usr/bin/env python3
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
# ISO Creation Based on tijme/generate-iso-image.py:
# See: https://gist.github.com/tijme/35da600ffb5830b817d81635c46bfce0
# Basically copied line for line and adapted from Greg Neagle's Munki project.
# See: https://github.com/munki/munki/blob/master/code/client/munkilib/munkicommon.py#L1507

# Use with edu.psu.SharedProcessors/createISOProvider as processor name
import os
import glob
from autopkglib import ProcessorError
from autopkglib.DmgMounter import DmgMounter
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO
import pycdlib

__all__ = ["createISOProvider"]

class createISOProvider(DmgMounter):
    description = ("Creates an iso from source_path")
    input_variables = {
        "source_path": {
            "required": True,
            "description": ("Path to a file or folder. "
                            "Can point to a globbed path inside a .dmg which will "
                            "be mounted.")
        },
        "destination_path": {
            "required": False,
            "description": ("Destination Path for ISO. Should be a folder. ")
        },
        "overwrite": {
            "required": False,
            "description": ("Defaults to True. Boolean to overwrite ISO if it already exists . ")
        },
        "volume_name": {
            "required": False,
            "description": ("Defaults to first 8 of destination_path. Limited to 8 characters")
        }
    }
    output_variables = {
        "iso_path": {
            "description": "Path to created iso.",
        }
    }


    def copy_recursive(self, source_base_path, target_iso, sub_path=""):
        """
        Copy a directory tree from one location to an ISO. This differs from shutil.copytree() that it does not
        require the target destination to not exist. This will copy the contents of one directory in to another
        existing directory without complaining.
        It will create directories if needed, but notify they already existed.
        If will overwrite files if they exist, but notify that they already existed.

        :param source_base_path: Directory path
        :param target_iso: pycdlib iso object
        :return: None
        Source: https://www.devdungeon.com/content/walk-directory-python
        """
        print("copy_recursive({0}, {1}, {2})".format(source_base_path, target_iso, sub_path))
        if sub_path != "":
            orig_base_path = os.path.relpath(source_base_path, sub_path)
        else:
            orig_base_path = source_base_path
        for item in os.listdir(source_base_path):
            # Directory
            if os.path.isdir(os.path.join(source_base_path, item)):
                # Create destination directory if needed
                # Get a relative path to add to iso
                new_target_dir = sub_path + "/" + os.path.relpath(os.path.join(source_base_path, item), source_base_path)
                print("Adding new target dir: {0}".format(new_target_dir))
                try:
                    print("Add Directory: {0}".format(new_target_dir))
                    target_iso.add_directory(new_target_dir)
                except:
                    print("WARNING: Directory exists...")
                # Recurse the directory
                new_source_dir = os.path.join(source_base_path, item)
                print("New source dir: {0}".format(new_source_dir))
                # Pass the relative path as sub_path
                # print("Orig base path: {0}".format(orig_base_path))
                self.copy_recursive(new_source_dir, target_iso, sub_path=new_target_dir)
            # File
            else:
                # Copy file over
                source_name = os.path.join(source_base_path, item)
                print("Adding new target file: {0}".format(source_name))
                target_name = sub_path + "/" + os.path.relpath(os.path.join(source_base_path, item), source_base_path)
                print("Testing target name: {0}".format(target_name))
                targetfilehandle = open(source_name, 'rb')
                targetfilebody = targetfilehandle.read()
                targetfilehandle.close()
                # Write to ISO
                target_iso.add_fp(BytesIO(targetfilebody), len(targetfilebody), joliet_path=target_name)

    def createISO(self, source_path, destination_iso, volume_name, overwrite):
        """
        Creates ISO from source_path
        """

        if os.path.exists(destination_iso):
            self.output("Dest ISO exists")
            if os.path.isfile(destination_iso) and overwrite:
                self.output("Removing old iso")
                os.remove(destination_iso)
            else:
                raise ProcessorError(
                    f"Error destination_iso '{destination_iso}' is a folder!.")
        else:
            self.output("No old iso")

        iso = pycdlib.PyCdlib()
        if len(volume_name) > 0:
            VOLUME_NAME = volume_name
        else:
       	    VOLUME_NAME = os.path.basename(source_path)[:8]	
        self.output("VOLUME_NAME: {0}".format(VOLUME_NAME))
        iso.new(joliet=3, vol_ident=VOLUME_NAME, interchange_level=3)
        joliet = iso.get_joliet_facade()
        # Walk the directory to recreate it on iso
        self.copy_recursive(source_path, joliet)
        self.output("Writing ISO to:")
        self.output(destination_iso)
        iso.write(destination_iso)
        iso.close()

    def main(self):
        source_path = self.env["source_path"]
        RECIPE_CACHE_DIR = self.env.get("RECIPE_CACHE_DIR")
        version = self.env.get("version")
        extension = "iso"
        volume_label = self.env["volume_name"]
        # Set name from Source Path
        name = os.path.basename(source_path)
        self.output("name: {0}".format(name))
        # Default destination_path
        if len(volume_label) > 0:
            volume_name = volume_label
        else:
            volume_name = "{0}-{1}".format(name, version)
        destination_name = "{0}.{1}".format(volume_name, extension)
        destination_iso = "{0}/{1}".format(RECIPE_CACHE_DIR, destination_name)
        if self.env.get("destination_path"):
            destination_path = self.env.get("destination_path")
            self.output("Using provided destination_path value")
            destination_iso = "{0}{1}-{2}.{3}".format(destination_path, name, version, extension)
        # Default to overwrite
        overwrite = True
        # if self.env.get("overwrite"):
        #     overwrite = self.env.get("overwrite")
        # Check if we're trying to copy something inside a dmg.
        (dmg_path, dmg, dmg_source_path) = self.parsePathForDMG(source_path)
        self.output(
            f"Parsed dmg results: dmg_path: {dmg_path}, dmg: {dmg},\n"
            f"dmg_source_path: {dmg_source_path}",
            verbose_level=2,
        )
        (dmg_path, dmg, dmg_source_path) = self.env[
            'source_path'].partition(".dmg/")
        dmg_path += ".dmg"
        try:
            if dmg:
                # Mount dmg and copy path inside.
                mount_point = self.mount(dmg_path)
                source_path = os.path.join(mount_point, dmg_source_path)
            # process path with glob.glob
            matches = glob.glob(source_path, recursive=True)
            if len(matches) == 0:
                raise ProcessorError(
                    f"Error processing path '{source_path}' with glob."
                )
            matched_source_path = matches[0]
            if len(matches) > 1:
                self.output(
                    f"WARNING: Multiple paths match 'source_path' glob '{source_path}':"
                )
                for match in matches:
                    self.output(f"  - {match}")
            if [c for c in "*?[]!" if c in source_path]:
                self.output(
                    f"Using path '{matched_source_path}' matched from "
                    f"globbed '{source_path}'."
                )
            self.output(
                f"Using source path: '{source_path}'\n"
                f"ISO path:  '{destination_iso}'\n"
                f"Overwrite: '{overwrite}'"
            )
            # Create ISO and set path
            self.createISO(
                source_path,
                destination_iso,
                volume_name,
                overwrite)
            self.env["iso_path"] = destination_iso
        finally:
            if dmg:
                self.unmount(dmg_path)

if __name__ == '__main__':
    processor = createISOProvider()
    processor.execute_shell()