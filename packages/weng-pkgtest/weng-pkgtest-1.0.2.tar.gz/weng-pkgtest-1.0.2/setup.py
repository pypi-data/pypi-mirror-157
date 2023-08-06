import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

NAME = 'weng-pkgtest'
PACK_DIR_NAME = 'weng_pkgtest'
DESCRIPTION = 'a python package test project'
URL = 'https://github.com/MutiYouth'
EMAIL = 'murphe@qq.com'
AUTHOR = 'Cheetah'
REQUIRES_PYTHON = '>=3.6'
VERSION = '1.0.2'

CUR_ROOT = os.path.abspath(os.path.dirname(__file__))
with open(f"{CUR_ROOT}/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(CUR_ROOT, PACK_DIR_NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """
    Support setup.py upload.
    """
    # description = "Build and publish the python3 package."
    # user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds...")
            rmtree(os.path.join(CUR_ROOT, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel distribution...")
        os.system("{0} setup.py sdist bdist_wheel".format(sys.executable))

        # upload
        self.status("Uploading the package to PyPI via Twine...")
        os.system("twine upload dist/*")

        # self.status('Pushing git tags…')
        # os.system('git tag v{0}'.format(about['__version__']))
        # os.system('git push --tags')

        sys.exit()


setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    license="Apache",
    keywords="""
    weng 
    python test
    """,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[PACK_DIR_NAME],
    install_requires=[
        # "opencv-python",
        "numpy>=1.17.2<2.0.0"
    ],
    # packages=find_packages(exclude=["dist", "build" ,"*.egg-info", "*.iml" ,"docs", "*test*"]),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=[PACK_DIR_NAME],
    zip_safe=False,
    include_package_data=True,
    url=URL,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        # "Operating System :: Unix",
        # "Operating System :: Microsoft :: Windows",
        # "Operating System :: MacOS",
        "Operating System :: OS Independent",
    ],
    python_requires=REQUIRES_PYTHON,

    # Build and upload package: python3 setup.py upload
    cmdclass={"upload": UploadCommand},
)
