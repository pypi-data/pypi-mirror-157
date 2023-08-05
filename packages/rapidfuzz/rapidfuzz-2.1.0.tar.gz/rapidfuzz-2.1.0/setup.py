from skbuild import setup
import rapidfuzz_capi
import numpy as np

with open('README.md', 'rt', encoding="utf8") as f:
    readme = f.read()

setup(
    name="rapidfuzz",
    version="2.1.0",
    install_requires=["jarowinkler >= 1.0.3, < 1.1.0"],
    extras_require={'full': ['numpy']},
    url="https://github.com/maxbachmann/RapidFuzz",
    author="Max Bachmann",
    author_email="pypi@maxbachmann.de",
    description="rapid fuzzy string matching",
    long_description=readme,
    long_description_content_type="text/markdown",

    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License"
    ],

    packages=["rapidfuzz", "rapidfuzz/distance"],
    package_data={
        "rapidfuzz": ["*.pyi", "py.typed"],
        "rapidfuzz/distance": ["*.pyi"]
    },
    python_requires=">=3.6",

    cmake_args=[f'-DRF_CAPI_PATH:STRING={rapidfuzz_capi.get_include()}', f'-DNumPy_INCLUDE_DIR:STRING={np.get_include()}']
)
