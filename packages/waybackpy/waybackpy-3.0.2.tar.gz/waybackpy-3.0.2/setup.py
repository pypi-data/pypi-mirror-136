import os.path
from setuptools import setup

readme_path = os.path.join(os.path.dirname(__file__), "README.md")
with open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

about = {}
version_path = os.path.join(os.path.dirname(__file__), "waybackpy", "__version__.py")
with open(version_path, encoding="utf-8") as f:
    exec(f.read(), about)

version = str(about["__version__"])

download_url = "https://github.com/akamhy/waybackpy/archive/{version}.tar.gz".format(
    version=version
)

setup(
    name=about["__title__"],
    packages=["waybackpy"],
    version=version,
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=about["__license__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    download_url=download_url,
    keywords=[
        "Archive Website",
        "Wayback Machine",
        "Internet Archive",
        "Wayback Machine CLI",
        "Wayback Machine Python",
        "Internet Archiving",
        "Availability API",
        "CDX API",
        "savepagenow",
    ],
    install_requires=["requests", "click"],
    python_requires=">=3.4",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    entry_points={"console_scripts": ["waybackpy = waybackpy.cli:main"]},
    project_urls={
        "Documentation": "https://github.com/akamhy/waybackpy/wiki",
        "Source": "https://github.com/akamhy/waybackpy",
        "Tracker": "https://github.com/akamhy/waybackpy/issues",
    },
)
