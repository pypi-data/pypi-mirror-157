import glob
import importlib.util
from sysconfig import get_paths

from numpy import get_include
from numpy.distutils.core import Extension, setup

# Import <package>._version_git.py without importing <package>
path = glob.glob(__file__.replace("setup.py", "src/*/_version_git.py"))[0]
spec = importlib.util.spec_from_file_location("_version_git", path)
assert spec and spec.loader
vg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vg)

ext_modules = [
    Extension(
        "numcertain.uncertain",
        [
            "src/numcertain/uncertain.c",
            "src/numcertain/uncertaindtype.c",
            "src/numcertain/npyuncertain.c",
        ],
        include_dirs=[get_paths()["include"], get_include()],
    ),
]

setup(cmdclass=vg.get_cmdclass(), version=vg.__version__, ext_modules=ext_modules)
