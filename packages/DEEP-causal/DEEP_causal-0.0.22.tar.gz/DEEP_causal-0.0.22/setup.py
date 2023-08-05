from setuptools import setup

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="DEEP_causal",
    version="0.0.22",
    author="S.Zhang",
    author_email="shisheng.zhang@mymail.unisa.edu.au",
    url="https://pypi.org/project/DEEP-causal/",
    description=u"DEEP_causal",
    packages=["DEEP_causal"],
    install_requires=["gsq==0.1.6", "pandas==1.3.4", "numpy==1.21.4"],
    entry_points={"console_scripts": ["compute_dc=DEEP_causal:compute_dc"]},
    long_description=long_description,
    long_description_content_type="text/markdown",
)
