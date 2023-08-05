import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="urb",
    version="1.2.2",
    description="a command line dictionary and wrapper for various dictionary APIs",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/addyett/urb",
    author="addyett",
    author_email="g.aditya2048@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["pyfiglet", "requests", "typer"],
    entry_points={
        "console_scripts": [
            "urb=urb.__main__:main",
        ]
    },
)
