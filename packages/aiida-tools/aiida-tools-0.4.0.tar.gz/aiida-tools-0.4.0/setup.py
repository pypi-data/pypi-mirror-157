#!/usr/bin/env python

# © 2017-2019, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>


import re
from setuptools import setup

readme = """Helper tools for developing AiiDA plugins."""

# Get the version number
with open("./aiida_tools/__init__.py", encoding="utf-8") as f:
    match_expr = "__version__[^'\"]+(['\"])([^'\"]+)"
    version = re.search(match_expr, f.read()).group(2).strip()


setup(
    name="aiida-tools",
    version=version,
    url="https://aiida-tools.readthedocs.io",
    author="Dominik Gresch",
    author_email="mail@greschd.ch",
    description=readme,
    python_requires=">=3.7",
    install_requires=["aiida-core>=2.0.0<3.0.0", "pyyaml"],
    extras_require={"dev": ["sphinx", "sphinx-rtd-theme", "pre-commit"]},
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Development Status :: 3 - Alpha",
    ],
    license="Apache 2.0",
    packages=["aiida_tools"],
)
