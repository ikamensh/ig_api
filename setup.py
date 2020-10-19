from pathlib import Path

from setuptools import setup, find_packages

_DIR = Path(__file__).parent

version = "0.8"


def get_requirements():
    with (_DIR / "requirements.txt").open() as f:
        return f.read()


setup(
    name="ig_api",
    packages=find_packages("src"),
    package_dir={"": "src"},
    version=version,
    description="API for using ig.com trading; also a set of tools for local simulation.",
    author="Ilya Kamenshchikov",
    keywords=["trading", "api"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    license="MIT",
    long_description=(_DIR / "README.md").read_text().strip(),
    long_description_content_type="text/markdown",
    install_requires=get_requirements(),
    python_requires=">=3.6",
    url="https://github.com/ikamensh/ig_api",
    include_package_data=True,
)
