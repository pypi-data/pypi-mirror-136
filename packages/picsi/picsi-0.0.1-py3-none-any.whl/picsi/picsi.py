#!/usr/bin/env python3

from pathlib import Path
from sys import argv
import tomli

dir_module = Path(__file__).parent.resolve()

with open(f"{dir_module}/config.toml", "rb") as conffile:
    conf = tomli.load(conffile)

if __name__ == "__main__":
    for arg in argv:
        if arg in ["help", "h", "--help"]:
            help.print()
            exit()

    # Command line flags
    for arg in argv:
        if arg in ["--apt-upgrade"]:
            conf["apt"]["upgrade"] = True
        elif arg in ["--no-source"]:
            conf["nexmon"]["enabled"] = False
        elif arg in ["--no-binaries"]:
            conf["binaries"]["enabled"] = False

    # Command line options
    for arg in argv:
        if arg in ["--url"]:
            conf["app"]["url"] = arg
        elif arg in ["--branch"]:
            conf["app"]["branch"] = arg
        elif arg in ["--nexmon-url"]:
            conf["nexmon"]["url"] = arg
        elif arg in ["--nexmon-branch"]:
            conf["nexmon"]["branch"] = arg
        elif arg in ["--binary-url"]:
            conf["binaries"]["url"] = arg
        elif arg in ["--binary-branch"]:
            conf["binaries"]["branch"] = arg

    # Command line.. commands?
    for arg in argv:
        if arg in ["i", "install"]:
            import commands.install

            exit(commands.install.install(argv, conf))

    print("No command supplied for picsi. See picsi help for usage.")
