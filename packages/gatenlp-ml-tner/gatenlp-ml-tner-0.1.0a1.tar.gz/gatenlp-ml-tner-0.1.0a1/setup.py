#!/usr/bin/env python
# encoding: utf-8
"""Packaging script for the gatenlp_ml_tner library."""
import sys
import os
import re
from setuptools import setup, find_packages

if sys.version_info < (3, 7):
    sys.exit("ERROR: gatenlp requires Python 3.7+")

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md")) as f:
    readme = f.read()


def versionfromfile(*filepath):
    infile = os.path.join(here, *filepath)
    with open(infile) as fp:
        version_match = re.search(
            r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", fp.read(), re.M
        )
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string in {}.".format(infile))


version = versionfromfile("gatenlp_ml_tner/version.py")


setup(
    name="gatenlp-ml-tner",
    version=version,
    author="Johann Petrak",
    author_email="johann.petrak@gmail.com",
    url="https://github.com/GateNLP/python-gatenlp-ml-tner",
    keywords=["nlp", "text processing", "natural language processing", "machinge learning"],
    description="Train and use transformer token classification models using tner",
    long_description=readme,
    long_description_content_type="text/markdown",
    setup_requires=[
        # deliberately not used, since it installs packages without pip,  use the "dev" extras instead
    ],
    install_requires=["iobes"],
    # extras_require=get_install_extras_require(),
    python_requires=">=3.7",
    # tests_require=["pytest", "pytest-cov"],
    platforms="any",
    license="Apache License 2.0",
    packages=find_packages(),
    # test_suite="tests",
    entry_points={"console_scripts": [
        "gatenlp-tner-train=gatenlp_ml_tner.train:run_training",
        "gatenlp-tner-eval=gatenlp_ml_tner.eval:run_eval",
        "gatenlp-tner-docs2dataset=gatenlp_ml_tner.export:run_docs2dataset",
    ]},
    classifiers=[
        # "Development Status :: 6 - Mature",
        # "Development Status :: 5 - Production/Stable",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
    ],
    project_urls={
        "Documentation": "https://gatenlp-ml-tner.readthedocs.io",
        "Source": "https://github.com/GateNLP/python-gatenlp-ml-tner",
    },
)
