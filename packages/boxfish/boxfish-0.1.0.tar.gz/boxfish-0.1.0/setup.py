import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of README and VERSION
README = (HERE / "README.md").read_text()
VERSION = (HERE / "boxfish/VERSION").read_text()

# This call to setup() does all the work
setup(
    name="boxfish",
    version=VERSION,
    description="A lightweight tool for table extraction from HTML pages.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/peterkorteweg/boxfish/",
    author="Peter Korteweg",
    author_email="boxfish@peterkorteweg.com",
    license="MIT",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    keywords='beautifulsoup html pandas scraping tables',

    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    #package_dir={'': 'boxfish'},  # Required
    packages=find_packages(),  # Required

    package_data={'boxfish': ['VERSION']},

    python_requires='>=3.6',

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    # install_requires=['requests'],  # Optional
)
