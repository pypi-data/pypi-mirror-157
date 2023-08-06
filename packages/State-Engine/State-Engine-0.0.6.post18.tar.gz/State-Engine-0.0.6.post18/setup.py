from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="State-Engine",
    url="https://yuriylygin.gitlab.io/state-engine/",
    author="Yu.A.Lygin",
    author_email="yuriylygin@gmail.com",
    description="Finite State Machine",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=["tests", "samples"]),
    license="MIT",
    keywords=["STATE MACHINE", "MOORE MACHINE", "STATE", "MACHINE", "MOORE"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    setuptools_git_versioning={
        "template": "{tag}",
        "dev_template": "{tag}.post{ccount}",
        "dirty_template": "{tag}.post{ccount}",
        "starting_version": "0.0.1",
        "version_callback": None,
        "version_file": None,
        "count_commits_from_version_file": False,
    },
    setup_requires=["setuptools-git-versioning"],
    # zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=[],
    dependency_links=[],
    # Install these with 'pip install -e .[docs,dev]'
    extras_require={
        "docs": ["sphinx>=5.0.2", "pallets-sphinx-themes>=2.0.2", "rinohtype>=0.5.4", "sphinx_issues", "sphinx_toolbox"],
        "dev": ["pytest>=6.2.5", "pytest-order>=1.0.0", "coverage>=5.5", "black"],
    },
)
