import os
from setuptools import setup, find_packages
from importlib.machinery import SourceFileLoader


module = SourceFileLoader(
    "version", os.path.join("wfs_trx", "version.py")
).load_module()


setup(
    name="wfs-trx",
    version=module.__version__,
    author=module.__author__,
    author_email=module.team_email,
    license=module.package_license,
    description=module.package_info,
    long_description=open("README.md").read(),
    platforms="all",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    packages=find_packages(exclude=["tests"]),
    package_data={"wfs_trx": ["py.typed"]},
    install_requires=[],
    python_requires=">=3.5, <4",
    extras_require={
        "develop": [
            "coverage!=4.3",
            "coveralls",
            "pylava",
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "tox>=2.4",
        ],
    },
    project_urls={
        "Documentation": "https://wfs-trx.readthedocs.org/",
        "Source": "https://github.com/itsmehdi97/wfs-trx",
    },
)
