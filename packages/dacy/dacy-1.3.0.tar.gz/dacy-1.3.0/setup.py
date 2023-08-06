import setuptools

with open("dacy/about.py") as f:
    v = f.read()
    for l in v.split("\n"):
        if l.startswith("__version__"):
            __version__ = l.split('"')[-2]

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().split("\n")

setuptools.setup(
    name="dacy",
    version=__version__,
    description="a Danish preprocessing pipeline trained in SpaCy. \
        At the time of writing it has achieved State-of-the-Art \
            performance on all Benchmark tasks for Danish",
    license="Apache License 2.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kenneth C. Enevoldsen",
    author_email="kennethcenevoldsen@gmail.com",
    url="https://github.com/KennethEnevoldsen/dacy",
    packages=setuptools.find_packages(),
    include_package_data=True,
    # external packages as dependencies
    install_requires=[
        "spacy-transformers>=1.0.1,<1.1.0",
        "spacy>=3.2.0,<3.3.0",
        "pandas >= 1.0.0,<2.0.0",
        "wasabi >= 0.8.2,< 0.9.0",
    ],
    extras_require={
        "large": [
            "protobuf>=3.17.3",
            "sentencepiece>=0.1.96",
        ],
        "all": [
            "protobuf>=3.17.3",
            "sentencepiece>=0.1.96",
        ],
    },
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="NLP danish",
)
