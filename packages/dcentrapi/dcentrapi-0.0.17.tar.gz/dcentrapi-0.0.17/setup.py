from pathlib import Path

from setuptools import setup, find_packages

VERSION = '0.0.17'
DESCRIPTION = 'RPC aggregation'
# LONG_DESCRIPTION = 'rpc aggregation.'

this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

# Setting up
setup(
    name="dcentrapi",
    version=VERSION,
    author="Dcentralab (Niv Shitrit)",
    author_email="<niv@dcentralab.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    license='MIT',
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
