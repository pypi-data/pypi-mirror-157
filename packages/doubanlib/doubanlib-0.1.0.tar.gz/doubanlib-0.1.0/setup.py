# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name="doubanlib",
    version="0.1.0",
    description="An api tool for DouBan movie",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xhboke/douban",
    author="xhboke",
    author_email="2361903575@qq.com",
    classifiers=[ 
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="douban,movie",
    package_dir={"": "src"}, 
    packages=find_packages(where="src"),
    python_requires=">=3.7, <4",
    install_requires=["requests"],

    project_urls={
        "Bug Reports": "https://github.com/xhboke/douban/issues",
    },
)
