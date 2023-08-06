from setuptools import find_packages, setup
import io, re

with io.open('__version__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

DESCRIPTION = 'Downloading movies and tv shows thorugh egybest'
LONG_DESCRIPTION = 'a cli tool that allows you to download movies and tv shows through egybest'
setup (
    name="egycli",
    version=version,
    author="Cytolytic (Aktham Mostafa)",
    author_email="cytolyticdev@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    keywords=["egybest", "python", "movies", "download"],
    packages=find_packages(),
    install_requires=[
        "rich",
        "requests",
        "beautifulsoup4",
        "Js2Py",
        "simple-term-menu"
    ],
    entry_points="""
    [console_scripts]
    egybest=egycli.__main__:main
    """
)