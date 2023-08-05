# Compute a version number from a git repo or archive

# This file is released into the public domain. Generated by:
# versiongit-2.1 (https://github.com/dls-controls/versiongit)
import re
import sys
from pathlib import Path
from subprocess import STDOUT, CalledProcessError, check_output

# These will be filled in if git archive is run or by setup.py cmdclasses
GIT_REFS = 'tag: 0.1.0'
GIT_SHA1 = '2bfd4a1'

# Git describe gives us sha1, last version-like tag, and commits since then
CMD = "git describe --tags --dirty --always --long --match=[0-9]*[-.][0-9]*"


def get_version_from_git(path=None):
    """Try to parse version from git describe, fallback to git archive tags."""
    tag, plus, suffix = "0.0", "untagged", ""
    if not GIT_SHA1.startswith("$"):
        # git archive or the cmdclasses below have filled in these strings
        sha1 = GIT_SHA1
        for ref_name in GIT_REFS.split(", "):
            if ref_name.startswith("tag: "):
                # git from 1.8.3 onwards labels archive tags "tag: TAGNAME"
                tag, plus = ref_name[5:], "0"
    else:
        if path is None:
            # If no path to git repo, choose the directory this file is in
            path = Path(__file__).absolute().parent
        # output is TAG-NUM-gHEX[-dirty] or HEX[-dirty]
        try:
            cmd_out = check_output(CMD.split(), stderr=STDOUT, cwd=path)
        except Exception as e:
            sys.stderr.write("%s: %s\n" % (type(e).__name__, str(e)))
            if isinstance(e, CalledProcessError):
                sys.stderr.write("-> %s" % e.output.decode())
            return "0.0+unknown", None, e
        else:
            out = cmd_out.decode().strip()
            if out.endswith("-dirty"):
                out = out[:-6]
                suffix = ".dirty"
            if "-" in out:
                # There is a tag, extract it and the other pieces
                match = re.search(r"^(.+)-(\d+)-g([0-9a-f]+)$", out)
                tag, plus, sha1 = match.groups()
            else:
                # No tag, just sha1
                sha1 = out
    # Replace dashes in tag for dots
    tag = tag.replace("-", ".")
    if plus != "0" or suffix:
        # Not on a tag, add additional info
        tag = f"{tag}+{plus}.g{sha1}{suffix}"
    return tag, sha1, None


__version__, git_sha1, git_error = get_version_from_git()


def get_cmdclass(build_py=None, sdist=None):
    """Create cmdclass dict to pass to setuptools.setup.

    Create cmdclass dict to pass to setuptools.setup which will write a
    _version_static.py file in our resultant sdist, wheel or egg.
    """
    if build_py is None:
        from setuptools.command.build_py import build_py
    if sdist is None:
        from setuptools.command.sdist import sdist

    def make_version_static(base_dir: str, pkg: str):
        vg = Path(base_dir) / pkg.split(".")[0] / "_version_git.py"
        if vg.is_file():
            lines = open(vg).readlines()
            with open(vg, "w") as f:
                for line in lines:
                    # Replace GIT_* with static versions
                    if line.startswith("GIT_SHA1 = "):
                        f.write("GIT_SHA1 = '%s'\n" % git_sha1)
                    elif line.startswith("GIT_REFS = "):
                        f.write("GIT_REFS = 'tag: %s'\n" % __version__)
                    else:
                        f.write(line)

    class BuildPy(build_py):
        def run(self):
            build_py.run(self)
            for pkg in self.packages:
                make_version_static(self.build_lib, pkg)

    class Sdist(sdist):
        def make_release_tree(self, base_dir, files):
            sdist.make_release_tree(self, base_dir, files)
            for pkg in self.distribution.packages:
                make_version_static(base_dir, pkg)

    return dict(build_py=BuildPy, sdist=Sdist)
