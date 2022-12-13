Shared Processors
===============

## createISOProvider.py

Takes a source_path and creates an iso from it. Outputs 'iso_path' with absolute path. 

## SourceForgeURLProvider.py

Older provider to download releases from SourceForge projects. Not sure if it still works (10/2018).

## FossHubURLProvider.py

FossHub provides whitelisted IPs for organizations that want to cache downloads for redistribution internally. 

Basic use for the processor is to pass the app name, which can be found within the json here: https://university.fosshub.com/projects.json
You should pass the app_type to be sure you're getting the download requested. Check the json for the "type" you want, it has to match exactly in app_type. Sometimes the type has multiple options for platform or might have an additional space in the type. Create an override with these options of an existing recipe.
```
<dict>
    <key>Processor</key>
    <string>com.github.rustymyers.SharedProcessors/FossHubURLProvider</string>
    <key>Arguments</key>
    <dict>
        <key>app_name</key>
        <string>Audacity</string>
        <key>app_type</key>
        <string>macOS DMG for Apple silicon </string>
    </dict>
</dict>
```

Additional inputs are: 
* projects_url = override projects.json URL
* app_type = download specific release of project (defaults to "macOS DMG").

Current list of app_type options from projects.json. Use autopkg run -vvv with a recipe that calls the processor to list all current app\_types.

```
All PlugIns - 32-bit Windows Installer
64-bit Windows Portable
Windows portable (64-bit)
Small Installer (Java 1.7++ required)
Portable (WinPenPack Format)
macOS DMG - Full Version
32bit Linux binary
macOS Intel
Windows Installer
64-bit Windows Installer
Portable (PortableApps Format)
64-bit Portable
Source File - Linux
32-bit Windows Installer - ZIP
64-bit Windows ZIP
Source code
32-bit and 64-bit Portable
(Stable) Windows Installer
Portable version (Zip Archive) -
Windows portable (32-bit)
64-bit Windows installer
Windows Installer 64-bit
32/64 Bits Installer
Windows Installer - Russian
32-bit and 64-bit Installer
ISO file
ZIP
Windows Portable
Windows Installer - Simplified Chinese
Windows Installer (for 7,8,10)
Debugging symbols
Windows Portable (PAF)
developer build
OS X - Java 10 JRE
Windows installer (32-bit)
LADSPA plugins for Mac - ZIP
Cross-Platform
Windows Portable 7-Zip Archive
Tar.Gz Archive
macOS DMG
Bonus Content
64-bit Linux AppImage
(Experimental) Windows Installer
64-bit Linux Universal Binary
Mac OS X 2.1.1 - ZIP (screen reader accessible)
Windows Installer - Traditional Chinese
Windows (standalone, x64)
OS X Binary
DOS and Win9x
Android
Setup and portable
Windows Installer (Beta)
64-bit Windows Installer - no Java JRE
macOS
macOS-Zip
Windows portable
Preview, Installer (32-bit, 64-bit)
Linux, kernel 2.6.18 or later x86_64
WinPE plugin
Windows Installer and Portable
Source Code
Portable - PAF Format
64-bit Linux
Windows Installer - Italian
Installer for Debian (DoliDeb)
64-bit Image
Manual
32-bit and 64-bit - Windows Installer
Installer for Windows (DoliWamp)
Windows Installer - Spanish
Windows Portable - ZIP
Portable - Professional Edition
Windows Portable 64-bit
64-bit Linux portable tar
Windows Installer (for XP and Vista)
Mac OS X 2.1.1 - DMG (screen reader accessible)
Windows ZIP
32-bit and 64-bit Windows Installer
JAR File
Portable
Windows Installer - German
32-bit Linux App Image
Windows XP
OS X dmg
Windows installer
Zip (Java 1.7++ required)
64bit Linux binary
Installer
OS X - Wine.app included
Debian Linux
Windows Installer - French
KeePass Portable - Classic Edition
Windows Installer 32-bit
64-bit Windows Installer - Java 8 JRE
32-bit Portable
Linux ZIP
ERP-CRM (Zip)
for PC 32-bit Package (Legacy Only)
DOS
32-bit Linux
Portable version
Windows Portable - ZIP Archive
Windows Installer (without GTK)
zip
Mac OS X
RPM file
Linux AppImage
Beta
for PC 64-bit Package (EFI &amp; Legacy)
Windows Portable 32-bit
Main Content
KeePass Installer - Classic Edition
All PlugIns - 32-bit Windows ZIP
RemixOS-Player
64-bit Linux App Image
Calibre Portable
Installer - Professional Edition
 Windows Installer - No GCC or GDB debugger
macOS - DMG
OS X
32-bit Installer
Preview, Portable (32-bit, 64-bit)
Windows Installer (GCC and GDB debugger)
All PlugIns - 64-bit Windows ZIP
64-bit Windows Installer - Java 10 JRE
(NO administrator rights)
Windows Installer (with GTK)
Windows Installer - Full Version
Windows Installer (ZIP Archive)
Windows (standalone, x86)
Portable Server Edition (Headless)
Pixel C
Windows x64
All PlugIns - 64-bit Windows Installer
Linux and macOS
OS X 64-bit
32-bit Windows installer
Portable (All Platforms)
ERP-CRM (TGZ)
Legacy Windows package (pre-Windows 2000)
Fortran Setup
32-bit ZIP Archive (x86)
macOS PowerPC
Beta ZIP
32-bit and 64-bit Windows Portable
Preview, PortableApps.com
32-bit Windows Portable
Linux and Mac (Java 1.7++ required)
ZIP Archive
Ubuntu Linux
OS X 32-bit
Windows classic
Universal Linux (Fedora, Redhat, Mandriva, OpenSuse)
Windows Installer - Polish
PGP
Windows 64bit installer
PhotoShop plugin
Windows Installer - English
Linux, kernel 2.6.18 or later i386
LADSPA plugins for Windows - Installer
Windows
Linux App Image
Platform independent runnable JAR
32-bit Windows Installer
Windows Installer (Stable)
64-bit ZIP Archive (x64)
Full Installer
64-bit Installer
Linux Source (2.2.2)
Nexus 9
Windows installer (64-bit)
All Platforms
64-bit Windows Installer - ZIP
32-bit Windows ZIP
32-bit Windows portable
64-bit Windows portable
OS X (Zip)
Windows EXE
Linux
ZIP Archive - No Installer - Please read Important section below```

"We use FossHub to check for available software updates. We acknowledge that their update checker does not perform any tracking (cookies, advertising identifiers, and similar technologies) and they respect the EU General Data Protection Regulation (GDPR) guidelines."

References:

https://www.fosshub.com/privacy.html
https://eugdpr.org/
https://ec.europa.eu/info/law/law-topic/data-protection_en

For more information contact: admin@fosshub.com


## BoxDriveDownloadURLProvider.py

This provider returns the rollout-version of BoxDrive when an update is being published to clinets early. It returns the current version when there is no rollout-version availiable.
